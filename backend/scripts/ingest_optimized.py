"""
Quantum Studio v5.2 - Knowledge_Repo 优化版入库脚本
==================================================
与 ingest_knowledge.py 的 A/B 测试版本。

优化点:
1. 合并 LLM 调用 (2次 -> 1次): 评分 + 实体/关键词同时返回

Usage:
    cd backend
    # 处理单个文件夹
    python -m scripts.ingest_optimized --folder "DeFi进展与分析" --limit 10
    
    # 处理所有文件夹
    python -m scripts.ingest_optimized --all --limit 5
"""

import os
import sys
import json
import asyncio
import hashlib
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
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

from scripts.batch.hash_cache import get_hash_cache, compute_content_hash

# Windows 编码兼容：禁用所有格式化，避免 GBK 编码错误
import io
import sys

# 强制 stdout 使用 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

console = Console(force_terminal=True, emoji=False, no_color=True, legacy_windows=True)

# ==========================================
# 配置区
# ==========================================
WEB3_DATA_DIR = Path(__file__).parent.parent / "data" / "Web3素材"
ENABLE_LLM = True  # 是否启用 LLM

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

def compute_hash(content: str) -> str:
    """计算内容的 MD5 哈希"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def clean_content(content: str) -> str:
    """清洗内容：去除作者、来源等前缀"""
    cleaned = content
    
    for pattern in CLEAN_PREFIXES:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    
    cleaned = cleaned.lstrip('\n\r ')
    cleaned = re.sub(r'\*\*作者[：:]\*\*.*?[\n\r]', '', cleaned)
    cleaned = re.sub(r'\*\*来源[：:]\*\*.*?[\n\r]', '', cleaned)
    
    return cleaned.strip()

def infer_fact_type(content: str) -> str:
    """根据内容推断事实类型"""
    if any(word in content[:500] for word in ['今日', '刚刚', '消息', '据悉', '宣布']):
        return FACT_TYPE_LABELS["news"]
    if any(word in content[:1000] for word in ['数据显示', '增长', '%', '美元', 'TVL', '市值']):
        return FACT_TYPE_LABELS["data"]
    if any(word in content[:1000] for word in ['分析', '深度', '研究', '报告', '解读']):
        return FACT_TYPE_LABELS["analysis"]
    if any(word in content[:500] for word in ['我认为', '观点', '评论', '看法']):
        return FACT_TYPE_LABELS["opinion"]
    return FACT_TYPE_LABELS["news"]

def parse_date(date_str: str) -> Optional[int]:
    if not date_str:
        return None
    
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


# ==========================================
# 合并版 LLM 调用 (核心优化)
# ==========================================

MERGED_PROMPT = """分析以下 Web3 内容，返回 JSON:

标题: {title}
赛道: {topic}
内容: {content}

返回格式 (严格 JSON，无其他文字):
{{
  "quality_score": 1-10,
  "summary": "一句话概括核心观点 (30字以内)",
  "entities": ["项目/人名/代币1", "项目/人名/代币2"],
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "fact_type": "硬数据/深度分析/观点评论/梗_黑话/快讯资讯"
}}

