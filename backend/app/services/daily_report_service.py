"""
P31/P34: 每日投研快报生成服务

编排完整流程（P34重构）：
    侦察官 → 策略官×N → enrichment → 质检官 → 总结官 → 推文写手 → 主推文 → 配图 → 回写

调用方式：
    POST /api/research/daily-report
    或定时任务直接调用 generate_daily_report()
"""
import os
import re
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..services.surf_service import SurfService
from ..agents.research.scout import _parse_projects_from_text
from ..core.llm import generate_text
from ..core.config import get_logger, cn_now

logger = get_logger("daily_report")

# 默认配置
DEFAULT_MODEL = "surf-1.5"
DEFAULT_CONCURRENCY = 6
REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "research"
PROMPTS_DIR = Path(__file__).parent.parent.parent / "data" / "prompts" / "research"


def _render_research_template(template_name: str, variables: dict) -> Optional[str]:
    """
    P32-C: 渲染投研 Jinja2 模板（P15 可编辑）。
    
    Args:
        template_name: 模板文件名，如 "analyst.jinja2" 或 "copywriter/tweet_digest.jinja2"
        variables: 模板变量字典
    
    Returns:
        渲染后的文本，失败返回 None
    """
    try:
        from jinja2 import Template
        path = PROMPTS_DIR / template_name
        if not path.exists():
            logger.warning(f"模板不存在: {path}")
            return None
        template_str = path.read_text(encoding="utf-8")
        template = Template(template_str)
        return template.render(**variables)
    except Exception as e:
        logger.warning(f"模板渲染失败 ({template_name}): {e}")
        return None


# ============================================================
#  Grok X Search: batch support for >10 accounts (P39)
# ============================================================

GROK_X_SEARCH_BATCH_SIZE = 10  # Grok API hard limit per x_search call


def _grok_batch_x_search(sources: list[dict]) -> dict:
    """
    P39: Grok x_search with automatic batching for >10 accounts.

    Grok's x_search tool allows at most 10 allowed_x_handles per call.
    This function splits the source list into batches, calls Grok serially
    for each batch, and merges results using _parse_projects_from_text()
    which handles dedup via its internal `seen` set.

    Args:
        sources: [{handle: "@xxx", desc: "..."}, ...]

    Returns:
        {"projects": list[dict], "raw_text": str, "elapsed": float}
    """
    import time as _time
    from datetime import timedelta

    t0 = _time.time()
    today = cn_now()
    today_str = today.strftime("%Y-%m-%d")
    two_days_ago = (today - timedelta(days=2)).strftime("%Y-%m-%d")

    # Split into batches of GROK_X_SEARCH_BATCH_SIZE
    all_handles = [s['handle'].replace('@', '').strip() for s in sources]
    batches = [
        all_handles[i:i + GROK_X_SEARCH_BATCH_SIZE]
        for i in range(0, len(all_handles), GROK_X_SEARCH_BATCH_SIZE)
    ]

    if len(batches) > 1:
        batch_sizes = "+".join(str(len(b)) for b in batches)
        logger.info(
            f"🔭 Grok batch x_search: {len(all_handles)} accounts "
            f"-> {len(batches)} batches ({batch_sizes})"
        )
    else:
        logger.info(f"🔭 Grok x_search: {len(all_handles)} accounts (single batch)")

    grok_system = (
        "你是加密货币投研侦察机器。你的唯一职责是将搜索到的数据转换为 Markdown 表格。\n"
        "请搜索用户指定的 Twitter/X 账号近 48 小时的推文。只要推文提到了任何 Crypto 实体、代币符号、积分任务、空投或项目名称，"
        "无论你认为其质量如何，都必须将其视为项目并收录。\n"
        "【绝对强制要求】：不准写任何废话！不准做质量主观评判！不准写\u201c目前未发现重点项目\u201d！\n"
        "只要你搜索到了任何上面提到的内容，你必须、绝对、强制输出一个完整的 Markdown 表格。\n"
        "如果有任何相关提到项目，不要写除此之外的说明。"
    )

    all_raw_texts = []
    batch_errors = []

    for batch_idx, batch_handles in enumerate(batches, 1):
        batch_label = f"batch {batch_idx}/{len(batches)}"
        logger.info(
            f"🔭 Grok {batch_label}: searching {', '.join(batch_handles)} "
            f"({len(batch_handles)} accounts)"
        )

        grok_tools = [{
            "type": "x_search",
            "allowed_x_handles": batch_handles,
            "from_date": two_days_ago,
            "to_date": today_str
        }]

        grok_prompt = (
            f"请搜索这些账号近48小时的内容: {', '.join(batch_handles)}\n"
            "提取其中提到的所有加密货币项目、代币符号、空投活动或积分任务。\n"
            "不用管是不是优质项目！全部放在这个格式的表格里：\n"
            "| 项目名称 | Twitter | 赛道 | KOL 关注数 | 代币 | 阶段 | 近期催化剂 |\n\n"
            "近期催化剂字段要求：必须包含具体日期！按以下优先级：\n"
            "第一优先: TGE、空投、代币上线、主网上线（如'3月23日TGE'）\n"
            "第二优先: 测试网、产品发布、Galxe/Zealy任务、快照、Binance Alpha\n"
            "第三优先: 积分系统、竞赛活动、NFT铸造、代币解锁\n\n"
            "所有表格内容必须用中文输出，项目名称和代币符号除外。近期催化剂务必用中文且带具体日期。"
        )

        try:
            grok_text = generate_text(
                prompt=grok_prompt,
                provider="grok",
                system_prompt=grok_system,
                temperature=0.8,
                max_tokens=4096,
                extra_body={
                    "search": True,
                    "tools": grok_tools
                },
            )
            logger.info(f"🔭 Grok {batch_label} raw output:\n{grok_text}")
            all_raw_texts.append(grok_text)
        except Exception as e:
            logger.error(f"🔭 Grok {batch_label} failed: {e}")
            batch_errors.append(f"{batch_label}: {e}")

    # Merge all batch outputs and parse + dedup
    elapsed = _time.time() - t0
    if not all_raw_texts:
        logger.error(f"🔭 Grok all {len(batches)} batches failed: {batch_errors}")
        return {"projects": [], "raw_text": "", "elapsed": elapsed}

    combined_text = "\n\n".join(all_raw_texts)
    projects = _parse_projects_from_text(combined_text)

    if batch_errors:
        logger.warning(
            f"🔭 Grok partial success: {len(all_raw_texts)}/{len(batches)} batches OK, "
            f"failures: {batch_errors}"
        )

    logger.info(
        f"🔭 Grok batch search done: {len(projects)} projects "
        f"from {len(all_raw_texts)} batches ({elapsed:.0f}s)"
    )
    return {
        "projects": projects,
        "raw_text": combined_text,
        "elapsed": elapsed,
    }


# ============================================================
#  Step 1: 侦察官 — 搜索热门项目
# ============================================================


