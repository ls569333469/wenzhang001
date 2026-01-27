"""
P12.1 - Lark Data Cleaning CLI Tool v2.0 (Industrial Grade)
============================================================
基于 Shell-Kernel 壳肉分离法的工业级数据清洗工具。

Features:
- ⚡ 异步并发 (AsyncIO + Semaphore)
- 🛡️ 断点续传 (processed_log.json)
- 📄 智能分片 (3000 字符/片)
- 🔄 MD5 去重 (避免重复入库)

Usage:
    python -m tools.cleaner_cli clean --folder data/mimeng --author 咪蒙 --style mimeng --source-category Shell
"""

import os
import sys
import json
import asyncio
import hashlib
from pathlib import Path
from typing import List, Optional, Set, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

try:
    import typer
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from openai import AsyncOpenAI
    import tenacity
except ImportError:
    print("Missing dependencies. Run: pip install typer rich openai tenacity")
    sys.exit(1)

console = Console()
app = typer.Typer(help="Lark 数据清洗工具 v2.0 - 工业级异步版")

# ==========================================
# 1. 配置区 (Configuration)
# ==========================================
CONCURRENCY_LIMIT = 10  # 同时并发多少个请求 (提高以加速清洗)
CHECKPOINT_FILE = Path(__file__).parent / "processed_log.json"
CHUNK_SIZE = 3000  # 每个分片的最大字符数

# ==========================================
# 2. 配置加载 (从 .env 和 user_config.json 读取)
# ==========================================

def load_api_config() -> dict:
    """从 user_config.json 加载前端配置的 API Keys"""
    config_path = Path(__file__).parent.parent / "config" / "user_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# ==========================================
# 3. 异步模型工厂 (Async LLM Factory)
# ==========================================

class AsyncLLMProvider:
    """异步 LLM 提供商适配器"""
    
    def __init__(self, provider_name: str):
        self.name = provider_name
        self.client: Optional[AsyncOpenAI] = None
        self.model_name = ""
        self.user_config = load_api_config()

    def _get_api_key(self, env_key: str, config_key: str) -> Optional[str]:
        """优先从 .env 读取，fallback 到 user_config.json"""
        key = os.getenv(env_key)
        if key:
            return key
        api_keys = self.user_config.get("api_keys", {})
        return api_keys.get(config_key)

    def connect(self) -> tuple:
        """连接到指定的 LLM 提供商 (异步客户端)"""
        if self.name == "doubao":
            # 火山引擎豆包 - 豆包最新模型
            api_key = self._get_api_key("ARK_API_KEY", "doubao")
            base_url = "https://ark.cn-beijing.volces.com/api/v3"
            self.model_name = "doubao-seed-1-8-251228"
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            
        elif self.name == "deepseek" or self.name == "deepseek-ark":
            # 火山引擎 DeepSeek V3.2 - 数据清洗推荐 (更便宜)
            api_key = self._get_api_key("ARK_API_KEY", "deepseek")
            base_url = "https://ark.cn-beijing.volces.com/api/v3"
            self.model_name = "deepseek-v3-2-251201"
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            
        elif self.name == "gemini":
            # Google Gemini 3 Pro
            api_key = self._get_api_key("GOOGLE_API_KEY", "gemini")
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            self.model_name = "gemini-3-pro-preview"
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            raise ValueError(f"不支持的模型提供商: {self.name}")

        if not self.client or not self.client.api_key:
            raise ValueError(f"未找到 {self.name} 的 API Key")
        
        return self.client, self.model_name

# ==========================================
# 4. 数据结构 (Schema)
# ==========================================

class CleanedSnippet(BaseModel):
    """清洗后的素材片段"""
    original_text: str = Field(default="", description="原始片段")
    clean_text: str = Field(description="去名化后的通用内容")
    snippet_type: str = Field(default="Quote", description="Hook/Body/CTA/Quote/Hard_Fact")
    logic_pattern: str = Field(default="", description="逻辑公式")
    emotional_valence: str = Field(default="Neutral", description="情绪效价")
    quality_score: int = Field(default=5, description="评分 1-10")

# ==========================================
# 4.1 字段值映射 (英文 → 中文)
# ==========================================

