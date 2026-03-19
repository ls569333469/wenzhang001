"""
Quantum Studio v3.0 - Antigravity 智能清洗入库脚本
==================================================


Usage:
    cd backend
    python -m scripts.ingest_antigravity --folder "DeFi进展与分析" --limit 10
    python -m scripts.ingest_antigravity --all --limit 50
"""

import os
import sys
import json
import hashlib
import asyncio
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# ==========================================
# 配置 (优化版 v3.1)
# ==========================================

WEB3_DATA_DIR = Path(__file__).parent.parent / "data" / "Web3素材"

# 性能参数
CONCURRENCY_LIMIT = 5   # 并发数 (从 3 提升到 5)
MAX_RETRIES = 3         # 最大重试次数
RETRY_DELAY = 2         # 重试间隔 (秒)

# v3.0 Prompt 模板 (优化版 - 使用句子数约束)
SYSTEM_PROMPT = """**Role**: 
你是一个 Web3 行业情报清洗专家。

**Task**: 
阅读输入的文章内容，提取关键信息，并**严格输出**为一个标准的 JSON 对象。不要输出 Markdown 标记或任何其他废话。

**Output Requirement (Strict JSON Format)**:
请严格按照以下 Keys 输出，Key 必须保持英文，Value 使用中文：
{
  "title": "文章标题，不超过30字",
  "summary": "用3-5句话概括核心内容。必须包含：1)核心事件 2)关键数据(如金额、涨跌幅) 3)重要人名或项目名。",
  "keywords": "3-5个关键词，用英文逗号分隔。",
  "info_depth": "请判断文章深度，只能输出以下三个词之一：'快讯' (短消息), '资讯' (一般新闻), '深度' (长文研报)。",
  "fact_type": "请判断内容类型，只能输出以下三个词之一：'事实' (客观发生), '观点' (某人预测), '黑话' (概念解释)。",
  "publish_date": "从文中提取日期，格式必须为 'YYYY-MM-DD'。如果文中没有日期，输出 'Today'。"
}"""

# ==========================================
# 工具函数
# ==========================================

def compute_hash(text: str) -> str:
    """计算内容 MD5 哈希"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

async def retry_async(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """异步重试包装器"""
    last_error = None
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))  # 递增延迟
                console.print(f"[yellow]⚠️ 重试中 ({attempt + 2}/{max_retries})...[/yellow]")
    raise last_error

def truncate_summary(summary: str, max_chars: int = 180) -> str:
    """按句子截断摘要，确保不超过最大字符数"""
    if not summary or len(summary) <= max_chars:
        return summary
    
    # 按句号拆分，保留完整句子
    sentences = summary.split('。')
    truncated = ''
    for s in sentences:
        if len(truncated) + len(s) + 1 <= max_chars - 3:  # 预留 "..." 空间
            truncated += s + '。'
        else:
            break
    
    if not truncated:
        return summary[:max_chars - 3] + '...'
    return truncated.rstrip('。') + '。'

def clean_json_response(response: str) -> str:
    """清理 LLM 返回的 JSON（移除 markdown 标记）"""
    response = response.strip()
    # 移除 ```json 和 ``` 标记
    response = re.sub(r'^```json\s*', '', response)
    response = re.sub(r'^```\s*', '', response)
    response = re.sub(r'\s*```$', '', response)
    return response.strip()

def parse_date_v3(date_str: str) -> Optional[int]:
    if not date_str or date_str == "Today":
        return int(datetime.now().timestamp() * 1000)
    
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    return int(datetime.now().timestamp() * 1000)

# ==========================================
# LLM 调用
# ==========================================

async def extract_with_antigravity(content: str, topic: str) -> dict:
    """使用 Gemini 提取结构化信息"""
    from app.core.llm import generate_text
    
    user_prompt = f"""**Input Content**: 
{content[:8000]}

