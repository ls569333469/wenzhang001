"""
P11 统一数据导入器 v1.0
========================
支持 JSON 直接导入和 TXT AI 处理两种模式。

Features:
- 🔄 自动识别输入类型 (JSON/TXT)
- 📄 JSON 直接映射字段，无需 AI
- 🤖 TXT 调用 AI 处理
- 🔀 双库路由 (Style_Repo / Knowledge_Repo)

Usage:
    python -m tools.unified_importer import --input data/Web3素材 --target knowledge
"""

import os
import sys
import json
import asyncio
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

try:
    import typer
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from openai import AsyncOpenAI
except ImportError:
    print("Missing dependencies. Run: pip install typer rich openai")
    sys.exit(1)

console = Console()
app = typer.Typer(help="P11 统一数据导入器 v1.0")

# ==========================================
# 配置
# ==========================================
CONCURRENCY_LIMIT = 10  # 高并发处理
MAX_TOKENS = 30000
CHECKPOINT_FILE = Path(__file__).parent.parent / "data" / ".unified_importer_checkpoint.json"

# ==========================================
# Prompt 模板 (含 Few-Shot)
# ==========================================

KERNEL_KNOWLEDGE_PROMPT = """
# Role
你是 Web3 知识库管理员，负责从文章中提取结构化信息。

# Task
从原文中提取完整字段，输出标准 JSON。

# 示例1
输入: "Uniswap V4 正式上线，TVL 达到 50 亿美元，较 V3 提升 120%。"
输出:
```json
{
  "title": "Uniswap V4 正式上线",
  "summary": "Uniswap V4 上线，TVL 达 50 亿美元，较 V3 提升 120%",
  "fact_type": "里程碑",
  "info_depth": "中",
  "keywords": ["Uniswap", "V4", "TVL", "DEX"],
  "track": "DeFi"
}
```

# 示例2
输入: "某项目完成 1000 万美元 A 轮融资，由 a16z 领投，Paradigm 跟投。"
输出:
```json
{
  "title": "某项目完成 A 轮融资",
  "summary": "获 1000 万美元融资，a16z 领投，Paradigm 跟投",
  "fact_type": "融资",
  "info_depth": "浅",
  "keywords": ["融资", "a16z", "Paradigm", "A轮"],
  "track": "VC投融资"
}
```

# 输出规范
严格按以下 JSON 格式输出，不要有多余文字：
{
  "title": "标题 (15-30字)",
  "summary": "核心摘要 (50-200字)",
  "fact_type": "快讯/研报/分析/教程/里程碑/融资",
  "info_depth": "浅/中/深",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "track": "DeFi/NFT/Layer2/DAO/GameFi/AI_Crypto/VC投融资/安全/监管/其他"
}

# 现在处理以下内容:
"""

STYLE_EXTRACT_PROMPT = """
# Role
你是文学解构专家，负责提取高质量写作片段。

# Task
从原文中提取值得学习的写作片段，输出标准 JSON。

# 输出规范
{
  "content": "清洗后的内容（去名化）",
  "snippet_type": "Hook/Body/Quote/CTA",
  "quality_score": 5
}
"""

# ==========================================
# 数据结构
# ==========================================

class KnowledgeRecord(BaseModel):
    """Knowledge_Repo 记录"""
    title: str = ""
    summary: str = ""
    full_text: str = ""
    fact_type: str = "快讯"
    info_depth: str = "中"
    keywords: List[str] = []
    publish_date: Optional[str] = None
    source_file: str = ""
    track: str = "其他"
    content_hash: str = ""

class StyleRecord(BaseModel):
    """Style_Repo 记录"""
    content: str = ""
    author: str = ""
    snippet_type: str = "Quote"
    status: str = "待处理"

# ==========================================
# 工具函数
# ==========================================

def get_content_hash(text: str) -> str:
    """计算内容 MD5 指纹"""
    return hashlib.md5(text.strip().encode('utf-8')).hexdigest()

def detect_file_type(file_path: Path) -> str:
    """检测文件类型"""
    suffix = file_path.suffix.lower()
    if suffix == '.json':
        return 'json'
    elif suffix in ['.txt', '.md']:
        return 'txt'
    else:
        return 'unknown'