SNIPPET_TYPE_MAP = {
    # 英文 → 中文
    "Hook": "开头金句",
    "Body": "正文段落",
    "Quote": "金句语录",
    "CTA": "行动号召",
    "Hard_Fact": "硬数据",
    # 中文直接通过
    "开头金句": "开头金句",
    "正文段落": "正文段落",
    "金句语录": "金句语录",
    "行动号召": "行动号召",
    "硬数据": "硬数据",
}

EMOTION_MAP = {
    # 英文 → 中文
    "Positive": "积极",
    "Negative": "消极",
    "Neutral": "中性",
    "High Arousal": "激昂",
    # 中文直接通过
    "积极": "积极",
    "消极": "消极",
    "中性": "中性",
    "激昂": "激昂",
    "共情": "共情",
}

# ==========================================
# 5. Prompt 模板
# ==========================================

SHELL_MINER_PROMPT = """
# Role
你是一个精通认知心理学和NLP的**顶级文学解构专家**。

# Context
当前日期: {current_date}

# Task
仔细阅读【文章片段】，提取**所有**有价值的写作素材片段。每个独立的观点、金句、故事都应作为一条单独的 snippet 输出。

# Extraction Guidelines
- 每个段落可能包含多个有价值的片段，请尽可能多地提取
- 精彩的金句、有洞察力的观点、情感共鸣的故事都是有价值的素材
- 控制每个 snippet 的 clean_text 长度在 50-300 字符之间

# Rules
1. **去名化**: 将具体人名（如"{author}"）替换为通用代词（"我"、"他"）
2. **逻辑公式**: 分析写作套路（如"先抑后扬 + 制造焦虑"）
3. **情绪效价**: High Arousal / Positive / Negative / Neutral
4. **时效性过滤**: 含节日/具体日期的内容 quality_score=1
5. **PS 内容降权**: "PS:"开头的广告 quality_score=2

# Quality Score 评分标准 (1-10分)
- 9-10分: 顶级金句，可直接复用，具有病毒传播潜力
- 7-8分: 优质内容，观点独特，有较强感染力
- 5-6分: 普通内容，有参考价值但不突出
- 3-4分: 质量一般，缺乏亮点
- 1-2分: 低质量，时效性内容或广告

# Output (JSON Only, 尽可能提取多条)
{{
  "snippets": [
    {{
      "original_text": "原文片段1...",
      "clean_text": "去名化后的精华内容1...",
      "snippet_type": "Hook/Body/CTA/Quote",
      "logic_pattern": "逻辑公式",
      "emotional_valence": "High Arousal",
      "quality_score": 8
    }},
    {{
      "original_text": "原文片段2...",
      "clean_text": "去名化后的精华内容2...",
      "snippet_type": "Quote",
      "logic_pattern": "情感共鸣",
      "emotional_valence": "Positive",
      "quality_score": 6
    }}
  ]
}}
"""

KERNEL_FILTER_PROMPT = """
# Role
你是一个冷酷的 **Web3 链上分析师**，只关心可验证的硬数据。

# Context
当前日期: {current_date}

# Task
从【快讯/研报】中提取核心事实，过滤营销噪音。

# Rules
1. **丢弃**: "战略升级"、"治理提案"等无实质内容
2. **保留**: TVL变动、大额转账、融资、黑客攻击、里程碑
3. **Logic_Pattern**: 统一填"数据背书"或"事件驱动"
4. **snippet_type 必须是中文**: 快讯 / 研报 / 分析 / 资讯 / 深度 (不要用英文)

# Output (JSON Only)
{{
  "snippets": [
    {{
      "original_text": "原文...",
      "clean_text": "精简事实...",
      "snippet_type": "快讯",
      "logic_pattern": "数据背书",
      "emotional_valence": "Neutral",
      "quality_score": 5
    }}
  ]
}}
"""

# ==========================================
# 6. 预扫描规划器 (v2.2 Smart Planner)
# ==========================================