def run_scout() -> dict:
    """
    调用 Surf API 搜索热门项目。
    
    P32-C: prompt 来自 scout.jinja2 模板（P15 可编辑），
    账号列表从 Google Sheets '侦察源' Tab 动态注入。

    Returns:
        {"projects": list[dict], "raw_text": str, "elapsed": float}
    """
    logger.info("🔭 侦察官：开始搜索...")

    # P32-C: 从 Sheets 读取信源账号
    try:
        from app.services.research_sheet import research_sheet_service
        sources = research_sheet_service.get_scout_sources()
    except Exception as e:
        logger.warning(f"读取 Sheets 信源失败，使用默认: {e}")
        sources = [
            {"handle": "@leakmealpha", "desc": "Crypto KOL Tracker"},
            {"handle": "@top7ico", "desc": "早期融资与 ICO"},
            {"handle": "@Eli5defi", "desc": "DeFi 科普与分析"},
            {"handle": "@Web3Alerts", "desc": "Web3 动态与预警"},
            {"handle": "@WY_mask", "desc": "中文投研与分析"},
        ]

    # 生成账号列表文本
    accounts_text = "\n".join(
        f"{i+1}. {s['handle']} — {s['desc']}"
        for i, s in enumerate(sources)
    )
    logger.info(f"🔭 侦察官信源: {len(sources)} 个账号")

    # P32-C: 渲染 scout.jinja2 模板（P15 可编辑）
    user_prompt = _render_research_template("scout.jinja2", {
        "accounts": accounts_text,
        "account_count": len(sources),
    })

    if not user_prompt:
        # fallback: 硬编码 prompt
        user_prompt = (
            f"检索以下 {len(sources)} 个 Twitter/X 账号近 2 天推文，找出热门 Crypto 项目：\n"
            f"{accounts_text}\n\n"
            "汇总去重后只输出一张表格：\n"
            "| 项目名称 | Twitter | 赛道 | KOL 关注数 | 代币 | 阶段 | 近期催化剂 |\n"
            "排除个人 KOL、交易所、媒体、纯 meme 币。最多 12 个。"
        )

    surf = SurfService()
    result = surf.call(
        model=DEFAULT_MODEL,
        user_prompt=user_prompt,
        abilities=["search"],
        reasoning="high",
    )

    # Surf 成功
    if result["status"] == 200:
        projects = _parse_projects_from_text(result["content"])
        logger.info(f"🔭 侦察官完成(Surf): 发现 {len(projects)} 个项目 ({result['elapsed']:.0f}s)")
        return {
            "projects": projects,
            "raw_text": result["content"],
            "elapsed": result.get("elapsed", 0),
    }

    # Surf 失败 → Grok 分批搜索 fallback (P39)
    error = result.get("error", "Unknown")[:200]
    logger.warning(f"🔭 Surf 失败({error})，尝试 Grok 分批搜索...")
    return _grok_batch_x_search(sources)



# ============================================================
#  Step 1.7: 6551 X 账号验证（P35 B3）
# ============================================================

def _verify_twitter_handle(handle: str) -> dict:
    """
    用 6551 API 验证单个 twitter handle。
    返回 {"valid": bool, "verified_handle": str, "display_name": str}
    """
    import httpx
    from dotenv import dotenv_values

    clean = handle.lstrip("@").strip()
    if not clean:
        return {"valid": False, "verified_handle": handle, "display_name": ""}

    # 从 .env 获取 token
    token = os.environ.get("TWITTER_TOKEN", "")
    if not token:
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            vals = dotenv_values(env_path)
            token = vals.get("TWITTER_TOKEN", "")

    if not token:
        logger.warning("[6551] TWITTER_TOKEN 未配置，跳过验证")
        return {"valid": True, "verified_handle": handle, "display_name": ""}

    try:
        resp = httpx.post(
            "https://ai.6551.io/open/twitter_user_info",
            json={"username": clean},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=10.0,
        )
        data = resp.json()

        if resp.status_code == 200 and data.get("data"):
            user_data = data["data"]
            verified = user_data.get("screen_name", clean)
            display = user_data.get("name", "")
            logger.info(f"[6551] ✅ @{clean} → @{verified} ({display})")
            return {
                "valid": True,
                "verified_handle": f"@{verified}",
                "display_name": display,
            }
        else:
            logger.warning(f"[6551] ❌ @{clean} 无效或未找到")
            return {"valid": False, "verified_handle": handle, "display_name": ""}
    except Exception as e:
        logger.warning(f"[6551] 验证失败 @{clean}: {e}")
        return {"valid": True, "verified_handle": handle, "display_name": ""}


def verify_project_handles(projects: list[dict]) -> list[dict]:
    """
    批量验证项目 twitter handle，修正错误 handle。
    """
    verified = 0
    corrected = 0
    for p in projects:
        tw = p.get("twitter", "")
        if not tw:
            continue
        result = _verify_twitter_handle(tw)
        if result["valid"]:
            if result["verified_handle"] != tw:
                logger.info(f"[6551] 修正: {tw} → {result['verified_handle']}")
                p["twitter"] = result["verified_handle"]
                corrected += 1
            verified += 1
        else:
            logger.warning(f"[6551] ⚠️ {p.get('name', '?')} 的 handle {tw} 无效，保留原值")

    logger.info(f"[6551] 验证完成: {verified}/{len(projects)} 有效, {corrected} 个修正")
    return projects


# ============================================================
#  Step 2: 策略官 — 逐个深度分析（并发控制）
# ============================================================

def _analyze_single_project(project: dict) -> dict:
    """
    对单个项目调用 Surf API 做深度分析

    Returns:
        {"name": str, "content": str, "elapsed": float, "error": str|None}
    """
    name = project.get("name", "Unknown")
    twitter = project.get("twitter", "")
    logger.info(f"🔬 策略官: 分析 {name} ({twitter})...")

    category = project.get("category", "")
    token = project.get("token", "未知")
    stage = project.get("stage", "未知")
    catalyst = project.get("catalyst", project.get("buzz", ""))

    # P32-C: 从 analyst.jinja2 模板渲染 prompt（P15 可编辑）
    user_prompt = _render_research_template("analyst.jinja2", {
        "name": name,
        "twitter": twitter,
        "category": category,
        "token": token,
        "stage": stage,
        "catalyst": catalyst,
    })

    if not user_prompt:
        # fallback: 硬编码 prompt
        user_prompt = (
            f"深度调研项目 {name} ({twitter})。\n"
            f"侦察线索: 赛道 {category}，代币 {token}，阶段 {stage}，催化剂 {catalyst}。\n\n"
            f"输出完整投研报告，包含以下板块，只写事实和数据：\n\n"
            f"## 📊 项目定位\n是什么、做什么、核心产品、目标市场。\n\n"
            f"## 💰 融资\n用表格列出每轮融资：\n| 时间 | 轮次 | 金额 | 领投方 |\n融资总额。\n\n"
            f"## 👥 团队\n核心成员（姓名/角色/背景）。\n\n"
            f"## 🪙 代币经济学\n代币符号、是否已发行、总供应量、分配比例、解锁计划。\n\n"
            f"## 📈 市场数据\n当前价格、市值、FDV、TVL、Twitter 粉丝数。\n\n"
            f"## 🔥 近期催化剂\n最近已发生 + 即将发生的关键事件，注明日期。\n\n"
            f"## 🏁 竞品对比\n同赛道 2-3 个竞品，简要对比定位和差异。\n\n"
            f"不要附带来源链接和 URL。没有数据的板块直接跳过。"
        )

    surf = SurfService()
    result = surf.call(
        model=DEFAULT_MODEL,
        user_prompt=user_prompt,
        abilities=["search"],
        reasoning="high",
        timeout=600,  # 深度分析耗时较长
    )

    # Surf 成功
    if result["status"] == 200:
        logger.info(f"🔬 策略官完成(Surf) ({name}): {result['elapsed']:.0f}s")
        return {
            "name": name,
            "twitter": twitter,
            "content": result["content"],
            "elapsed": result.get("elapsed", 0),
            "error": None,
        }

    # Surf 失败 → Grok fallback
    error = result.get("error", "Unknown")[:200]
    logger.warning(f"🔬 策略官 Surf 失败({name}): {error}，尝试 Grok fallback...")

    import time
    from datetime import timedelta
    t0 = time.time()
    today = cn_now()
    today_str = today.strftime("%Y-%m-%d")
    try:
        from app.core.llm import generate_text
        two_days_ago = (today - timedelta(days=2)).strftime("%Y-%m-%d")
        grok_system = (
            "你是加密货币投研策略官。\n"
            "请用实时搜索深度调研用户指定的项目，输出完整投研报告，只写事实和数据：\n\n"
            "## 项目定位\n是什么、做什么、核心产品、目标市场。\n\n"
            "## 融资\n用表格列出每轮融资：\n| 时间 | 轮次 | 金额 | 领投方 |\n融资总额。\n\n"
            "## 团队\n核心成员（姓名/角色/背景）。\n\n"
            "## 代币经济学\n代币符号、是否已发行、总供应量、分配比例、解锁计划。\n\n"
            "## 市场数据\n当前价格、市值、FDV、TVL、Twitter 粉丝数。\n\n"
            "## 近期催化剂\n最近已发生 + 即将发生的关键事件，注明日期。\n"
            "卡片催化剂: 从上述事件中选出对投资者最有参与价值的一条，格式「YYYY-MM-DD 一句话中文描述」。\n"
            "优先选择未来事件，其次近2天内已发生事件，超过2天的丢弃。\n"
            "第一优先: TGE、空投、代币上线、主网上线、白名单、大使计划、IDO/IEO/公售\n"
            "第二优先: 测试网、产品发布、功能上线、Galxe/Zealy任务、快照、生态合作\n"
            "第三优先: 积分系统、竞赛活动、NFT铸造、奖励计划、代币解锁\n"
            "如果找不到近期事件，输出「卡片催化剂: 无」。\n\n"
            "## 竞品对比\n同赛道 2-3 个竞品，简要对比定位和差异。\n\n"
            "【重要】所有内容必须用中文输出。项目名称和代币符号除外。"
            "卡片催化剂必须是中文且带具体日期。不要用英文写催化剂。"
            "不要附带来源链接和 URL。没有数据的板块直接跳过。"
        )
        grok_tools = [{
            "type": "x_search",
            "from_date": two_days_ago,
            "to_date": today_str
        }]

        grok_text = generate_text(
            prompt=user_prompt,
            provider="grok",
            system_prompt=grok_system,
            temperature=0.3,
            max_tokens=4096,
            extra_body={
                "search": True,
                "tools": grok_tools
            },
        )
        elapsed = time.time() - t0
        logger.info(f"🔬 策略官完成(Grok) ({name}): {elapsed:.0f}s")
        return {
            "name": name,
            "twitter": twitter,
            "content": grok_text,
            "elapsed": elapsed,
            "error": None,
        }
    except Exception as e:
        elapsed = time.time() - t0
        logger.error(f"🔬 策略官 Grok fallback 失败 ({name}): {e}")
        return {"name": name, "content": "", "elapsed": elapsed, "error": str(e)}