def chunk_text(text: str, max_chars: int = 3000) -> List[str]:
    """按段落切分长文本"""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current = ""
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if len(current) + len(para) + 2 < max_chars:
            current += para + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para + "\n\n"
    
    if current.strip():
        chunks.append(current.strip())
    
    return chunks if chunks else [text[:max_chars]]

def load_checkpoint() -> set:
    """加载断点记录"""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get("processed_files", []))
        except:
            pass
    return set()

def save_checkpoint(processed_files: set):
    """保存断点记录"""
    try:
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({"processed_files": list(processed_files)}, f)
    except:
        pass

def clear_checkpoint():
    """清除断点记录"""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

# ==========================================
# JSON 直接导入
# ==========================================

async def import_json_file(file_path: Path, target: str) -> Optional[Dict[str, Any]]:
    """直接导入 JSON 文件 (无需 AI) - 与 ingest_knowledge.py 对齐"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 映射字段到 Knowledge_Repo - 与 ingest_knowledge.py 完全对齐
        record = {
            "标题": data.get("title", file_path.stem),
            "内容": data.get("content", ""),  # 对齐 ingest_knowledge.py
            "赛道分类": data.get("track", file_path.parent.name),
            "内容类型": "快讯资讯",  # 默认值，与 ingest_knowledge.py 对齐
            "来源文件": file_path.name,
            "来源链接": data.get("url", ""),  # 对齐 ingest_knowledge.py
            "内容指纹": get_content_hash(data.get("content", "")),
            "质量评分": 5.0,  # 默认中等分数
            "状态": "待处理"  # 对齐 ingest_knowledge.py
        }
        
        # 日期字段特殊处理
        published_at = data.get("published_at", "")
        if published_at:
            record["发布日期"] = published_at
        
        return record
    except Exception as e:
        console.print(f"[red]JSON 解析错误: {file_path.name} - {e}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]JSON 解析错误: {file_path.name} - {e}[/red]")
        return None

# ==========================================
# TXT AI 处理
# ==========================================

async def process_txt_with_ai(
    file_path: Path,
    client: AsyncOpenAI,
    model_name: str,
    semaphore: asyncio.Semaphore
) -> List[Dict[str, Any]]:
    """使用 AI 处理 TXT 文件"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception:
        return []
    
    chunks = chunk_text(text)
    results = []
    
    for chunk in chunks:
        async with semaphore:
            try:
                response = await client.chat.completions.create(
                    model=model_name,
                    temperature=0,
                    messages=[
                        {"role": "system", "content": KERNEL_KNOWLEDGE_PROMPT},
                        {"role": "user", "content": chunk}
                    ],
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                if content.startswith("```"):
                    content = content.replace("```json", "").replace("```", "")
                
                data = json.loads(content)
                
                record = {
                    "标题": data.get("title", ""),
                    "内容": data.get("summary", chunk),  # 对齐 ingest_knowledge.py
                    "赛道分类": data.get("track", file_path.parent.name),
                    "内容类型": "快讯资讯",  # 默认值
                    "来源文件": file_path.name,
                    "来源链接": "",
                    "内容指纹": get_content_hash(chunk),
                    "质量评分": 5.0,
                    "状态": "待处理"  # 对齐 ingest_knowledge.py
                }
                results.append(record)
                
            except Exception as e:
                console.print(f"[yellow]AI 处理错误: {e}[/yellow]")
                continue
    
    return results

# ==========================================
# Lark 上传
# ==========================================

async def upload_to_lark(record: Dict[str, Any], target: str) -> bool:
    """上传到 Lark"""
    try:
        from app.core.lark_client import lark_client
        
        app_token = os.getenv("LARK_BASE_TOKEN")
        
        if target == "knowledge":
            table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
        else:
            table_id = os.getenv("LARK_TABLE_ID")
        
        if not app_token or not table_id:
            return False
        
        # 去重检查
        content_hash = record.get("内容指纹", "")
        # TODO: 实现 Lark 端去重
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: lark_client.create_record(app_token, table_id, record)
        )
        return True
        
    except Exception as e:
        console.print(f"[red]Lark 上传错误: {e}[/red]")
        return False