def plan_processing(file_path: Path, chunk_size: int = CHUNK_SIZE) -> tuple:
    """
    v2.2 预扫描规划器：在处理前分析文件并规划策略
    返回: (text, total_chars, estimated_chunks, estimated_time_seconds)
    """
    import math
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    total_chars = len(text)
    estimated_chunks = math.ceil(total_chars / chunk_size) if total_chars > chunk_size else 1
    # 估算时间：每个分片约 3-5 秒
    estimated_time = estimated_chunks * 4  # 取中间值 4 秒
    
    return text, total_chars, estimated_chunks, estimated_time

def display_plan_summary(files: list, chunk_size: int = CHUNK_SIZE):
    """显示批量处理计划摘要"""
    import math
    
    total_files = len(files)
    total_chars = 0
    total_chunks = 0
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            chars = len(text)
            total_chars += chars
            total_chunks += math.ceil(chars / chunk_size) if chars > chunk_size else 1
        except Exception:
            continue
    
    estimated_time = total_chunks * 4  # 秒
    
    console.print(f"\n[bold cyan]📊 预处理分析结果:[/bold cyan]")
    console.print(f"   📁 文件数量: {total_files} 个")
    console.print(f"   📝 总字符数: {total_chars:,} 字符")
    console.print(f"   🔢 总分片数: {total_chunks} 块")
    console.print(f"   ⏱️ 预计耗时: {estimated_time // 60} 分 {estimated_time % 60} 秒")
    console.print("")
    
    return total_chunks, estimated_time

# ==========================================
# 7. 辅助函数
# ==========================================

def chunk_text(text: str, max_chars: int = CHUNK_SIZE) -> List[str]:
    """智能分片：按段落切分长文本"""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current = ""
    
    # 优先按段落切分
    paragraphs = text.split('\n\n')
    for para in paragraphs:
        if len(current) + len(para) + 2 < max_chars:
            current += para + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            # 如果单段落超长，按行切分
            if len(para) > max_chars:
                lines = para.split('\n')
                current = ""
                for line in lines:
                    if len(current) + len(line) + 1 < max_chars:
                        current += line + "\n"
                    else:
                        if current.strip():
                            chunks.append(current.strip())
                        current = line + "\n"
            else:
                current = para + "\n\n"
    
    if current.strip():
        chunks.append(current.strip())
    
    return chunks if chunks else [text[:max_chars]]

def get_content_hash(text: str) -> str:
    """计算文本 MD5 指纹，用于去重"""
    return hashlib.md5(text.strip().encode('utf-8')).hexdigest()

def load_checkpoint() -> Set[str]:
    """加载断点记录"""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def save_checkpoint(processed: Set[str]):
    """保存断点记录"""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed), f, ensure_ascii=False)

# ==========================================
# 7. 异步核心逻辑
# ==========================================

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import RateLimitError, APITimeoutError, APIConnectionError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIConnectionError))
)
async def call_llm_with_retry(client: AsyncOpenAI, model_name: str, messages: list):
    """带重试的 LLM 调用"""
    return await client.chat.completions.create(
        model=model_name,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.3
    )

async def process_single_chunk(
    chunk: str,
    author: str,
    source_category: str,
    client: AsyncOpenAI,
    model_name: str,
    semaphore: asyncio.Semaphore
) -> List[CleanedSnippet]:
    """处理单个分片 (异步，带并发控制)"""
    
    async with semaphore:
        # 获取当前日期
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        # 选择 Prompt
        if source_category.lower() == "shell":
            system_prompt = SHELL_MINER_PROMPT.format(author=author, current_date=current_date)
        else:
            system_prompt = KERNEL_FILTER_PROMPT.format(current_date=current_date)

        user_prompt = f"【待处理文本】\n作者: {author}\n内容:\n{chunk}"

        try:
            response = await call_llm_with_retry(
                client, 
                model_name, 
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            content = response.choices[0].message.content
            
            # 清理可能的 markdown 包裹
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "")
            
            data = json.loads(content)
            
            # 兼容性处理
            if "snippets" in data:
                snippets_data = data["snippets"]
            elif isinstance(data, list):
                snippets_data = data
            else:
                snippets_data = [data]

            result = [CleanedSnippet(**item) for item in snippets_data if item]
            
            # 🔍 诊断日志：记录每次 LLM 调用的提取结果 (Step 1)
            console.print(f"  [dim]LLM返回: {len(result)} 条[/dim]")
            
            return result

        except json.JSONDecodeError as e:
            console.print(f"  [red]❌ JSON解析失败: {str(e)[:50]}[/red]")
            return []
        except Exception as e:
            console.print(f"  [red]❌ LLM调用异常: {type(e).__name__}: {str(e)[:50]}[/red]")
            return []

