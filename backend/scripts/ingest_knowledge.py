"""
Quantum Studio v5.1 - Knowledge_Repo 数据入库脚本
==================================================

Usage:
    cd backend
    # 处理单个文件夹
    python -m scripts.ingest_knowledge --folder "DeFi进展与分析" --limit 10
    
    # 处理所有文件夹
    python -m scripts.ingest_knowledge --all --limit 5
"""

import os
import sys
import json
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
except ImportError:
    print("Missing rich. Run: pip install rich")
    sys.exit(1)


console = Console()

# ==========================================
# 配置区
# ==========================================
WEB3_DATA_DIR = Path(__file__).parent.parent / "data" / "Web3素材"
CONCURRENCY_LIMIT = 3  # 并发上传数量
ENABLE_LLM_SCORING = True  # 是否启用 LLM 评分

# 需要清洗的前缀模式
CLEAN_PREFIXES = [
    r'^作者[：:].+?[\n\r]',
    r'^撰文[：:].+?[\n\r]',
    r'^整理[：:].+?[\n\r]',
    r'^编译[：:].+?[\n\r]',
    r'^翻译[：:].+?[\n\r]',
    r'^原文来源[：:].+?[\n\r]',
    r'^原文作者[：:].+?[\n\r]',
    r'^来源[：:].+?[\n\r]',
    r'^文章来源[：:].+?[\n\r]',
    r'^本文.*?不构成投资建议.*?[。\n]',
    r'^PANews.*?[\n\r]',
    r'^链捕手.*?[\n\r]',
    r'^Odaily.*?[\n\r]',
    r'^BlockBeats.*?[\n\r]',
    r'^律动.*?[\n\r]',
    r'^深潮.*?[\n\r]',
    r'^金色财经.*?[\n\r]',
    r'^Foresight News.*?[\n\r]',
]

# 中文内容类型映射
FACT_TYPE_LABELS = {
    "data": "硬数据",
    "analysis": "深度分析", 
    "opinion": "观点评论",
    "meme": "梗_黑话",
    "news": "快讯资讯",
}

# ==========================================
# 工具函数
# ==========================================
import re

def compute_hash(content: str) -> str:
    """计算内容的 MD5 哈希"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def clean_content(content: str) -> str:
    """清洗内容：去除作者、来源等前缀"""
    cleaned = content
    
    for pattern in CLEAN_PREFIXES:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    
    # 去除开头的多余空行
    cleaned = cleaned.lstrip('\n\r ')
    
    # 去除 Markdown 格式的作者信息（如 **作者：** xxx）
    cleaned = re.sub(r'\*\*作者[：:]\*\*.*?[\n\r]', '', cleaned)
    cleaned = re.sub(r'\*\*来源[：:]\*\*.*?[\n\r]', '', cleaned)
    
    return cleaned.strip()

async def score_content_async(content: str, topic: str) -> float:
    """使用 LLM 对内容进行质量评分 (1-10)"""
    if not ENABLE_LLM_SCORING:
        return 5.0  # 默认中等分数
    
    try:
        from app.core.llm import generate_text
        
        prompt = f"""请对以下 Web3 行业内容进行质量评分（1-10分）。

评分标准：
- 信息密度：是否包含具体数据、项目名称、技术细节（权重 30%）
- 时效性：是否讨论最新事件或趋势（权重 20%）
- 专业性：是否有深度分析或独特见解（权重 30%）
- 可读性：语言是否清晰流畅（权重 20%）

内容分类：{topic}

---
{content[:1500]}
---

请只返回一个数字（1-10），不要有其他文字。"""
        
        result = await asyncio.to_thread(
            lambda: generate_text(
                prompt=prompt,
                provider="volcengine",
                temperature=0.1,
                max_tokens=10
            )
        )
        
        # 提取数字
        score_match = re.search(r'(\d+(?:\.\d+)?)', result)
        if score_match:
            score = float(score_match.group(1))
            return min(max(score, 1.0), 10.0)  # 限制在 1-10 范围
        
        return 5.0
    except Exception as e:
        console.print(f"[yellow]⚠️ 评分失败: {e}[/yellow]")
        return 5.0

async def extract_entities_keywords(content: str, title: str) -> dict:
    """使用 LLM 提取核心实体和关键词"""
    try:
        from app.core.llm import generate_text
        
        prompt = f"""分析以下 Web3 内容，提取核心信息。

标题: {title}
内容: {content[:2000]}

请提取：
1. 核心实体（项目名、人名、代币名、公司名，最多 5 个，如 Uniswap, Vitalik, $ETH, a16z）
2. 关键词（主题关键词，最多 5 个，如 DEX, 流动性挖矿, 治理, 黑客攻击）