请严格输出 JSON 格式："""
    
    try:
        response = await asyncio.to_thread(
            generate_text,
            prompt=user_prompt,  # 修正参数名
            system_prompt=SYSTEM_PROMPT,
            provider="volcengine",
            temperature=0.3
        )
        
        # 清理并解析 JSON
        clean_response = clean_json_response(response)
        data = json.loads(clean_response)
        return data
        
    except json.JSONDecodeError as e:
        console.print(f"[yellow]⚠️ JSON 解析失败: {e}[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]❌ LLM 调用失败: {e}[/red]")
        return None

# ==========================================
# ==========================================

async def check_exists_async(content_hash: str, app_token: str, table_id: str) -> bool:
    """查重：检查是否已存在"""
    
    try:
        filter_str = f'CurrentValue.[内容指纹] = "{content_hash}"'
        result = await asyncio.to_thread(
        )
        items = result.get("data", {}).get("items", [])
        return len(items) > 0
    except Exception:
        return False

async def upload_record_async(
    structured_data: dict,
    topic: str,
    raw_content: str,
    content_hash: str,
    source_file: str,
    app_token: str,
    table_id: str
) -> bool:
    """上传记录到 Knowledge_Repo"""
    
    # v3.0 字段映射 (含摘要截断)
    raw_summary = structured_data.get("summary", "")
    safe_summary = truncate_summary(raw_summary, max_chars=180)
    
    fields = {
        "标题": structured_data.get("title", "无标题"),
        "核心摘要": safe_summary,  # 已截断
        "关键词": structured_data.get("keywords", ""),
        "信息深度": structured_data.get("info_depth", "资讯"),
        "事实类型": structured_data.get("fact_type", "事实"),
        "赛道分类": topic,
        "来源文件": source_file,
        "内容指纹": content_hash,
        "状态": "待处理"
    }
    
    # 日期处理
    publish_date = parse_date_v3(structured_data.get("publish_date", ""))
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

async def upload_with_retry(
    structured_data: dict,
    topic: str,
    raw_content: str,
    content_hash: str,
    source_file: str,
    app_token: str,
    table_id: str
) -> bool:
    """带重试的上传函数"""
    for attempt in range(MAX_RETRIES):
        try:
            success = await upload_record_async(
                structured_data, topic, raw_content, content_hash, source_file, app_token, table_id
            )
            if success:
                return True
            return False
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                console.print(f"[yellow]⚠️ 网络错误，重试中 ({attempt + 2}/{MAX_RETRIES})...[/yellow]")
            else:
                console.print(f"[red]❌ 重试耗尽: {e}[/red]")
                return False
    return False

# ==========================================
# 文件处理
# ==========================================

async def process_txt_file(
    file_path: Path,
    topic: str,
    app_token: str,
    table_id: str,
    semaphore: asyncio.Semaphore
) -> Tuple[bool, str]:
    """处理单个 TXT 文件"""
    async with semaphore:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            if not raw_content or len(raw_content) < 100:
                return False, "内容过短"
            
            # 查重
            content_hash = compute_hash(raw_content)
            if await check_exists_async(content_hash, app_token, table_id):
                return False, "已存在"
            
            # Antigravity 智能清洗
            structured_data = await extract_with_antigravity(raw_content, topic)
            if not structured_data:
                return False, "LLM 清洗失败"
            
            # 上传 (带重试)
            success = await upload_with_retry(
                structured_data=structured_data,
                topic=topic,
                raw_content=raw_content,
                content_hash=content_hash,
                source_file=file_path.name,
                app_token=app_token,
                table_id=table_id
            )
            
            if success:
                return True, "成功"
            else:
                return False, "上传失败"
                
        except Exception as e:
            return False, str(e)

async def process_folder(
    folder_name: str,
    app_token: str,
    table_id: str,
    limit: int = None
) -> Tuple[int, int, int]:
    """处理单个文件夹"""
    folder_path = WEB3_DATA_DIR / folder_name
    
    if not folder_path.exists():
        console.print(f"[red]❌ 文件夹不存在: {folder_path}[/red]")
        return 0, 0, 0
    
    # 收集 TXT 和 JSON 文件
    files = list(folder_path.glob("*.txt")) + list(folder_path.glob("*.json"))
    
    if limit:
        files = files[:limit]
    
    if not files:
        return 0, 0, 0
    
    console.print(f"\n📂 处理文件夹: [cyan]{folder_name}[/cyan]")
    console.print(f"   找到 {len(files)} 个文件")
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("入库中...", total=len(files))
        
        for file_path in files:
            success, reason = await process_txt_file(
                file_path, folder_name, app_token, table_id, semaphore
            )
            
            if success:
                success_count += 1
            elif reason == "已存在":
                skip_count += 1
            else:
                fail_count += 1
            
            progress.update(task, advance=1)
        
        progress.update(task, description=f"✅ 成功: {success_count} | ⚠️ 跳过: {skip_count} | ❌ 失败: {fail_count}")
    
    return success_count, skip_count, fail_count

# ==========================================
# 主入口
# ==========================================

async def main():
    parser = argparse.ArgumentParser(description="v3.0 Antigravity 智能清洗入库")
    parser.add_argument("--folder", type=str, help="指定文件夹名称")
    parser.add_argument("--all", action="store_true", help="处理所有文件夹")
    parser.add_argument("--limit", type=int, default=None, help="每个文件夹最大处理数量")
    args = parser.parse_args()
    
    # 配置
    
    console.print("=" * 60)
    console.print("🚀 Quantum Studio v3.0 - Antigravity 智能清洗")
    console.print("=" * 60)
    console.print(f"📋 Base Token: {app_token}")
    console.print(f"📋 Knowledge Table ID: {table_id}")
    
    total_success = 0
    total_skip = 0
    total_fail = 0
    
    if args.folder:
        s, sk, f = await process_folder(args.folder, app_token, table_id, args.limit)
        total_success += s
        total_skip += sk
        total_fail += f
    
    elif args.all:
        folders = [f.name for f in WEB3_DATA_DIR.iterdir() if f.is_dir()]
        for folder in sorted(folders):
            s, sk, f = await process_folder(folder, app_token, table_id, args.limit)
            total_success += s
            total_skip += sk
            total_fail += f
    
    else:
        console.print("[yellow]请指定 --folder 或 --all 参数[/yellow]")
        return
    
    console.print("\n" + "=" * 60)
    console.print("📊 入库完成!")
    console.print("=" * 60)
    console.print(f"  ✅ 成功入库: {total_success}")
    console.print(f"  ⚠️ 重复跳过: {total_skip}")
    console.print(f"  ❌ 失败: {total_fail}")

if __name__ == "__main__":
    asyncio.run(main())