async def _analyze_with_semaphore(sem: asyncio.Semaphore, project: dict) -> dict:
    """带信号量控制的异步分析"""
    async with sem:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _analyze_single_project, project)


async def run_strategist_batch(projects: list[dict], concurrency: int = DEFAULT_CONCURRENCY) -> list[dict]:
    """
    并发分析多个项目

    Args:
        projects: 项目列表
        concurrency: 最大并发数

    Returns:
        list of {"name": str, "content": str, "elapsed": float, "error": str|None}
    """
    logger.info(f"🔬 策略官批量分析: {len(projects)} 个项目, 并发 {concurrency}")
    sem = asyncio.Semaphore(concurrency)
    tasks = [_analyze_with_semaphore(sem, p) for p in projects]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理异常
    processed = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            logger.error(f"策略官异常 ({projects[i].get('name', '?')}): {r}")
            processed.append({
                "name": projects[i].get("name", "Unknown"),
                "content": "",
                "elapsed": 0,
                "error": str(r),
            })
        else:
            processed.append(r)

    ok_count = sum(1 for r in processed if not r.get("error"))
    logger.info(f"🔬 策略官批量完成: {ok_count}/{len(projects)} 成功")
    return processed


# ============================================================
#  Step 3: 审核官 — 总结归纳
# ============================================================