严格按以下 JSON 格式返回，不要有其他文字：
{{"entities": ["实体1", "实体2"], "keywords": ["关键词1", "关键词2"]}}"""
        
        result = await asyncio.to_thread(
            lambda: generate_text(
                prompt=prompt,
                provider="volcengine",
                temperature=0.1,
                max_tokens=200
            )
        )
        
        # 提取 JSON
        import json
        # 尝试找到 JSON 块
        json_match = re.search(r'\{[^{}]*\}', result.replace('\n', ''))
        if json_match:
            data = json.loads(json_match.group())
            return {
                "entities": data.get("entities", [])[:5],
                "keywords": data.get("keywords", [])[:5]
            }
        
        return {"entities": [], "keywords": []}
    except Exception as e:
        console.print(f"[yellow]⚠️ 实体提取失败: {e}[/yellow]")
        return {"entities": [], "keywords": []}

def parse_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    
    # 尝试多种格式
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y年%m月%d日",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    
    return None

def infer_fact_type(content: str) -> str:
    """根据内容推断 Fact Type（返回中文标签）"""
    
    # 黑话/梗关键词
    meme_keywords = ["WAGMI", "NGMI", "FOMO", "FUD", "Diamond Hands", "Rug Pull", "Degen", "HODL", "Ape in", "LFG", "DYOR", "NFA"]
    
    # 观点/评论关键词
    opinion_keywords = ["我认为", "观点", "展望", "预测", "未来", "趋势", "看法", "个人观点", "我觉得", "应该", "可能会"]
    
    # 快讯关键词
    news_keywords = ["宣布", "发布", "上线", "官方", "公告", "消息", "突发", "刚刚", "今日", "今天"]
    
    # 深度分析关键词
    analysis_keywords = ["分析", "研究", "报告", "深度", "解读", "解析", "详解", "机制", "原理", "技术"]
    
    content_lower = content.lower()
    
    # 检查黑话/梗
    for keyword in meme_keywords:
        if keyword.lower() in content_lower:
            return FACT_TYPE_LABELS["meme"]
    
    # 检查深度分析 (优先于观点)
    analysis_count = sum(1 for k in analysis_keywords if k in content)
    if analysis_count >= 2 or len(content) > 5000:
        return FACT_TYPE_LABELS["analysis"]
    
    # 检查观点评论
    for keyword in opinion_keywords:
        if keyword in content:
            return FACT_TYPE_LABELS["opinion"]
    
    # 检查快讯
    for keyword in news_keywords:
        if keyword in content[:500]:  # 只检查开头部分
            return FACT_TYPE_LABELS["news"]
    
    # 默认为硬数据
    return FACT_TYPE_LABELS["data"]

async def check_exists_async(content_hash: str, app_token: str, table_id: str) -> bool:
    """检查记录是否已存在（基于 内容指纹）"""
    try:
        filter_str = f'CurrentValue.[内容指纹] = "{content_hash}"'
        result = await asyncio.to_thread(
        )
        items = result.get("data", {}).get("items", [])
        return len(items) > 0
    except Exception as e:
        console.print(f"[yellow]⚠️ 查重失败: {e}[/yellow]")
        return False

async def upload_record_async(
    content: str,
    topic: str,
    publish_date: int,
    fact_type: str,
    source_file: str,
    content_hash: str,
    quality_score: float,
    title: str,
    source_url: str,
    entities: list,    # 新增：核心实体
    keywords: list,    # 新增：关键词
    app_token: str,
    table_id: str
) -> bool:
    """上传单条记录到 Knowledge_Repo - 最终字段配置 v4"""
    
    # 保留: 标题, 核心摘要, 正文原文, 赛道分类, 关键词, 项目/人名/代币, 事实类型, 质量评分, 发布日期, 内容指纹
    # 删除: 来源链接, 信息深度, 时效性, 状态, 来源文件
    
    fields = {
        "标题": title,
        "核心摘要": content[:500] if len(content) > 500 else content,
        "正文原文": content,
        "赛道分类": topic,
        "关键词": ", ".join(keywords) if keywords else "",
        "项目/人名/代币": ", ".join(entities) if entities else "",
        "事实类型": fact_type,
        "质量评分": quality_score,
        "内容指纹": content_hash,  # 用于查重
    }
    
    # 日期字段特殊处理
    if publish_date:
        fields["发布日期"] = publish_date

    
    try:
        result = await asyncio.to_thread(
        )
        if result.get("code") == 0:
            return True
        else:
            console.print(f"[red]❌ 上传失败: {result.get('msg')}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ 上传异常: {e}[/red]")
        return False

async def process_json_file(
    file_path: Path,
    topic: str,
    app_token: str,
    table_id: str,
    semaphore: asyncio.Semaphore
) -> tuple[bool, str]:
    """处理单个 JSON 文件"""
    async with semaphore:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            raw_content = data.get("content", "")
            if not raw_content or len(raw_content) < 50:
                return False, "内容过短"
            
            # 提取标题和链接 (新增)
            title = data.get("title", file_path.stem)  # 默认用文件名
            source_url = data.get("url", "")
            
            # 清洗内容
            content = clean_content(raw_content)
            if len(content) < 50:
                return False, "清洗后内容过短"
            
            # 计算哈希（基于清洗后的内容）
            content_hash = compute_hash(content)
            
            # 查重
            if await check_exists_async(content_hash, app_token, table_id):
                return False, "已存在"
            
            # 解析日期
            publish_date = parse_date(data.get("published_at", ""))
            
            # 推断类型
            fact_type = infer_fact_type(content)
            
            # LLM 评分
            quality_score = await score_content_async(content, topic)
            
            # LLM 提取核心实体和关键词
            extracted = await extract_entities_keywords(content, title)
            
            # 上传 (包含核心实体和关键词)
            success = await upload_record_async(
                content=content,
                topic=topic,
                publish_date=publish_date,
                fact_type=fact_type,
                source_file=file_path.name,
                content_hash=content_hash,
                quality_score=quality_score,
                title=title,
                source_url=source_url,
                entities=extracted["entities"],    # LLM 提取
                keywords=extracted["keywords"],    # LLM 提取
                app_token=app_token,
                table_id=table_id
            )
            
            if success:
                return True, "成功"
            else:
                return False, "上传失败"
                
        except json.JSONDecodeError:
            return False, "JSON解析错误"
        except Exception as e:
            return False, str(e)

async def process_folder(
    folder_name: str,
    app_token: str,
    table_id: str,
    limit: int = 0
) -> dict:
    """处理单个文件夹"""
    folder_path = WEB3_DATA_DIR / folder_name
    
    if not folder_path.exists():
        console.print(f"[red]❌ 文件夹不存在: {folder_path}[/red]")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    # 获取所有 JSON 文件
    json_files = list(folder_path.glob("*.json"))
    
    if limit > 0:
        json_files = json_files[:limit]
    
    console.print(f"\n[bold cyan]📂 处理文件夹: {folder_name}[/bold cyan]")
    console.print(f"   找到 {len(json_files)} 个 JSON 文件")
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    stats = {"success": 0, "failed": 0, "skipped": 0}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]入库中...", total=len(json_files))
        
        for file_path in json_files:
            success, msg = await process_json_file(
                file_path, folder_name, app_token, table_id, semaphore
            )
            
            if success:
                stats["success"] += 1
            elif msg == "已存在":
                stats["skipped"] += 1
            else:
                stats["failed"] += 1
            
            progress.update(task, advance=1)
    
    console.print(f"   ✅ 成功: {stats['success']} | ⚠️ 跳过: {stats['skipped']} | ❌ 失败: {stats['failed']}")
    return stats

async def main():
    parser = argparse.ArgumentParser(description="Knowledge_Repo 数据入库工具")
    parser.add_argument("--folder", type=str, help="指定处理的文件夹名称")
    parser.add_argument("--all", action="store_true", help="处理所有文件夹")
    parser.add_argument("--limit", type=int, default=0, help="每个文件夹最多处理的文件数 (0=不限制)")
    parser.add_argument("--dry-run", action="store_true", help="仅统计，不实际上传")
    
    args = parser.parse_args()
    
    # 获取配置
    
    if not app_token or not table_id:
        console.print("   请确保 .env 文件中包含这两个配置项")
        return
    
    console.print("=" * 60)
    console.print("[bold green]🚀 Quantum Studio v5.1 - Knowledge_Repo 数据入库[/bold green]")
    console.print("=" * 60)
    console.print(f"📋 Base Token: {app_token}")
    console.print(f"📋 Knowledge Table ID: {table_id}")
    
    if args.dry_run:
        console.print("[yellow]⚠️ Dry Run 模式：仅统计，不实际上传[/yellow]")
    
    # 确定要处理的文件夹
    folders_to_process = []
    
    if args.all:
        # 获取所有子文件夹
        folders_to_process = [f.name for f in WEB3_DATA_DIR.iterdir() if f.is_dir()]
        console.print(f"\n找到 {len(folders_to_process)} 个赛道文件夹")
    elif args.folder:
        folders_to_process = [args.folder]
    else:
        console.print("[yellow]⚠️ 请指定 --folder 或 --all 参数[/yellow]")
        return
    
    # 处理每个文件夹
    total_stats = {"success": 0, "failed": 0, "skipped": 0}
    
    for folder_name in folders_to_process:
        if args.dry_run:
            folder_path = WEB3_DATA_DIR / folder_name
            json_count = len(list(folder_path.glob("*.json")))
            console.print(f"  📂 {folder_name}: {json_count} 个 JSON 文件")
            total_stats["success"] += json_count
        else:
            stats = await process_folder(folder_name, app_token, table_id, args.limit)
            total_stats["success"] += stats["success"]
            total_stats["failed"] += stats["failed"]
            total_stats["skipped"] += stats["skipped"]
    
    # 汇总
    console.print("\n" + "=" * 60)
    console.print("[bold green]📊 入库完成![/bold green]")
    console.print("=" * 60)
    console.print(f"  ✅ 成功入库: {total_stats['success']}")
    console.print(f"  ⚠️ 重复跳过: {total_stats['skipped']}")
    console.print(f"  ❌ 失败: {total_stats['failed']}")

if __name__ == "__main__":
    asyncio.run(main())