# ==========================================
# 主入口
# ==========================================

@app.command()
def import_data(
    input_path: str = typer.Option(..., "--input", "-i", help="输入路径 (文件或目录)"),
    target: str = typer.Option("knowledge", "--target", "-t", help="目标库: knowledge / style"),
    provider: str = typer.Option("volcengine", "--provider", "-p", help="AI 模型: volcengine / google"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅测试，不上传")
):
    """
    统一数据导入器
    
    自动识别 JSON/TXT 格式，路由到对应处理逻辑。
    """
    asyncio.run(_import_async(input_path, target, provider, dry_run))

async def _import_async(input_path: str, target: str, provider: str, dry_run: bool):
    """异步导入逻辑"""
    
    console.print(f"[bold green]🚀 P11 统一数据导入器 v1.0[/bold green]")
    console.print(f"   📁 输入: {input_path}")
    console.print(f"   🎯 目标: {target}")
    console.print(f"   🤖 模型: {provider}")
    
    # 获取文件列表
    input_p = Path(input_path)
    if not input_p.exists():
        console.print(f"[red]错误: 路径不存在[/red]")
        return
    
    if input_p.is_file():
        all_files = [input_p]
    else:
        all_files = list(input_p.glob("**/*.json")) + list(input_p.glob("**/*.txt"))
    
    if not all_files:
        console.print(f"[yellow]没有找到 JSON/TXT 文件[/yellow]")
        return
    
    console.print(f"   📄 文件数: {len(all_files)}")
    
    # 初始化 AI 客户端
    client = AsyncOpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=os.getenv("ARK_API_KEY")
    )
    
    # P14: 统一使用火山引擎，根据 provider 选择不同模型
    if provider == "google":
        # Google Gemini 需要单独处理 (暂不支持 cleaner)
        console.print(f"[yellow]警告: Google 模型暂不支持 cleaner，使用 volcengine 替代[/yellow]")
        model_name = "doubao-seed-1-8-251228"
    else:
        # 默认使用火山引擎 DeepSeek 模型
        model_name = "deepseek-v3-2-251201"
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    total_uploaded = 0
    total_processed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console
    ) as progress:
        task_id = progress.add_task("处理中...", total=len(all_files))
        
        for file_path in all_files:
            file_type = detect_file_type(file_path)
            
            if file_type == 'json':
                # JSON 直接导入
                record = await import_json_file(file_path, target)
                if record:
                    total_processed += 1
                    if not dry_run:
                        if await upload_to_lark(record, target):
                            total_uploaded += 1
                    else:
                        total_uploaded += 1
            
            elif file_type == 'txt':
                # TXT AI 处理
                records = await process_txt_with_ai(file_path, client, model_name, semaphore)
                for record in records:
                    total_processed += 1
                    if not dry_run:
                        if await upload_to_lark(record, target):
                            total_uploaded += 1
                    else:
                        total_uploaded += 1
            
            progress.advance(task_id)
    
    console.print("")
    console.print(f"[bold green]🎉 完成![/bold green]")
    console.print(f"   📊 处理总数: {total_processed}")
    console.print(f"   📤 入库总数: {total_uploaded}")

@app.command()
def stats():
    """查看数据库统计"""
    from app.core.lark_client import lark_client
    
    app_token = os.getenv("LARK_BASE_TOKEN")
    style_id = os.getenv("LARK_TABLE_ID")
    knowledge_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
    
    style_resp = lark_client.list_records(app_token, style_id, page_size=1)
    knowledge_resp = lark_client.list_records(app_token, knowledge_id, page_size=1)
    
    style_count = style_resp.get('data', {}).get('total', 0)
    knowledge_count = knowledge_resp.get('data', {}).get('total', 0)
    
    console.print(f"[bold]📊 数据库统计[/bold]")
    console.print(f"   🩸 Style_Repo: {style_count} 条")
    console.print(f"   🥩 Knowledge_Repo: {knowledge_count} 条")

if __name__ == "__main__":
    app()