def run_summarizer(analysis_results: list[dict], api_config: dict = None) -> str:
    """
    把 N 篇长报告总结归纳成精简版

    Args:
        analysis_results: 策略官的分析结果列表
        api_config: AI 配置 (provider, model_id)

    Returns:
        精简版文本
    """
    api_config = api_config or {}
    logger.info(f"📋 审核官: 总结归纳 {len(analysis_results)} 篇报告...")

    # 拼接所有成功的分析报告
    combined = []
    for r in analysis_results:
        if r.get("content"):
            combined.append(f"## {r['name']}\n\n{r['content']}")

    if not combined:
        logger.warning("📋 审核官: 无有效报告可总结")
        return ""

    all_reports = "\n\n---\n\n".join(combined)

    # P32-C: 从 summarizer.jinja2 模板渲染（P15 可编辑）
    system_prompt = _render_research_template("summarizer.jinja2", {})

    if not system_prompt:
        system_prompt = (
            "你是投研报告编辑。你的任务是将多篇详细的项目分析报告总结归纳成精简版本。\n\n"
            "每个项目保留以下 4 个板块（每项 100-200 字）：\n"
            "1. 📊 一句话定位\n2. 🎯 关键事件与参与机会\n"
            "3. 👥 团队与背书\n4. 🔥 近期催化剂\n\n"
            "去掉所有 URL、内部标记、冗长的方法论描述。"
        )

    user_prompt = f"请将以下 {len(combined)} 篇投研报告总结归纳成精简版：\n\n{all_reports}"

    provider = api_config.get("provider", "volcengine")
    model_id = api_config.get("model_id")

    try:
        result = generate_text(
            prompt=user_prompt,
            model_id=model_id,
            provider=provider,
            temperature=0.3,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        logger.info("📋 总结官完成")
        return result
    except Exception as e:
        logger.warning(f"📋 总结官 {provider} 失败: {e}，尝试 Grok fallback...")
        # P37: Grok fallback
        try:
            result = generate_text(
                prompt=user_prompt,
                provider="grok",
                temperature=0.3,
                system_prompt=system_prompt,
                max_tokens=4096,
            )
            logger.info("📋 总结官完成(Grok fallback)")
            return result
        except Exception as e2:
            logger.error(f"📋 总结官 Grok 也失败: {e2}")
            # 简单 fallback：截取每个报告前 500 字
            fallback = []
            for r in analysis_results:
                if r.get("content"):
                    fallback.append(f"## {r['name']}\n\n{r['content'][:500]}...")
            return "\n\n---\n\n".join(fallback)


# P34: run_writer() 已删除 — 日报由 report.jinja2 代码模板直接渲染


# ============================================================
#  Step 4.5: 从总结官+策略官报告中回填 summary + catalyst
# ============================================================

def _parse_summarizer_positions(summary_text: str) -> dict:
    """P37: 从总结官输出中解析每个项目的 ⚡ 卡片定位 和 ⚡ 卡片催化剂"""
    positions = {}
    if not summary_text:
        return positions
    
    # 按 ## 项目名 分块
    import re
    blocks = re.split(r"(?=^##\s)", summary_text, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block.startswith("##"):
            continue
        
        # 提取项目名
        name_match = re.match(r"##\s*(.+?)(?:\n|$)", block)
        if not name_match:
            continue
        name = name_match.group(1).strip().lower()
        
        data = {}
        
        # 提取 ⚡ 卡片定位
        pos_match = re.search(r"⚡\s*卡片定位[:：]\s*(.+?)(?:\n|$)", block)
        if pos_match:
            data["summary"] = pos_match.group(1).strip()[:40]
        
        # 提取 ⚡ 卡片催化剂
        cat_match = re.search(r"⚡\s*卡片催化剂[:：]\s*(.+?)(?:\n|$)", block)
        if cat_match:
            cat_text = cat_match.group(1).strip()
            if cat_text and cat_text not in ("无", "无。"):
                data["catalyst"] = cat_text
        
        if data:
            positions[name] = data
    
    logger.info(f"📋 总结官解析: 找到 {len(positions)} 个项目 "
                f"({sum(1 for d in positions.values() if 'summary' in d)} 定位, "
                f"{sum(1 for d in positions.values() if 'catalyst' in d)} 催化剂)")
    return positions


def _enrich_projects_from_analysis(
    projects: list[dict],
    analysis_results: list[dict],
    summary_text: str = "",
) -> list[dict]:
    """
    P37: 从总结官+策略官的报告中提取一句话定位和催化剂，回填到 projects 列表。

    summary 优先从总结官的 ⚡ 卡片定位 提取（≤20字精炼版），
    fallback 到策略官报告的 ## 项目定位 段落截取。
    catalyst 仍从策略官报告的 ⚡ 卡片催化剂 行提取。
    """
    import re

    # 建立 twitter → analysis_content 映射（P34: twitter handle 更可靠）
    analysis_map_tw = {}
    analysis_map_name = {}
    for r in analysis_results:
        if r.get("content"):
            tw = r.get("twitter", "").lower().strip().lstrip("@")
            if tw:
                analysis_map_tw[tw] = r["content"]
            analysis_map_name[r["name"].lower().strip()] = r["content"]

    # ---- 正则模式（兼容有无 emoji 前缀）----
    # Summary: ## 📊 项目定位 / ## 项目定位 / ## 1. 项目概要
    POS_PATTERN = re.compile(
        r"##\s*(?:📊\s*)?(?:项目定位|\d+\.\s*项目概要[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        re.DOTALL,
    )


    # P37: 解析总结官的卡片定位
    summarizer_positions = _parse_summarizer_positions(summary_text)

    # P37: KOL 信源账号集合（直接在 enrichment 清洗，不依赖 scout.py 模块缓存）
    _KOL_HANDLES = {
        "@leakmealpha", "@top7ico", "@eli5defi", "@web3alerts", "@wy_mask",
        "@rootdatacrypto", "@sanyi_eth_", "@kiemusddongao", "@basezh",
        "@airdroptrail", "@solana", "@base",
    }

    enriched = []
    for p in projects:
        p = dict(p)  # shallow copy

        # ---- P37: 清洗 Twitter handle（去除 KOL 信源账号） ----
        raw_tw = p.get("twitter", "")
        if raw_tw and "," in raw_tw:
            handles = [h.strip() for h in raw_tw.split(",") if h.strip()]
            non_kol = [h for h in handles if h.lower() not in _KOL_HANDLES]
            if non_kol:
                p["twitter"] = non_kol[0]
            else:
                # 全是 KOL → 用项目名
                clean_name = re.sub(r"\s+", "", p.get("name", "")).lower()
                p["twitter"] = f"@{clean_name}" if clean_name else ""
            logger.info(f"📋 enrichment [{p.get('name')}] twitter 清洗: '{raw_tw}' → '{p['twitter']}'")

        # ---- 保存侦察官催化剂（防止被策略官覆盖） ----
        _scout_catalyst = p.get("catalyst", "") or p.get("buzz", "")

        # 优先用 twitter handle 匹配，fallback 到 name
        tw_key = p.get("twitter", "").lower().strip().lstrip("@")
        name_key = p.get("name", "").lower().strip()
        content = analysis_map_tw.get(tw_key) or analysis_map_name.get(name_key, "")

        # P36: 模糊子串匹配（如 Anchorage → Anchorage Digital）
        if not content and name_key:
            for k, v in analysis_map_name.items():
                if name_key in k or k in name_key:
                    content = v
                    break

        match_by = "twitter" if tw_key in analysis_map_tw else ("name" if name_key in analysis_map_name else ("fuzzy" if content else "none"))
        logger.info(f"📋 enrichment [{p.get('name')}] match={match_by} tw={tw_key} content={'✅' if content else '❌'}")

        # ---------- P37: 提取一句话定位（优先总结官）----------
        summ_key = name_key
        summ_data = summarizer_positions.get(summ_key)
        # 模糊匹配：项目名可能不完全一致
        if not summ_data:
            for sk, sv in summarizer_positions.items():
                if summ_key in sk or sk in summ_key:
                    summ_data = sv
                    break

        # summary: 总结官 > 策略官 > 空
        if summ_data and summ_data.get("summary"):
            p["summary"] = summ_data["summary"]
            logger.info(f"📋 enrichment [{p.get('name')}] summary=总结官 '{summ_data['summary']}'")
        elif content:
            # Fallback: 从策略官报告截取
            pos_match = POS_PATTERN.search(content)
            if pos_match:
                text = pos_match.group(1).strip()
                lines = [
                    l.strip() for l in text.split("\n")
                    if l.strip()
                    and not l.strip().startswith("|")
                    and not l.strip().startswith("-")
                    and not l.strip().startswith("**")
                ]
                if lines:
                    lines = [
                        l for l in lines
                        if len(l) > 8
                        and "是什么" not in l
                        and "用表格" not in l
                    ]
                if lines:
                    raw = lines[0]
                    raw = re.sub(r"[（(]来源[：:].*?[）)]", "", raw).strip()
                    p["summary"] = raw[:40]
                    logger.info(f"📋 enrichment [{p.get('name')}] summary=策略官fallback")

        # ---------- P37: 催化剂提取（优先总结官 > 策略官 > 侦察官）----------
        # 总结官的催化剂是中文且带日期，不受前半段 API 影响
        def _clean_catalyst(val: str) -> str:
            """清理催化剂: 去除 ** markdown, 判断是否实质为空"""
            val = re.sub(r'\*\*', '', val).strip().rstrip("。.")
            # 过滤 "无" 的各种变体
            if not val or val in ("无", "暂无", "无。", "N/A", "n/a", "-", "—"):
                return ""
            return val

        if summ_data and summ_data.get("catalyst"):
            cleaned = _clean_catalyst(summ_data["catalyst"])
            if cleaned:
                p["catalyst"] = cleaned
                logger.info(f"📋 enrichment [{p.get('name')}] catalyst=总结官 '{cleaned}'")
        elif content:
            # Fallback: 从策略官的 ⚡ 卡片催化剂 提取
            card_cat_match = re.search(r"(?:⚡\s*)?卡片催化剂[:：]\s*(.+)", content)
            if card_cat_match:
                card_cat = _clean_catalyst(card_cat_match.group(1))
                if card_cat:
                    has_stale_date = bool(re.search(r"202[0-5]", card_cat))
                    if has_stale_date:
                        p["catalyst"] = _scout_catalyst
                        logger.warning(f"📋 enrichment [{p.get('name')}] 策略官催化剂含旧日期，恢复侦察官的: "
                                      f"策略官='{card_cat}' → 侦察官='{_scout_catalyst}'")
                    else:
                        card_cat = re.sub(r"2026-(\d{2})-(\d{2})", r"\1-\2", card_cat)
                        p["catalyst"] = card_cat.strip()
                        logger.info(f"📋 enrichment [{p.get('name')}] catalyst=策略官 '{p['catalyst']}'")

        # 最终兜底: 如果 catalyst 仍为空，用侦察官的 buzz 填充
        if not p.get("catalyst") and _scout_catalyst:
            p["catalyst"] = _clean_catalyst(_scout_catalyst) or _scout_catalyst
            logger.info(f"📋 enrichment [{p.get('name')}] catalyst=侦察官buzz '{p['catalyst']}'")

        # 最终安全网: 再次清理 ** 符号
        if p.get("catalyst"):
            p["catalyst"] = re.sub(r'\*\*', '', p["catalyst"]).strip()

        # P36: 无催化剂项目记录警告
        if not p.get("catalyst"):
            logger.warning(f"⚠️ [{p.get('name')}] 无催化剂")

        enriched.append(p)

    logger.info(
        f"📋 数据回填: {sum(1 for p in enriched if p.get('summary'))} 个 summary, "
        f"{sum(1 for p in enriched if p.get('catalyst'))} 个 catalyst"
    )
    return enriched


# ============================================================
#  Step 3.5: 质检官 — 检查配图数据
# ============================================================

def run_reviewer(projects: list[dict], api_config: dict = None) -> list[dict]:
    """
    P34: 质检官 — 用 LLM 检查 enrichment 提取的 catalyst/summary。
    修复截断、英文、主观预测等问题。
    """
    api_config = api_config or {}
    logger.info("🔍 质检官: 检查配图数据...")

    # 只检查有 catalyst 或 summary 的项目
    items = []
    for p in projects:
        cat = p.get("catalyst", "无")
        summ = p.get("summary", "无")
        if cat or summ:
            items.append(f"{p.get('name', '?')} | {cat or '无'} | {summ or '无'}")

    if not items:
        logger.info("🔍 质检官: 无数据需要检查")
        return projects

    system_prompt = _render_research_template("reviewer.jinja2", {})
    if not system_prompt:
        logger.warning("🔍 质检官: 模板不存在，跳过")
        return projects

    user_prompt = "\n".join(items)
    provider = api_config.get("provider", "volcengine")
    model_id = api_config.get("model_id")

    try:
        result = generate_text(
            prompt=user_prompt,
            model_id=model_id,
            provider=provider,
            temperature=0.2,
            system_prompt=system_prompt,
            max_tokens=2000,
        )

        # 解析质检结果，回写到 projects
        for line in result.strip().split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                continue
            name = parts[0]
            for p in projects:
                if p.get("name", "") == name:
                    new_cat = parts[1].strip()
                    new_summ = parts[2].strip()
                    # P35: 质检官只能改进催化文本，不能清空已有催化
                    if new_cat and new_cat not in ("无", "无。", ""):
                        p["catalyst"] = new_cat
                    # new_cat == "无" 时保留 enrichment 原值
                    if new_summ and new_summ not in ("无", "无。", ""):
                        p["summary"] = new_summ
                    break

        logger.info(f"🔍 质检官完成: 检查 {len(items)} 个项目")
    except Exception as e:
        logger.warning(f"🔍 质检官失败，使用原始数据: {e}")

    return projects


# ============================================================
#  Step 4: 配图生成
# ============================================================

def run_card_generator(projects: list[dict], date_str: str) -> str:
    """
    生成 1200×675 配图 HTML + PNG

    Returns:
        保存路径
    """
    logger.info("📸 配图: 生成中...")
    from ..services.card_generator import save_card, generate_card_image
    path = save_card(projects, date_str)
    logger.info(f"📸 配图 HTML 完成: {path}")

    # 确保 PNG 也被生成（save_card 中 Playwright 可能静默失败）
    png_path = path.replace(".html", ".png")
    import os
    if not os.path.exists(png_path):
        logger.warning("📸 PNG 不存在，尝试重新生成...")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
            generate_card_image(html, png_path)
            if os.path.exists(png_path):
                logger.info(f"📸 PNG 重新生成成功: {png_path}")
            else:
                logger.error("📸 PNG 重新生成仍然失败")
        except Exception as e:
            logger.error(f"📸 PNG 重新生成异常: {e}")
    else:
        logger.info(f"📸 PNG 已生成: {png_path}")

    return path


# ============================================================
#  Step 6: 推文文案
# ============================================================

def run_tweet_writer(
    summary: str,
    projects: list[dict],
    api_config: dict = None,
) -> list[dict]:
    """
    为每个项目生成一条独立的 Alpha 推文

    Returns:
        [{"name": project_name, "text": str, "char_count": int}, ...]
    """
    api_config = api_config or {}
    project_names = [p.get("name", "Unknown") for p in projects]
    logger.info(f"🐦 推文: 聚合 {len(projects)} 个项目生成 Alpha 速报...")

    from datetime import datetime, timedelta
    today = cn_now()
    date_30d_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    date_str_today = today.strftime("%m-%d")

    # P32-C: 从 tweet_digest.jinja2 模板渲染 system prompt（P15 可编辑）
    system_prompt = _render_research_template("copywriter/tweet_digest.jinja2", {
        "date_30d_ago": date_30d_ago,
    })

    if not system_prompt:
        # fallback: 硬编码 prompt
        system_prompt = (
            "你是 Web3 Alpha 猎手，负责写 X(Twitter) 推文。\n\n"
            "## 任务\n根据投研报告，为每个项目生成一条独立推文。\n\n"
            "## 推文格式（每个项目一条）\n"
            "```\n项目名称：项目名 @X账号\n\n"
            "一句话介绍项目定位和核心产品（1-2句）\n\n"
            "1/ 融资金额 — 领投方\n"
            "2/ 创始人/团队背景\n"
            "3/ 代币分配 或 空投信息\n"
            "4/ TVL | 交易量 | 价格 | 粉丝数等数据\n\n"
            "🔥 一条最强近期催化剂（口语化）\n```\n\n"
            "## 要求\n"
            f"- 催化剂只取 {date_30d_ago} 之后的事件，旧事件不要\n"
            "- 标题固定格式：「项目名称：名称 @X账号」，不加 emoji\n"
            "- 数据行用「1/ 2/ 3/ 4/」编号，保留所有有价值的信息\n"
            "- 融资、团队、代币、数据 按顺序排列，没数据的跳过\n"
            "- 催化剂只写 1 条最强的，口语化，不加(2026-02)格式日期\n"
            "- 不使用 💰👥🪙📈 等 emoji（只保留🔥）\n"
            "- 不写可信度评分、建议动作、投资建议\n"
            "- 不附带 URL 和来源链接\n"
            "- 金额用简写：$670万、$1.08亿\n"
            "- 粉丝数用简写：10.2万粉\n"
            "- 没有数据的行直接跳过\n"
        )

    user_prompt = (
        f"今日投研的 {len(projects)} 个项目：{', '.join(project_names)}\n\n"
        f"投研简报内容：\n{summary[:6000]}"
    )

    provider = api_config.get("provider", "volcengine")
    model_id = api_config.get("model_id")

    try:
        result = generate_text(
            prompt=user_prompt,
            model_id=model_id,
            provider=provider,
            temperature=0.7,
            system_prompt=system_prompt,
            max_tokens=6000,
        )
    except Exception as e:
        logger.warning(f"🐦 推文 {provider} 失败: {e}，尝试 Grok fallback...")
        try:
            result = generate_text(
                prompt=user_prompt,
                provider="grok",
                temperature=0.7,
                system_prompt=system_prompt,
                max_tokens=6000,
            )
        except Exception as e2:
            logger.error(f"🐦 推文 Grok 也失败: {e2}")
            return []

    # 解析: 按行首「项目名称：」分割为各项目推文（兼容旧版🔍格式）
    import re
    tweets = []

    # P35: 构建 name → twitter 映射（精确 + 模糊）
    handle_map = {}  # exact lower name → twitter
    for p in projects:
        pname = p.get("name", "").strip()
        tw = p.get("twitter", "")
        if pname:
            handle_map[pname.lower()] = tw

    def _find_twitter(tweet_name: str, tweet_text: str) -> str:
        """3 级匹配: 精确 → 包含 → 从文本提取 @handle"""
        key = tweet_name.lower()
        # 1) 精确匹配
        if key in handle_map:
            return handle_map[key]
        # 2) 包含匹配（项目名是对方子串，或对方是项目名子串）
        for pname, tw in handle_map.items():
            if pname in key or key in pname:
                return tw
        # 3) 从推文文本第一行提取 @handle
        at_match = re.search(r"@(\w+)", tweet_text[:200])
        if at_match:
            return f"@{at_match.group(1)}"
        return ""

    # 按行首「项目名称：」或「🔍」或「**项目名 @handle**」分割
    # 注意: 不能用 ^\*\*[^*] 因为会误匹配 **定位：** 等内部格式行
    blocks = re.split(r"(?=^项目名称：|^🔍|^\*\*(?!定位|团队|代币|催化|🔥|背书|融资|数据))", result.strip(), flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # 提取项目名（兼容 "项目名称：XX @yy"、"🔍 XX"、"**XX @yy**" 格式）
        name_match = re.match(r"(?:项目名称：|🔍)\s*(.+?)(?:\s*@|\n)", block)
        if not name_match:
            # 兼容 LLM 输出 **ProjectName @handle** 格式
            name_match = re.match(r"\*\*\s*(.+?)\s*(?:@|\*\*)", block)
        if not name_match:
            continue
        name = name_match.group(1).strip().strip('*').strip()
        # 跳过误匹配到的内部格式行
        if name in ("定位", "团队与背书", "代币信息", "催化剂", "🔥 催化剂", "融资", "数据"):
            continue
        # P34: 清理 LLM 输出的孤零零 # 和尾部空白
        clean_text = re.sub(r'\n\s*#\s*$', '', block.strip()).strip()
        # P36: 清理 LLM 常见杂质
        clean_text = re.sub(r'###\s*项目\d+.*', '', clean_text)           # ### 项目4
        clean_text = re.sub(r'[（(]注[：:].*?[）)]', '', clean_text)       # （注：...）
        clean_text = re.sub(r'\n---+\n?', '\n', clean_text)               # --- 分隔线
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()        # 多余空行
        # P35: 3 级匹配查找 twitter handle
        twitter = _find_twitter(name, clean_text)

        # P36: 将 @handle 注入推文文本（方便复制时带上X账号）
        if twitter and twitter not in clean_text:
            # 兼容 "项目名称：XX" 和 "**XX**" 两种格式
            if f"项目名称：{name}" in clean_text:
                clean_text = clean_text.replace(
                    f"项目名称：{name}",
                    f"项目名称：{name} {twitter}",
                    1
                )
            elif f"**{name}**" in clean_text:
                clean_text = clean_text.replace(
                    f"**{name}**",
                    f"**{name} {twitter}**",
                    1
                )
            elif f"**{name}" in clean_text:
                clean_text = clean_text.replace(
                    f"**{name}",
                    f"**{name} {twitter}",
                    1
                )

        # Bug fix: 去除 ** markdown 符号（前端不渲染 markdown）
        clean_text = re.sub(r'\*\*', '', clean_text).strip()
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()

        tweets.append({
            "name": name,
            "twitter": twitter,
            "text": clean_text,
            "char_count": len(clean_text),
        })

    # fallback: 如果解析失败，整段作为推文
    if not tweets:
        tweets.append({
            "name": "Alpha日报",
            "text": result,
            "char_count": len(result),
        })

    # P33: 固定标语 + LLM 悬念内容的聚合主推文（tweets[0]）
    # 前端 TweetCards.tsx 取 tweets[0] 作为主推文展示
    if len(tweets) >= 2:
        n = len(tweets)

        # 提取每个项目的核心亮点供 LLM 参考
        highlights = []
        for t in tweets:
            name = t.get("name", "?")
            snippet = t["text"][:150].replace("🔍", "").strip()
            highlights.append(f"- {name}: {snippet}")
        highlights_text = "\n".join(highlights)

        hook_prompt = (
            f"今日投研发现了 {n} 个项目，亮点如下：\n{highlights_text}\n\n"
            "请为每个项目写一句悬念式描述（不写项目名称），要求：\n"
            "1. 每行以'一个'或具体数据开头，制造好奇心\n"
            "2. 只陈述事实，不夸张，不用感叹号\n"
            "3. 每行不超过25个字\n"
            "4. 只输出描述行，不加任何标题、编号、解释\n"
        )

        try:
            body_text = generate_text(
                prompt=hook_prompt,
                provider="grok",  # P37: 主推文也用 Grok
                temperature=0.7,
                max_tokens=300,
            )
            body_text = body_text.strip().strip("`").strip()
            if body_text.startswith("```"):
                body_text = body_text.split("```")[1].strip()
            # 只保留非空行
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            body_text = "\n".join(lines[:n])  # 最多和项目数一样
            logger.info(f"🐦 主推文内容(LLM): {len(body_text)}字")

            # P36: 主推文最小长度检查（≥50字），不足用模板补充
            if len(body_text) < 50:
                logger.warning(f"🐦 主推文过短({len(body_text)}字 < 50字)，使用模板补充")
                names = " | ".join(t.get("name", "?") for t in tweets[:6])
                body_text = f"今日 {n} 个 Alpha 项目值得关注：\n{names}\n\n{body_text}"
        except Exception as e:
            logger.warning(f"🐦 主推文 LLM 失败，使用 fallback: {e}")
            names = " | ".join(t.get("name", "?") for t in tweets[:6])
            body_text = f"今日 {n} 个项目：{names}"

        # 组装：固定标语 + LLM内容 + 固定结尾
        hook_text = f"今日发现，值得细看\n\n{body_text}\n\n⬇️\n\n#AI #Alpha"

        main_tweet = {
            "name": "Alpha日报",
            "text": hook_text,
            "char_count": len(hook_text),
        }
        tweets.insert(0, main_tweet)
        logger.info(f"🐦 主推文: {main_tweet['char_count']}字, 含 {n} 个项目")

    logger.info(f"🐦 推文完成: {len(tweets)} 条（含主推文）")
    return tweets


def _save_tweets(tweets: list[dict], date_str: str) -> str:
    """保存推文到文件（P36: 同时保存 JSON 保留所有字段）"""
    _ensure_dirs()
    # 保留 md 用于人工查看
    path = REPORTS_DIR / f"tweets_{date_str}.md"
    content = f"# 🐦 推文文案 — {date_str}\n\n"
    for t in tweets:
        content += f"## {t['name']}\n\n```\n{t['text']}\n```\n\n"
    path.write_text(content, encoding="utf-8")

    # P36: 保存 JSON（保留 twitter/char_count 等所有字段）
    import json
    json_path = REPORTS_DIR / f"tweets_{date_str}.json"
    json_path.write_text(json.dumps(tweets, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"📁 保存: {path} + {json_path}")
    return str(path)



# ============================================================
#  文件保存
# ============================================================

def _ensure_dirs():
    """确保报告目录存在"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "projects").mkdir(exist_ok=True)


def _save_scout_report(projects: list[dict], raw_text: str, date_str: str) -> str:
    """保存侦察官结果"""
    _ensure_dirs()
    path = REPORTS_DIR / f"scout_{date_str}.md"
    content = f"# 🔭 侦察官搜索结果 — {date_str}\n\n"
    content += f"发现 {len(projects)} 个项目\n\n"
    content += "| 项目 | Twitter | KOL | 热度 |\n|------|---------|-----|------|\n"
    for p in projects:
        content += f"| {p.get('name','')} | {p.get('twitter','')} | +{p.get('kol_24h',0)} | {p.get('buzz','')[:50]} |\n"
    content += f"\n---\n\n## 原始数据\n\n{raw_text}"
    path.write_text(content, encoding="utf-8")
    logger.info(f"📁 保存: {path}")
    return str(path)


def _save_project_report(name: str, content: str, date_str: str, twitter: str = "") -> str:
    """保存单项目完整报告（用 twitter handle 去重）"""
    _ensure_dirs()
    # 优先用 twitter handle 作为文件名（唯一标识，避免重复）
    if twitter:
        file_key = twitter.lstrip("@").replace(" ", "_").replace("/", "_")
    else:
        file_key = name.replace(" ", "_").replace("/", "_")
    path = REPORTS_DIR / "projects" / f"{file_key}_{date_str}.md"
    full = f"# 🔬 {name} — 投研报告\n\n> 生成时间: {date_str}\n\n{content}"
    path.write_text(full, encoding="utf-8")
    logger.info(f"📁 保存: {path}")
    return str(path)


def _save_daily_report(report: str, date_str: str) -> str:
    """保存日报"""
    _ensure_dirs()
    path = REPORTS_DIR / f"daily_research_{date_str}.md"
    path.write_text(report, encoding="utf-8")
    logger.info(f"📁 保存: {path}")
    return str(path)


# ============================================================
#  P35: 从磁盘加载已有策略官报告
# ============================================================

def load_analysis_from_disk(date_str: str, twitters: list[str] = None, names: list[str] = None) -> tuple[list[dict], list[dict]]:
    """
    从 reports/research/projects/ 目录加载已有的策略官报告。
    用于重新组装日报时跳过侦察+策略(省 Surf API)。

    Args:
        date_str: 日期字符串, 如 "20260309"
        twitters: 可选, 只加载指定 twitter handle 的报告
        names: 可选, 只加载指定项目名的报告（twitter 为空时的 fallback）

    Returns:
        (projects, analysis_results) — 与 generate_daily_report 兼容的格式
    """
    projects_dir = REPORTS_DIR / "projects"
    if not projects_dir.exists():
        return [], []

    projects = []
    analysis_results = []

    # P36: 有指定项目时，搜索所有日期的报告（支持跨日期重组）
    if twitters or names:
        files = list(projects_dir.glob("*.md"))
        logger.info(f"[load_disk] 跨日期搜索: {len(files)} 个文件")
    else:
        # 无指定项目时，只搜索当天（或最近日期）
        pattern = f"*_{date_str}.md"
        files = list(projects_dir.glob(pattern))

        # P36: 今天没文件时，自动查找最近有数据的日期
        if not files:
            import re as _re
            all_files = list(projects_dir.glob("*.md"))
            dates_found = set()
            for f in all_files:
                m = _re.search(r"(\d{8})\.md$", f.name)
                if m:
                    dates_found.add(m.group(1))
            if dates_found:
                latest_date = sorted(dates_found, reverse=True)[0]
                logger.info(f"[load_disk] {date_str} 无数据，自动切换到最近日期 {latest_date}")
                date_str = latest_date
                files = list(projects_dir.glob(f"*_{date_str}.md"))

    if not files:
        logger.warning(f"[load_disk] 未找到任何报告文件")
        return [], []

    # P36: 按文件名倒序（最新报告优先），跨日期去重
    files = sorted(files, key=lambda f: f.name, reverse=True)
    seen_handles = set()

    for fpath in files:
        content = fpath.read_text(encoding="utf-8")

        # 从文件名提取 twitter handle: {handle}_{date}.md
        fname = fpath.stem  # e.g. "reya_xyz_20260309"
        # P36: 用正则剥离日期后缀（支持跨日期）
        handle = re.sub(r"_\d{8}$", "", fname)

        # P36: 跨日期去重（文件已按日期倒序，第一次出现即最新）
        if handle.lower() in seen_handles:
            continue
        seen_handles.add(handle.lower())

        # 从报告内容提取项目名 (第一行 "# 🔬 Name — 投研报告")
        name = handle  # fallback
        first_line = content.split("\n")[0] if content else ""
        if "—" in first_line:
            name = first_line.split("🔬")[-1].split("—")[0].strip()
        elif "-" in first_line:
            name = first_line.split("🔬")[-1].split("-")[0].strip()

        twitter = f"@{handle}"

        # 按 twitter 或 name 过滤
        if twitters or names:
            matched = False
            if twitters:
                normalized_tw = {t.lstrip("@").lower().replace(" ", "_") for t in twitters}
                if handle.lower() in normalized_tw:
                    matched = True
            if not matched and names:
                normalized_names = {n.lower().strip() for n in names}
                if name.lower().strip() in normalized_names:
                    matched = True
            if not matched:
                continue

        # 提取正文（跳过标题和元信息行）
        lines = content.split("\n")
        body_lines = []
        for line in lines:
            if line.startswith("# 🔬") or line.startswith("> 生成时间"):
                continue
            body_lines.append(line)
        body = "\n".join(body_lines).strip()

        # 从报告提取赛道
        category = ""
        for line in lines:
            if "赛道" in line or "Track" in line:
                category = line.split(":")[-1].strip() if ":" in line else ""
                break

        projects.append({
            "name": name,
            "twitter": twitter,
            "category": category,
        })

        analysis_results.append({
            "name": name,
            "twitter": twitter,
            "content": body,
        })

    logger.info(f"[load_disk] 从磁盘加载 {len(projects)} 个项目报告 ({date_str})")
    return projects, analysis_results


def get_available_projects(date_str: str = None) -> list[dict]:
    """
    获取指定日期已分析的项目列表（供前端重新组装选择用）

    Returns:
        [{"name": str, "twitter": str, "file": str, "date": str}]
    """
    if not date_str:
        date_str = cn_now().strftime("%Y%m%d")

    projects_dir = REPORTS_DIR / "projects"
    if not projects_dir.exists():
        return []

    pattern = f"*_{date_str}.md"
    files = list(projects_dir.glob(pattern))

    result = []
    for fpath in files:
        fname = fpath.stem
        handle = fname.replace(f"_{date_str}", "")
        # 读第一行取项目名
        first_line = fpath.read_text(encoding="utf-8").split("\n")[0]
        name = handle
        if "🔬" in first_line and "—" in first_line:
            name = first_line.split("🔬")[-1].split("—")[0].strip()

        result.append({
            "name": name,
            "twitter": f"@{handle}",
            "file": str(fpath),
            "date": date_str,
        })

    return result


# ============================================================
#  P35: 后半段管线（enrichment → 日报）
# ============================================================

async def _run_post_analysis_pipeline(
    projects: list[dict],
    analysis_results: list[dict],
    api_config: dict,
    date_str: str,
    _progress,
    skip_sheets_writeback: bool = False,
) -> dict:
    """
    后半段管线: enrichment → 总结 → 推文 → 配图 → 质检(终检) → 日报渲染 → Sheets回写

    Args:
        projects: 项目基础信息列表
        analysis_results: 策略官分析结果列表
        api_config: AI 配置
        date_str: 日期字符串
        _progress: 进度回调
        skip_sheets_writeback: 重新组装时跳过 Sheets 回写

    Returns:
        {"report_path", "card_path", "tweets_path", "report_content", "tweets"}
    """
    # ===== P37: 总结官先跑（生成精炼定位） =====
    _progress("summarizer", "总结归纳分析报告...")
    summary = run_summarizer(analysis_results, api_config)

    # ===== enrichment — 从总结官+策略官回填 summary + catalyst =====
    _progress("enrich", "提取项目定位与催化剂...")
    enriched_projects = _enrich_projects_from_analysis(projects, analysis_results, summary)

    # ===== 推文文案 =====
    _progress("tweets", "生成推文文案...")
    card_projects = enriched_projects[:6]
    tweets = run_tweet_writer(summary, card_projects, api_config)
    tweets_path = ""
    if tweets:
        tweets_path = _save_tweets(tweets, date_str)

    # ===== 配图生成 =====
    _progress("card", "生成配图...")
    card_path = run_card_generator(enriched_projects, date_str)

    # ===== P36: 质检官移到最后（终检最终产物） =====
    _progress("reviewer", "质检终检...")
    enriched_projects = run_reviewer(enriched_projects, api_config)

    # ===== 日报渲染（代码模板，不用 LLM） =====
    _progress("report", "渲染日报...")
    report_projects = []
    for p_item in projects:
        rp = dict(p_item)
        for r in analysis_results:
            if r.get("twitter") == p_item.get("twitter") and r.get("content"):
                clean_analysis = re.sub(
                    r"###\s*Reasoning Process.*?(?=\n##|\Z)",
                    "", r["content"], flags=re.DOTALL
                ).strip()
                rp["analysis"] = clean_analysis
                break
        else:
            rp["analysis"] = ""
        report_projects.append(rp)

    try:
        from jinja2 import Template
        template_path = PROMPTS_DIR / "copywriter" / "report.jinja2"
        template_text = template_path.read_text(encoding="utf-8")
        template_lines = [l for l in template_text.split("\n") if not l.strip().startswith("{#")]
        template_clean = "\n".join(template_lines)
        tmpl = Template(template_clean)
        final_report = tmpl.render(
            date=date_str,
            display_time=cn_now().strftime("%Y-%m-%d %H:%M"),
            projects=report_projects,
        )
    except Exception as e:
        logger.warning(f"report.jinja2 渲染失败，使用 fallback: {e}")
        final_report = (
            f"# 每日投研快报\n\n"
            f"> 日期: {date_str}\n\n"
            f"{summary}"
        )

    # 保存日报
    report_path = _save_daily_report(final_report, date_str)

    # ===== Sheets 回写 =====
    if not skip_sheets_writeback:
        try:
            from app.services.research_sheet import research_sheet_service
            _progress("writeback", "回写分析记录到 Sheets...")
            research_sheet_service.write_analysis_records(enriched_projects, date_str)
            _progress("writeback", f"回写 {len(enriched_projects)} 条记录完成")
        except Exception as e:
            logger.warning(f"Sheets 回写跳过: {e}")

    return {
        "report_path": report_path,
        "card_path": card_path,
        "tweets_path": tweets_path,
        "report_content": final_report,
        "tweets": tweets,
        "enriched_projects": enriched_projects,
    }


# ============================================================
#  主入口
# ============================================================

async def generate_daily_report(
    api_config: dict = None,
    concurrency: int = DEFAULT_CONCURRENCY,
    selected_projects: list[str] = None,
    scout_projects: list[dict] = None,
    progress_callback=None,
) -> dict:
    """
    生成每日投研快报 — 完整流程

    Args:
        api_config: AI 配置 {"provider": str, "model_id": str}
        concurrency: 策略官并发数（默认 3）
        progress_callback: 进度回调 (step: str, detail: str) -> None

    Returns:
        {
            "status": "success" | "error",
            "projects_count": int,
            "report_path": str,
            "project_paths": list[str],
            "report_content": str,
            "elapsed": float,
            "error": str | None,
        }
    """
    api_config = api_config or {}
    start_time = time.time()
    date_str = cn_now().strftime("%Y%m%d")

    def _progress(step: str, detail: str):
        logger.info(f"[{step}] {detail}")
        if progress_callback:
            progress_callback(step, detail)

    try:
        # ===== Step 1: 侦察官 =====
        if scout_projects:
            # 前端已提供侦察结果，跳过重新搜索（避免 Surf API 返回不同结果）
            _progress("scout", f"使用前端提供的 {len(scout_projects)} 个侦察结果，跳过重新搜索")
            projects = scout_projects
            _save_scout_report(projects, "(已由前端提供)", date_str)
        else:
            _progress("scout", "开始搜索热门项目...")
            scout_result = run_scout()
            projects = scout_result["projects"]

            if not projects:
                return {
                    "status": "error",
                    "projects_count": 0,
                    "report_path": "",
                    "project_paths": [],
                    "report_content": "",
                    "elapsed": time.time() - start_time,
                    "error": "侦察官未发现任何项目",
                }

            _progress("scout", f"发现 {len(projects)} 个项目")
            _save_scout_report(projects, scout_result["raw_text"], date_str)

        # ===== Step 1.5: 去重过滤（P32-B） =====
        try:
            from app.services.research_sheet import research_sheet_service
            _progress("dedup", f"去重过滤 {len(projects)} 个项目...")
            original_count = len(projects)
            projects = research_sheet_service.dedup_filter(projects)
            skipped = original_count - len(projects)
            if skipped > 0:
                _progress("dedup", f"去重: {len(projects)} 保留, {skipped} 跳过")
            else:
                _progress("dedup", f"去重: 全部 {len(projects)} 个保留（均为新项目）")
        except Exception as e:
            logger.warning(f"去重过滤跳过（Sheets 不可用）: {e}")

        # ===== Step 1.55: 48h ChromaDB 去重（P35 F2） =====
        if not selected_projects:  # 仅自动模式，用户手动选择不过滤
            try:
                from app.services.chroma_service import get_chroma_service
                chroma = get_chroma_service()
                recent_handles = chroma.get_recent_reports(hours=48)
                if recent_handles:
                    before = len(projects)
                    projects = [
                        p for p in projects
                        if p.get("twitter", "").lower().lstrip("@") not in recent_handles
                        or p.get("twitter", "").lower().lstrip("@") in ("", "-")
                    ]
                    skipped_48h = before - len(projects)
                    if skipped_48h > 0:
                        _progress("dedup", f"⚠️ 48h去重: 跳过 {skipped_48h} 个已分析项目")
                        logger.info(f"[48h dedup] {skipped_48h} 个项目已在近48h分析，跳过")
            except Exception as e:
                logger.warning(f"48h ChromaDB 去重跳过: {e}")

        # ===== Step 1.6: 用户手动筛选 =====
        if selected_projects:
            selected_set = {n.lower() for n in selected_projects}
            # 保留侦察中被选中的项目
            scouted_names = {p.get("name", "").lower() for p in projects}
            projects = [p for p in projects if p.get("name", "").lower() in selected_set]

            # 补充历史项目（用户选了但侦察官没搜到的）
            missing = selected_set - {p.get("name", "").lower() for p in projects}
            if missing:
                try:
                    from app.services.research_sheet import research_sheet_service
                    records = research_sheet_service.get_all_records(use_cache=False)
                    for r in records:
                        rname = r.get("项目名", "").strip()
                        if rname.lower() in missing:
                            projects.append({
                                "name": rname,
                                "twitter": r.get("Twitter", ""),
                                "category": r.get("赛道", ""),
                                "buzz": r.get("催化剂摘要", ""),
                            })
                            _progress("filter", f"补充历史项目: {rname}")
                except Exception as e:
                    logger.warning(f"补充历史项目失败: {e}")

            _progress("filter", f"用户选择: {len(projects)} 个项目")

        if not projects:
            return {
                "status": "error",
                "projects_count": 0,
                "report_path": "",
                "project_paths": [],
                "report_content": "",
                "elapsed": time.time() - start_time,
                "error": "筛选后无剩余项目",
            }

        # ===== Step 1.8: 6551 X 账号验证（P35 B3） =====
        try:
            _progress("verify", f"验证 {len(projects)} 个 X 账号...")
            projects = verify_project_handles(projects)
            _progress("verify", "X 账号验证完成")
        except Exception as e:
            logger.warning(f"6551 验证跳过: {e}")

        # ===== Step 2: 策略官（并发 N） =====
        _progress("strategist", f"开始分析 {len(projects)} 个项目（并发 {concurrency}）...")
        analysis_results = await run_strategist_batch(projects, concurrency)

        # 保存每个项目的完整报告
        project_paths = []
        for r in analysis_results:
            if r.get("content"):
                path = _save_project_report(r["name"], r["content"], date_str, r.get("twitter", ""))
                project_paths.append(path)
                # P35 F2: 同时入库 ChromaDB
                try:
                    from app.services.chroma_service import get_chroma_service
                    get_chroma_service().add_research_report(
                        twitter=r.get("twitter", r["name"]),
                        date=date_str,
                        name=r["name"],
                        content=r["content"],
                    )
                except Exception as e:
                    logger.warning(f"[Chroma] 入库失败 {r['name']}: {e}")

        ok_count = sum(1 for r in analysis_results if not r.get("error"))
        _progress("strategist", f"{ok_count}/{len(projects)} 个项目分析完成")

        if ok_count == 0:
            return {
                "status": "error",
                "projects_count": len(projects),
                "report_path": "",
                "project_paths": project_paths,
                "report_content": "",
                "elapsed": time.time() - start_time,
                "error": "所有项目分析均失败",
            }

        # ===== Step 3-7: 后半段管线（P35 抽取） =====
        pipeline_result = await _run_post_analysis_pipeline(
            projects=projects,
            analysis_results=analysis_results,
            api_config=api_config,
            date_str=date_str,
            _progress=_progress,
        )

        elapsed = time.time() - start_time
        _progress("done", f"日报生成完成！{ok_count} 个项目, {elapsed:.0f}s")

        return {
            "status": "success",
            "date": date_str,
            "projects_count": ok_count,
            "report_path": pipeline_result["report_path"],
            "card_path": pipeline_result["card_path"],
            "tweets_path": pipeline_result["tweets_path"],
            "project_paths": project_paths,
            "report_content": pipeline_result["report_content"],
            "tweets": pipeline_result["tweets"],
            "elapsed": elapsed,
            "error": None,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"日报生成失败: {e}")
        return {
            "status": "error",
            "projects_count": 0,
            "report_path": "",
            "project_paths": [],
            "report_content": "",
            "elapsed": elapsed,
            "error": str(e),
        }