评分标准:
- 信息密度(30%): 具体数据、项目名称、技术细节
- 时效性(20%): 最新事件或趋势
- 专业性(30%): 深度分析或独特见解
- 可读性(20%): 语言清晰流畅"""


async def analyze_content_merged(content: str, title: str, topic: str) -> Dict[str, Any]:
    """
    合并版 LLM 调用：一次调用同时返回评分、实体、关键词和事实类型
    
    旧方案: 2 次调用 (score_content + extract_entities_keywords)
    新方案: 1 次调用 (analyze_content_merged)
    """
    default_result = {
        "quality_score": 5.0,
        "summary": content[:100] + "..." if len(content) > 100 else content,
        "entities": [],
        "keywords": [],
        "fact_type": infer_fact_type(content)
    }
    
    if not ENABLE_LLM:
        return default_result
    
    try:
        from app.core.llm import generate_text
        
        prompt = MERGED_PROMPT.format(
            title=title,
            topic=topic,
            content=content[:2000]
        )
        
        result = await asyncio.to_thread(
            lambda: generate_text(
                prompt=prompt,
                provider="volcengine",
                temperature=0.1,
                max_tokens=300
            )
        )
        
        # 提取 JSON
        json_match = re.search(r'\{[^{}]*\}', result.replace('\n', ''))
        if json_match:
            data = json.loads(json_match.group())
            return {
                "quality_score": min(max(float(data.get("quality_score", 5)), 1.0), 10.0),
                "summary": data.get("summary", default_result["summary"]),
                "entities": data.get("entities", [])[:5],
                "keywords": data.get("keywords", [])[:5],
                "fact_type": data.get("fact_type", default_result["fact_type"])
            }
        
        return default_result
    except Exception as e:
        console.print(f"[yellow]⚠️ LLM 分析失败: {e}[/yellow]")
        return default_result


# ==========================================
# 主处理逻辑 (并发优化版)
# ==========================================

# 并发控制：限制同时进行的 LLM 调用数量
LLM_CONCURRENCY = 5  # 降低到 5 个，减少网络压力和费用 (原为 10)


async def process_single_file(
    json_file: Path, 
    topic: str, 
    hash_cache,
    semaphore: asyncio.Semaphore
) -> Optional[Dict]:
    """处理单个文件，返回待上传的记录或 None"""
    async with semaphore:  # 控制并发数
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            title = data.get("title", "")
            content = data.get("content", "")
            publish_date = data.get("published_at", "")
            
            if not content or len(content) < 50:
                return {"status": "skipped", "data": None}
            
            # 清洗内容
            cleaned_content = clean_content(content)
            content_hash = compute_hash(cleaned_content)
            
            if hash_cache.contains(content_hash):
                return {"status": "skipped", "data": None}
            
            # 合并 LLM 调用 (1 次替代 2 次)
            analysis = await analyze_content_merged(cleaned_content, title, topic)
            
            # 上传时间戳
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 构建字段
            fields = {
                "上传时间": upload_time,  # 利用无法删除的主字段记录上传时间
                "标题": title,
                "核心摘要": analysis["summary"],  # LLM 生成的一句话摘要
                "正文原文": cleaned_content,
                "赛道分类": topic,
                "关键词": ", ".join(analysis["keywords"]) if analysis["keywords"] else "",
                "项目/人名/代币": ", ".join(analysis["entities"]) if analysis["entities"] else "",
                "事实类型": analysis["fact_type"],
                "质量评分": analysis["quality_score"],
                "内容指纹": content_hash,
            }
            
            # 日期字段特殊处理
            if publish_date:
                parsed_date = parse_date(publish_date)
                if parsed_date:
                    fields["发布日期"] = parsed_date
            
            # 添加到缓存
            hash_cache.add(content_hash)
            
            return {"status": "success", "data": fields}
            
        except Exception as e:
            console.print(f"[red]❌ 处理失败 {json_file.name}: {e}[/red]")
            return {"status": "failed", "data": None}


async def process_folder(folder_path: Path, topic: str, limit: int = 0, target: str = "web3") -> Dict[str, int]:
    """处理单个文件夹，使用并发 LLM 调用"""
    
    json_files = list(folder_path.glob("*.json"))
    if limit > 0:
        json_files = json_files[:limit]
    
    if not json_files:
        console.print(f"[dim]   跳过空文件夹[/dim]")
        return {"success": 0, "skipped": 0, "failed": 0}
    
    console.print(f"   找到 {len(json_files)} 个 JSON 文件")
    console.print(f"   [cyan][ASYNC] 并发模式: {LLM_CONCURRENCY} 个并行 LLM 调用[/cyan]")
    
    # 根据 target 选择表格 ID
    if target == "web2":
        console.print(f"   [cyan]目标表格: Web2 Style[/cyan]")
    else:
        console.print(f"   [cyan]目标表格: Web3 Knowledge[/cyan]")
    
    if not app_token or not table_id:
        return {"success": 0, "skipped": 0, "failed": len(json_files)}
    
    # 获取 Hash 缓存
    hash_cache = get_hash_cache()
    
    # 创建并发控制信号量
    semaphore = asyncio.Semaphore(LLM_CONCURRENCY)
    
    # 并发处理所有文件
    console.print(f"   [yellow][PROCESSING] 并发处理中...[/yellow]")
    start_time = datetime.now()
    
    tasks = [
        process_single_file(json_file, topic, hash_cache, semaphore)
        for json_file in json_files
    ]
    
    results = await asyncio.gather(*tasks)
    
    elapsed = (datetime.now() - start_time).total_seconds()
    console.print(f"   [green]✅ LLM 处理完成! 耗时: {elapsed:.1f}s ({len(json_files)/elapsed:.1f} 条/秒)[/green]")
    
    # 统计结果
    stats = {"success": 0, "skipped": 0, "failed": 0}
    records_to_upload = []
    
    for result in results:
        if result is None:
            stats["failed"] += 1
        elif result["status"] == "success":
            stats["success"] += 1
            records_to_upload.append(result["data"])
        elif result["status"] == "skipped":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1

    
    if records_to_upload:
        console.print(f"   [UPLOAD] 批量上传 {len(records_to_upload)} 条记录...")
        
        for i in range(0, len(records_to_upload), BATCH_SIZE):
            batch = records_to_upload[i:i+BATCH_SIZE]
            try:
                if result.get("code") == 0:
                    stats["success"] += len(batch)
                else:
                    console.print(f"[red][ERROR] 批量上传失败: {result.get('msg')}[/red]")
                    stats["failed"] += len(batch)
            except Exception as e:
                console.print(f"[red][ERROR] 批量上传异常: {e}[/red]")
                stats["failed"] += len(batch)
    
    # 保存 Hash 缓存
    hash_cache.save()
    
    console.print(f"   [OK] 成功: {stats['success']} | [SKIP] 跳过: {stats['skipped']} | [FAIL] 失败: {stats['failed']}")
    
    return stats


async def main():
    parser = argparse.ArgumentParser(description="Knowledge_Repo 优化版入库脚本 (A/B 测试)")
    parser.add_argument("--folder", type=str, help="指定处理的文件夹名称")
    parser.add_argument("--all", action="store_true", help="处理所有文件夹")
    parser.add_argument("--path", type=str, help="指定自定义目录路径 (支持任意本地目录)")
    parser.add_argument("--target", type=str, default="web3", choices=["web3", "web2"], help="目标表格 (web3 | web2)")
    parser.add_argument("--limit", type=int, default=0, help="每个文件夹处理的最大文件数 (0=不限制)")
    # Web2 专用参数
    parser.add_argument("--author", type=str, default="", help="[Web2] 博主名称")
    parser.add_argument("--style", type=str, default="", help="[Web2] 风格标签 (mimeng/banfo 等)")
    args = parser.parse_args()
    
    if not args.folder and not args.all and not args.path:
        parser.print_help()
        return
    
    console.print("=" * 60)
    console.print("[INFO] Quantum Studio v5.2 - Knowledge_Repo 优化版入库")
    console.print("=" * 60)
    console.print(f"[CONFIG] 优化特性: 合并LLM调用 + 批量上传 + 本地Hash缓存")
    console.print()
    
    total_stats = {"success": 0, "skipped": 0, "failed": 0}
    
    if args.path:
        # 自定义路径模式
        custom_path = Path(args.path)
        if not custom_path.exists():
            console.print(f"[red][ERROR] 自定义目录不存在: {custom_path}[/red]")
            return
        
        console.print(f"[FOLDER] 自定义目录模式: {custom_path}")
        
        # 处理目录下的所有 JSON/TXT 文件
        json_files = list(custom_path.glob("*.json"))
        txt_files = list(custom_path.glob("*.txt"))
        md_files = list(custom_path.glob("*.md"))
        all_files = json_files + txt_files + md_files
        
        if not all_files:
            console.print(f"[yellow][WARN] 目录中没有找到 JSON/TXT/MD 文件[/yellow]")
            return
        
        console.print(f"找到 {len(all_files)} 个文件 (JSON: {len(json_files)}, TXT: {len(txt_files)}, MD: {len(md_files)})")
        
        # =====================================
        # Web2 模式：委托给 cleaner_cli.py
        # =====================================
        if args.target == "web2":
            console.print("[cyan]检测到 Web2 模式，委托给 cleaner_cli.py 处理...[/cyan]")
            
            # 确定 author 和 style
            author = args.author if args.author else custom_path.name
            style = args.style if args.style else custom_path.name.lower()
            
            console.print(f"[CONFIG] 博主: {author}")
            console.print(f"[CONFIG] 风格: {style}")
            
            # 构建 cleaner_cli 命令
            backend_dir = Path(__file__).parent.parent
            cleaner_cmd = [
                sys.executable, "-m", "tools.cleaner_cli", "clean",
                "--input", str(custom_path),
                "--author", author,
                "--style", style,
                "--source-category", "Shell",
                "--provider", "deepseek",
                "--min-score", "3"
            ]
            
            console.print(f"[dim]执行: {' '.join(cleaner_cmd)}[/dim]")
            console.print()
            
            # 设置 UTF-8 编码环境，避免 Windows 编码问题
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run(cleaner_cmd, cwd=str(backend_dir), env=env)
            
            if result.returncode == 0:
                console.print("[green]✅ Web2 清洗完成[/green]")
            else:
                console.print(f"[red]❌ cleaner_cli 返回错误码: {result.returncode}[/red]")
            
            return  # 提前返回，不执行 Web3 逻辑
        
        # =====================================
        # Web3 模式：现有逻辑
        # =====================================
        # 使用目录名作为 topic
        topic = custom_path.name
        total_stats = await process_folder(custom_path, topic, args.limit, args.target)
        
    elif args.all:
        folders = sorted([f for f in WEB3_DATA_DIR.iterdir() if f.is_dir()])
        console.print(f"找到 {len(folders)} 个赛道文件夹\n")
        
        for folder in folders:
            console.print(f"[FOLDER] 处理文件夹: {folder.name}")
            stats = await process_folder(folder, folder.name, args.limit, args.target)
            for key in total_stats:
                total_stats[key] += stats[key]
            console.print()
    else:
        folder_path = WEB3_DATA_DIR / args.folder
        if not folder_path.exists():
            console.print(f"[red][ERROR] 文件夹不存在: {folder_path}[/red]")
            return
        
        console.print(f"[FOLDER] 处理文件夹: {args.folder}")
        total_stats = await process_folder(folder_path, args.folder, args.limit, args.target)
    
    console.print("=" * 60)
    console.print("[DONE] 入库完成!")
    console.print("=" * 60)
    console.print(f"  [OK] 成功入库: {total_stats['success']}")
    console.print(f"  [SKIP] 重复跳过: {total_stats['skipped']}")
    console.print(f"  [FAIL] 失败: {total_stats['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