async def check_exists_in_lark_async(content_hash: str) -> bool:
    """查询 Lark 是否已存在相同的 内容指纹"""
    try:
        from app.core.lark_client import lark_client
        app_token = os.getenv("LARK_BASE_TOKEN")
        table_id = os.getenv("LARK_TABLE_ID")
        
        loop = asyncio.get_event_loop()
        # Filter syntax: CurrentValue.['field_name'] = "value"
        filter_str = f'CurrentValue.[内容指纹] = "{content_hash}"'
        
        resp = await loop.run_in_executor(
            None, 
            lambda: lark_client.list_records(app_token, table_id, filter=filter_str, page_size=1)
        )
        
        if resp.get("code") == 0:
            items = resp.get("data", {}).get("items", [])
            return len(items) > 0
        return False
    except Exception:
        return False

# ==========================================
# 6.1 批量上传功能 (性能优化)
# ==========================================

BATCH_SIZE = 50  # 批量上传大小 (降低以便更快触发)

async def batch_upload_to_lark_async(
    records: List[Dict],
    source_category: str,
    max_retries: int = 3
) -> int:
    """批量上传记录到 Lark（带重试机制），返回成功上传数
    
    当 API 配额用尽时，自动保存到 CSV 文件供手动导入
    """
    if not records:
        return 0
        
    try:
        from app.core.lark_client import lark_client
        
        app_token = os.getenv("LARK_BASE_TOKEN")
        if source_category.lower() == "kernel":
            table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
        else:
            table_id = os.getenv("LARK_TABLE_ID")
        
        if not app_token or not table_id:
            return 0
        
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: lark_client.batch_create_records(app_token, table_id, records, timeout=120)
                )
                if result.get("code") == 0:
                    return len(result.get("data", {}).get("records", []))
                else:
                    error_msg = result.get('msg', '')
                    print(f"  ⚠️ 批量上传失败: {error_msg}")
                    
                    # 检测配额用尽，自动保存到 CSV
                    if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                        await save_records_to_csv(records, source_category)
                        return 0
                        
            except Exception as e:
                wait_time = 2 ** attempt
                print(f"  ⚠️ 批量上传异常 (重试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
        
        # 所有重试失败，保存到 CSV
        await save_records_to_csv(records, source_category)
        return 0
    except Exception as e:
        print(f"❌ 批量上传初始化失败: {e}")
        await save_records_to_csv(records, source_category)
        return 0


async def save_records_to_csv(records: List[Dict], source_category: str):
    """将记录保存到 CSV 文件（用于手动导入 Lark）"""
    import csv
    from datetime import datetime
    
    if not records:
        return
    
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = output_dir / f"lark_backup_{source_category}_{timestamp}.csv"
    
    # 确定字段名
    if source_category.lower() == "kernel":
        fieldnames = ["标题", "内容", "赛道分类", "内容类型", "来源文件", "来源链接", "内容指纹", "质量评分", "状态"]
    else:
        fieldnames = ["内容", "博主", "片段类型", "情绪", "内容指纹", "质量评分", "状态", "逻辑公式", "风格标签"]
    
    try:
        with open(csv_path, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            
            # 如果文件为空，写入表头
            if f.tell() == 0:
                writer.writeheader()
            
            for record in records:
                # 处理列表类型字段
                if "风格标签" in record and isinstance(record["风格标签"], list):
                    record["风格标签"] = ",".join(record["风格标签"])
                writer.writerow(record)
        
        print(f"  💾 已备份 {len(records)} 条记录到: {csv_path}")
    except Exception as e:
        print(f"  ❌ CSV 保存失败: {e}")


def prepare_lark_fields(snippet: CleanedSnippet, author: str, style: str, source_category: str) -> Dict:
    """准备 Lark 字段数据（不上传，只返回字段字典）"""
    content_hash = get_content_hash(snippet.clean_text)
    
    if source_category.lower() == "kernel":
        content_type_map = {"Hard_Fact": "硬数据", "Quote": "观点评论", "Hook": "快讯资讯", "Body": "深度分析", "CTA": "快讯资讯"}
        content_type = content_type_map.get(snippet.snippet_type, "快讯资讯")
        return {
            "标题": snippet.clean_text[:50], "内容": snippet.clean_text, "赛道分类": style or "其他",
            "内容类型": content_type, "来源文件": author, "来源链接": "", "内容指纹": content_hash,
            "质量评分": snippet.quality_score, "状态": "待处理"
        }
    else:
        snippet_type_cn = SNIPPET_TYPE_MAP.get(snippet.snippet_type, "金句语录")
        emotion_cn = EMOTION_MAP.get(snippet.emotional_valence, "中性") if snippet.emotional_valence else "中性"
        lp = snippet.logic_pattern.lower() if snippet.logic_pattern else ""
        style_tags = []
        if "毒舌" in lp or "讽刺" in lp: style_tags.append("毒舌")
        if "焦虑" in lp or "恐惧" in lp: style_tags.append("焦虑")
        if "逻辑" in lp or "推理" in lp or "分析" in lp: style_tags.append("逻辑")
        if "共情" in lp or "共鸣" in lp: style_tags.append("共情")
        if "对比" in lp or "反差" in lp: style_tags.append("对比")
        if "煽情" in lp or "情感" in lp: style_tags.append("煽情")
        if "数据" in lp or "事实" in lp: style_tags.append("数据流")
        if not style_tags: style_tags.append("逻辑")
        return {
            "内容": snippet.clean_text, "博主": author, "片段类型": snippet_type_cn, "情绪": emotion_cn,
            "内容指纹": content_hash, "质量评分": float(snippet.quality_score), "状态": "待处理",
            "逻辑公式": snippet.logic_pattern or "", "风格标签": style_tags
        }


async def upload_to_lark_async(snippet: CleanedSnippet, author: str, style: str, source_category: str = "Shell") -> bool:
    """异步上传到 Lark (带去重和重试)
    
    根据 source_category 选择不同的表：
    - Shell (风格素材/血) → LARK_TABLE_ID (Style_Repo)
    - Kernel (Web3知识/肉) → LARK_KNOWLEDGE_TABLE_ID (Knowledge_Repo)
    """
    try:
        from app.core.lark_client import lark_client
        
        app_token = os.getenv("LARK_BASE_TOKEN")
        
        # 根据 source_category 选择目标表
        if source_category.lower() == "kernel":
            table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")  # Knowledge_Repo (肉)
        else:
            table_id = os.getenv("LARK_TABLE_ID")  # Style_Repo (血)
        
        if not app_token or not table_id:
            return False

        # 1. Lark 端去重检查
        content_hash = get_content_hash(snippet.clean_text)
        if await check_exists_in_lark_async(content_hash):
            return False

        # 根据 source_category 使用不同的字段结构
        if source_category.lower() == "kernel":
            # Knowledge_Repo 表结构 - 与 ingest_knowledge.py 完全对齐
            # 字段: 标题, 内容, 赛道分类, 内容类型, 来源文件, 来源链接, 发布日期, 内容指纹, 质量评分, 状态
            
            # 内容类型映射 (与 ingest_knowledge.py 的 FACT_TYPE_LABELS 对齐)
            content_type_map = {
                # 英文 → 中文
                "Hard_Fact": "硬数据",
                "Quote": "观点评论",
                "Hook": "快讯资讯",
                "Body": "深度分析",
                "CTA": "快讯资讯",
                # 中文直接映射
                "快讯": "快讯资讯",
                "研报": "深度分析",
                "分析": "深度分析",
                "资讯": "快讯资讯",
                "深度": "深度分析",
            }
            
            # 确定内容类型
            content_type = snippet.snippet_type
            if content_type in content_type_map:
                content_type = content_type_map[content_type]
            elif content_type not in ["硬数据", "深度分析", "观点评论", "梗_黑话", "快讯资讯"]:
                content_type = "快讯资讯"  # 默认值
            
            fields = {
                "标题": snippet.clean_text[:50] if len(snippet.clean_text) > 50 else snippet.clean_text,
                "内容": snippet.clean_text,  # 对齐 ingest_knowledge.py
                "赛道分类": style if style else "其他",
                "内容类型": content_type,  # 对齐 ingest_knowledge.py
                "来源文件": author,
                "来源链接": "",  # TXT 文件无链接
                "内容指纹": content_hash,
                "质量评分": snippet.quality_score,  # 使用 AI 评分
                "状态": "待处理"  # 对齐 ingest_knowledge.py
            }
        else:
            # Style_Repo 表结构 (风格素材/血)
            # 完整 9 字段映射 (P12.3 更新: 字段值统一为中文)
            # 字段类型: 内容(Text), 博主(SingleSelect), 片段类型(SingleSelect), 
            #          情绪(SingleSelect), 内容指纹(Text), 质量评分(Number),
            #          状态(SingleSelect), 逻辑公式(Text), 风格标签(MultiSelect)
            
            # 应用中文映射转换
            snippet_type_cn = SNIPPET_TYPE_MAP.get(snippet.snippet_type, "金句语录")
            emotion_cn = EMOTION_MAP.get(snippet.emotional_valence, "中性") if snippet.emotional_valence else "中性"
            
            # 从 logic_pattern 推断风格标签
            style_tags = []
            lp = snippet.logic_pattern.lower() if snippet.logic_pattern else ""
            if "毒舌" in lp or "讽刺" in lp or "嘲讽" in lp:
                style_tags.append("毒舌")
            if "焦虑" in lp or "恐惧" in lp or "制造焦虑" in lp:
                style_tags.append("焦虑")
            if "逻辑" in lp or "推理" in lp or "分析" in lp:
                style_tags.append("逻辑")
            if "共情" in lp or "共鸣" in lp or "同理" in lp:
                style_tags.append("共情")
            if "对比" in lp or "反差" in lp or "转折" in lp:
                style_tags.append("对比")
            if "煽情" in lp or "情感" in lp or "感人" in lp:
                style_tags.append("煽情")
            if "数据" in lp or "事实" in lp:
                style_tags.append("数据流")
            # 默认至少有一个标签
            if not style_tags:
                style_tags.append("逻辑")
            
            fields = {
                "内容": snippet.clean_text,
                "博主": author,
                "片段类型": snippet_type_cn,  # 使用中文值
                "情绪": emotion_cn,           # 使用中文值
                "内容指纹": content_hash,
                "质量评分": float(snippet.quality_score),
                "状态": "待处理",
                "逻辑公式": snippet.logic_pattern if snippet.logic_pattern else "",
                "风格标签": style_tags  # 从 logic_pattern 推断
            }
        
        # 在线程池中运行同步代码
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            lambda: lark_client.create_record(app_token, table_id, fields)
        )
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Lark上传失败: {e}")
        traceback.print_exc()
        return False

async def process_file(
    file_path: Path,
    author: str,
    style: str,
    source_category: str,
    client: AsyncOpenAI,
    model_name: str,
    semaphore: asyncio.Semaphore,
    seen_hashes: Set[str],
    min_score: int,
    dry_run: bool,
    console: Console
) -> tuple:
    """处理单个文件"""
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return file_path.name, 0, 0

    # 智能分片
    chunks = chunk_text(text)
    total_chunks = len(chunks)
    
    if total_chunks > 10:
        console.print(f"  [dim]📄 {file_path.name}: {total_chunks} 分片[/dim]")
    
    # 为所有分片创建任务 (带超时)
    async def process_with_timeout(chunk, idx):
        try:
            return await asyncio.wait_for(
                process_single_chunk(chunk, author, source_category, client, model_name, semaphore),
                timeout=300.0  # 300 秒超时 (大文件处理需要更长时间)
            )
        except asyncio.TimeoutError:
            console.print(f"  [yellow]⏳ 分片 {idx}/{total_chunks} 超时[/yellow]")
            return []
    
    tasks = [
        process_with_timeout(chunk, i+1)
        for i, chunk in enumerate(chunks)
    ]
    
    # 使用 as_completed 实时获取结果
    all_snippets = []
    completed = 0
    for coro in asyncio.as_completed(tasks):
        result = await coro
        all_snippets.extend(result)
        completed += 1
        
        # 大文件显示进度
        if total_chunks > 20 and completed % 10 == 0:
            console.print(f"  [dim]  ⏳ {completed}/{total_chunks} 分片完成[/dim]")
    
    uploaded = 0
    filtered_by_score = 0
    filtered_by_local_hash = 0
    filtered_by_lark = 0
    pending_fields = []  # 待上传的字段列表
    
    for s in all_snippets:
        # 1. 分数过滤
        if s.quality_score < min_score:
            filtered_by_score += 1
            continue
            
        # 2. 本地去重过滤
        h = get_content_hash(s.clean_text)
        if h in seen_hashes:
            filtered_by_local_hash += 1
            continue
        seen_hashes.add(h)
        
        # 3. 准备上传字段
        if dry_run:
            uploaded += 1
        else:
            # Lark 端去重检查
            if await check_exists_in_lark_async(h):
                filtered_by_lark += 1
                continue
            # 准备字段而非直接上传
            fields = prepare_lark_fields(s, author, style, source_category)
            pending_fields.append(fields)
            uploaded += 1

    # 输出详细过滤统计
    if total_chunks > 10:
        console.print(f"  [dim]📊 过滤统计: 分数淘汰={filtered_by_score}, 本地去重={filtered_by_local_hash}, Lark去重={filtered_by_lark}[/dim]")

    return file_path.name, len(all_snippets), uploaded, pending_fields

# ==========================================
# 8. 主异步函数
# ==========================================

async def main_async(
    input_path: str,
    author: str,
    style: str,
    source_category: str,
    provider: str,
    min_score: int,
    dry_run: bool
):
    """主异步处理流程"""
    
    console.print(f"[bold green]🚀 P12.2 工业级清洗工具 v2.2[/bold green]")
    console.print(f"   📁 输入: {input_path}")
    console.print(f"   👤 作者: {author}")
    console.print(f"   🎨 风格: {style}")
    console.print(f"   📂 模式: {source_category}")
    console.print(f"   🤖 模型: {provider}")
    console.print(f"   ⭐ 最低分: {min_score}")
    console.print(f"   🔄 并发数: {CONCURRENCY_LIMIT}")
    console.print(f"   📄 分片大小: {CHUNK_SIZE} 字符")
    if dry_run:
        console.print(f"   [yellow]⚠️ DRY-RUN 模式[/yellow]")
    console.print("")

    # 1. 初始化 LLM
    try:
        llm = AsyncLLMProvider(provider)
        client, model_name = llm.connect()
        console.print(f"[dim]使用模型: {model_name}[/dim]")
    except Exception as e:
        console.print(f"[red]LLM 初始化失败: {e}[/red]")
        return

    # 2. 创建信号量
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    # 3. 获取文件列表 (智能识别文件/文件夹)
    input_p = Path(input_path)
    if not input_p.exists():
        console.print(f"[red]错误: 路径不存在 {input_path}[/red]")
        return

    # 自动识别: 文件 vs 文件夹
    if input_p.is_file():
        # 单个文件
        if not input_p.suffix.lower() == '.txt':
            console.print(f"[red]错误: 只支持 .txt 文件[/red]")
            return
        all_files = [input_p]
        console.print(f"[cyan]📄 单文件模式: {input_p.name}[/cyan]")
    else:
        # 文件夹
        all_files = list(input_p.glob("*.txt"))
        if not all_files:
            console.print(f"[yellow]警告: 文件夹中没有 .txt 文件[/yellow]")
            return
        console.print(f"[cyan]📂 文件夹模式: {len(all_files)} 个文件[/cyan]")

    # 4. 加载断点记录
    processed_files = load_checkpoint()
    if processed_files:
        console.print(f"[yellow]📦 检测到断点记录，已跳过 {len(processed_files)} 个文件[/yellow]")

    files_to_process = [f for f in all_files if f.name not in processed_files]
    
    if not files_to_process:
        console.print("[green]🎉 所有文件已处理完毕！[/green]")
        return

    console.print(f"[cyan]待处理: {len(files_to_process)} 个文件[/cyan]")

    # 4.5 v2.2 预扫描规划显示
    display_plan_summary(files_to_process, CHUNK_SIZE)

    # 5. 全局去重集合
    seen_hashes: Set[str] = set()

    # 6. 处理文件 (批量上传优化)
    total_extracted = 0
    total_uploaded = 0
    upload_buffer: List[Dict] = []  # 批量上传缓冲区

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console
    ) as progress:
        task_id = progress.add_task(
            f"[cyan]🚀 并发处理中 (Max {CONCURRENCY_LIMIT})...",
            total=len(files_to_process)
        )

        for file_path in files_to_process:
            filename, extracted, uploaded, pending_fields = await process_file(
                file_path, author, style, source_category,
                client, model_name, semaphore, seen_hashes, min_score, dry_run, console
            )
            
            total_extracted += extracted
            
            if not dry_run and pending_fields:
                upload_buffer.extend(pending_fields)
                
                # 达到批量大小则上传
                if len(upload_buffer) >= BATCH_SIZE:
                    batch_uploaded = await batch_upload_to_lark_async(upload_buffer, source_category)
                    total_uploaded += batch_uploaded
                    progress.console.print(f"  [blue]📤 批量上传: {batch_uploaded} 条[/blue]")
                    upload_buffer = []
            else:
                total_uploaded += uploaded
            
            # 记录进度
            processed_files.add(filename)
            save_checkpoint(processed_files)
            
            progress.console.print(
                f"  [green]✓[/green] {filename}: 提取 {extracted} → 待入库 {len(pending_fields) if not dry_run else uploaded}"
            )
            progress.advance(task_id, 1)

        # 上传剩余缓冲区
        if upload_buffer:
            batch_uploaded = await batch_upload_to_lark_async(upload_buffer, source_category)
            total_uploaded += batch_uploaded
            progress.console.print(f"  [blue]📤 最终批量上传: {batch_uploaded} 条[/blue]")

    console.print("")
    console.print(f"[bold green]🎉 完成![/bold green]")
    console.print(f"   📊 提取总数: {total_extracted}")
    console.print(f"   📤 入库总数: {total_uploaded}")
    console.print(f"   🔄 去重过滤: {total_extracted - total_uploaded} 条")

# ==========================================
# 9. CLI 入口
# ==========================================

@app.command()
def clean(
    input_path: str = typer.Option(..., "--input", "-i", help="输入路径 (单个 .txt 文件或文件夹)"),
    author: str = typer.Option(..., help="作者名 (用于去名化)"),
    style: str = typer.Option(..., help="风格标签 (mimeng/banfo/lianbushou 等)"),
    source_category: str = typer.Option("Shell", help="源类别: Shell (风格提取) 或 Kernel (事实清洗)"),
    provider: str = typer.Option("doubao", help="模型: doubao (默认), deepseek, gemini"),
    min_score: int = typer.Option(4, help="最低质量分 (1-5)"),
    dry_run: bool = typer.Option(False, help="仅测试，不上传到 Lark")
):
    """
    运行工业级数据清洗流水线 v2.0
    
    特性:
    - ⚡ 异步并发 (5-10x 速度提升)
    - 🛡️ 断点续传 (中断后可继续)
    - 📄 智能分片 (处理超长文件)
    - 🔄 MD5 去重 (避免重复入库)
    - 📂 智能识别 (支持单文件或文件夹)
    """
    asyncio.run(main_async(input_path, author, style, source_category, provider, min_score, dry_run))

@app.command()
def reset_checkpoint():
    """清除断点记录，重新开始处理"""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        console.print("[green]✅ 断点记录已清除[/green]")
    else:
        console.print("[yellow]没有断点记录[/yellow]")

@app.command()
def test_connection(
    provider: str = typer.Option("doubao", help="测试连接的模型提供商")
):
    """测试 LLM 连接"""
    console.print(f"[cyan]测试 {provider} 连接...[/cyan]")
    try:
        llm = AsyncLLMProvider(provider)
        client, model = llm.connect()
        console.print(f"[green]✅ 连接成功! Model: {model}[/green]")
    except Exception as e:
        console.print(f"[red]❌ 连接失败: {e}[/red]")

if __name__ == "__main__":
    app()
