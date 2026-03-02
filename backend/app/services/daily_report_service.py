"""
P31: 每日投研快报生成服务

编排完整流程：
    侦察官 → 策略官×N（并发3）→ 审核官 → 写手 → 配图 → 推文 → 润色官

调用方式：
    POST /api/research/daily-report
    或定时任务直接调用 generate_daily_report()
"""
import os
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..services.surf_service import SurfService
from ..agents.research.scout import _parse_projects_from_text
from ..core.llm import generate_text
from ..core.config import get_logger

logger = get_logger("daily_report")

# 默认配置
DEFAULT_MODEL = "surf-1.5"
DEFAULT_CONCURRENCY = 3
REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "research"


# ============================================================
#  Step 1: 侦察官 — 搜索热门项目
# ============================================================

def run_scout() -> dict:
    """
    调用 Surf API 搜索 leak.me 热门项目

    Returns:
        {"projects": list[dict], "raw_text": str, "elapsed": float}
    """
    logger.info("🔭 侦察官：开始搜索...")

    user_prompt = (
        "检索 @leakmealpha 近 7 天推文 + 访问 leak.me 网站 trending。\n"
        "leak.me 是 Crypto KOL Tracker，追踪加密 KOL 的新关注行为。\n"
        "只输出一张表格，不要写任何分析或说明：\n"
        "| 项目名称 | Twitter | 赛道 | KOL 关注数 | 代币 | 阶段 | 近期催化剂 |\n"
        "字段说明：\n"
        "- 赛道: DeFi/L2/AI/GameFi/RWA/Infra 等\n"
        "- 代币: 代币符号（如 $NEAR）或 无\n"
        "- 阶段: 预发布/测试网/已上线/TGE前\n"
        "- 近期催化剂: 一句话（融资/空投/TGE/上线/合作）\n"
        "排除个人 KOL、交易所、媒体、纯 meme 币。最多 8 个。"
    )

    surf = SurfService()
    result = surf.call(
        model=DEFAULT_MODEL,
        user_prompt=user_prompt,
        abilities=["search"],
        reasoning="high",
    )

    if result["status"] != 200:
        error = result.get("error", "Unknown")[:200]
        logger.error(f"🔭 侦察官失败: {error}")
        return {"projects": [], "raw_text": "", "elapsed": result.get("elapsed", 0)}

    projects = _parse_projects_from_text(result["content"])
    logger.info(f"🔭 侦察官完成: 发现 {len(projects)} 个项目 ({result['elapsed']:.0f}s)")

    return {
        "projects": projects,
        "raw_text": result["content"],
        "elapsed": result.get("elapsed", 0),
    }


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

    user_prompt = (
        f"深度调研项目 {name} ({twitter})。\n"
        f"侦察线索: 赛道 {category}，代币 {token}，阶段 {stage}，催化剂 {catalyst}。\n\n"
        f"输出完整投研报告，包含以下板块，只写事实和数据：\n\n"
        f"## 📊 项目定位\n"
        f"是什么、做什么、核心产品、目标市场。\n\n"
        f"## 💰 融资\n"
        f"用表格列出每轮融资：\n"
        f"| 时间 | 轮次 | 金额 | 领投方 |\n"
        f"融资总额。\n\n"
        f"## 👥 团队\n"
        f"核心成员（姓名/角色/背景）。\n\n"
        f"## 🪙 代币经济学\n"
        f"代币符号、是否已发行、总供应量、分配比例、解锁计划。\n\n"
        f"## 📈 市场数据\n"
        f"当前价格、市值、FDV、TVL、Twitter 粉丝数。\n\n"
        f"## 🔥 近期催化剂\n"
        f"最近已发生 + 即将发生的关键事件（TGE/空投/主网/上所/产品发布/合作），注明日期。\n\n"
        f"## 🏁 竞品对比\n"
        f"同赛道 2-3 个竞品，简要对比定位和差异。\n\n"
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

    if result["status"] != 200:
        error = result.get("error", "Unknown")[:200]
        logger.error(f"🔬 策略官失败 ({name}): {error}")
        return {"name": name, "content": "", "elapsed": result.get("elapsed", 0), "error": error}

    logger.info(f"🔬 策略官完成 ({name}): {result['elapsed']:.0f}s")
    return {
        "name": name,
        "twitter": twitter,
        "content": result["content"],
        "elapsed": result.get("elapsed", 0),
        "error": None,
    }


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

    system_prompt = (
        "你是投研报告编辑。你的任务是将多篇详细的项目分析报告总结归纳成精简版本。\n\n"
        "每个项目保留以下 4 个板块（每项 100-200 字）：\n"
        "1. 📊 一句话定位\n"
        "2. 🎯 关键事件与参与机会（时间窗口 + 参与方式）\n"
        "3. 👥 团队与背书（核心成员 + 可信度）\n"
        "4. 🔥 近期催化剂（具体事件 + 影响）\n\n"
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
        logger.info("📋 审核官完成")
        return result
    except Exception as e:
        logger.error(f"📋 审核官失败: {e}")
        # 简单 fallback：截取每个报告前 500 字
        fallback = []
        for r in analysis_results:
            if r.get("content"):
                fallback.append(f"## {r['name']}\n\n{r['content'][:500]}...")
        return "\n\n---\n\n".join(fallback)


# ============================================================
#  Step 4: 写手 — 组装日报
# ============================================================

def run_writer(
    summary: str,
    projects: list[dict],
    date_str: str,
    api_config: dict = None,
) -> str:
    """
    把精简版内容组装成一份日报

    Args:
        summary: 审核官输出的精简版
        projects: 侦察官发现的项目列表（含基本信息）
        date_str: 日期字符串
        api_config: AI 配置

    Returns:
        日报 Markdown 文本
    """
    api_config = api_config or {}
    logger.info("✍️ 写手: 组装日报...")

    # 构建项目总览表
    overview_rows = []
    for i, p in enumerate(projects, 1):
        name = p.get("name", "?")
        twitter = p.get("twitter", "")
        category = p.get("category", "")
        kol = p.get("kol_24h", 0)
        buzz = p.get("buzz", "")[:50]
        overview_rows.append(f"| {i} | **{name}** ({twitter}) | {category} | +{kol} | {buzz} |")

    overview_table = (
        "| # | 项目 | 类别 | 24h KOL | 热度原因 |\n"
        "|---|------|------|---------|----------|\n"
        + "\n".join(overview_rows)
    )

    system_prompt = (
        "你是投研日报写手。将项目总览和精简分析组装成一份结构清晰的每日投研快报。\n\n"
        "日报格式要求：\n"
        "1. 标题：# 🌊 每日投研快报\n"
        "2. 元信息（日期、项目数）\n"
        "3. 📋 项目总览表格\n"
        "4. 每个项目的分析，严格只保留以下 4 个板块：\n"
        "   - ## 📊 一句话定位\n"
        "   - ## 🎯 关键事件与参与机会\n"
        "   - ## 👥 团队与背书\n"
        "   - ## 🔥 近期催化剂\n"
        "5. 没有数据的板块直接省略，不要写「暂无」\n"
        "6. 每个板块 2-4 句话，语言简洁专业\n"
        "7. 末尾加免责声明\n\n"
        "直接输出 Markdown 格式日报，不要添加任何说明。"
    )

    user_prompt = (
        f"请组装以下内容为每日投研快报：\n\n"
        f"日期: {date_str}\n\n"
        f"项目总览:\n{overview_table}\n\n"
        f"精简分析:\n{summary}"
    )

    provider = api_config.get("provider", "volcengine")
    model_id = api_config.get("model_id")

    try:
        result = generate_text(
            prompt=user_prompt,
            model_id=model_id,
            provider=provider,
            temperature=0.5,
            system_prompt=system_prompt,
            max_tokens=6000,
        )
        logger.info("✍️ 写手完成")
        return result
    except Exception as e:
        logger.error(f"✍️ 写手失败: {e}")
        # fallback: 手动拼日报
        return (
            f"# 🌊 每日投研快报\n\n"
            f"> 日期: {date_str} | 数据来源: leak.me\n\n"
            f"## 项目总览\n\n{overview_table}\n\n"
            f"## 分析\n\n{summary}"
        )


# ============================================================
#  Step 4.5: 从策略官报告中回填 summary + catalyst
# ============================================================

def _enrich_projects_from_analysis(
    projects: list[dict],
    analysis_results: list[dict],
) -> list[dict]:
    """
    从策略官的深度报告中提取一句话定位和催化剂，回填到 projects 列表。

    用于 Step 5 (配图) 和 Step 6 (推文) 的数据输入。
    兼容新旧两种报告格式。
    """
    import re
    from .card_generator import pick_best_catalyst

    # 建立 name → analysis_content 映射
    analysis_map = {}
    for r in analysis_results:
        if r.get("content"):
            analysis_map[r["name"].lower().strip()] = r["content"]

    # 兼容新旧格式的 section 正则
    # 新格式: ## 📊 项目定位    旧格式: ## 1. 项目概要
    POS_PATTERN = re.compile(
        r"##\s*(?:📊\s*项目定位|\d+\.\s*项目概要[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        re.DOTALL,
    )
    # 新格式: ## 🔥 近期催化剂   旧格式: ## 7. 风险与机会
    CAT_PATTERN = re.compile(
        r"##\s*(?:🔥\s*近期催化剂|\d+\.\s*(?:风险与机会|近期催化剂)[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        re.DOTALL,
    )

    enriched = []
    for p in projects:
        p = dict(p)  # shallow copy
        name_key = p.get("name", "").lower().strip()
        content = analysis_map.get(name_key, "")

        if content:
            # 提取一句话定位
            pos_match = POS_PATTERN.search(content)
            if pos_match:
                text = pos_match.group(1).strip()
                # 过滤掉表格行和空行，取第一段有效文字
                lines = [
                    l.strip() for l in text.split("\n")
                    if l.strip()
                    and not l.strip().startswith("|")
                    and not l.strip().startswith("-")
                    and not l.strip().startswith("**")
                ]
                if lines:
                    first = lines[0]
                    # 截断到合理长度（第一个句号或逗号分句）
                    for sep in ["。", "，旨在", "，支持", "，提供", "，专注", "，强调"]:
                        idx = first.find(sep)
                        if idx > 10:
                            first = first[:idx + len(sep)].rstrip("，、")
                            break
                    # 去掉来源标注 (来源：xxx)
                    first = re.sub(r"[（(]来源[：:].*?[）)]", "", first).strip()
                    p["summary"] = first[:80]

            # 提取催化剂列表
            cat_match = CAT_PATTERN.search(content)
            if cat_match:
                cat_lines = []
                for l in cat_match.group(1).strip().split("\n"):
                    l = l.strip().lstrip("-•·* ")
                    if l and not l.startswith("|") and not l.startswith("#"):
                        cat_lines.append(l)
                best = pick_best_catalyst(cat_lines)
                if best:
                    p["catalyst"] = best

        enriched.append(p)

    logger.info(
        f"📋 数据回填: {sum(1 for p in enriched if p.get('summary'))} 个 summary, "
        f"{sum(1 for p in enriched if p.get('catalyst'))} 个 catalyst"
    )
    return enriched


# ============================================================
#  Step 5: 配图生成
# ============================================================

def run_card_generator(projects: list[dict], date_str: str) -> str:
    """
    生成 1200×675 配图 HTML

    Returns:
        保存路径
    """
    logger.info("📸 配图: 生成中...")
    from ..services.card_generator import save_card
    path = save_card(projects, date_str)
    logger.info(f"📸 配图完成: {path}")
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
    today = datetime.now()
    date_30d_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    date_str_today = today.strftime("%m-%d")

    system_prompt = (
        "你是 Web3 Alpha 猎手，负责写 X(Twitter) 推文。\n\n"
        "## 任务\n"
        "根据投研报告，为每个项目生成一条独立推文。\n\n"
        "## 推文格式（每个项目一条）\n"
        "```\n"
        "🔍 项目名称 @X账号\n\n"
        "一段话介绍项目定位和核心产品（2-3句）\n\n"
        "💰 融资金额 + 领投方\n"
        "👥 创始人姓名 + 背景\n"
        "🪙 代币符号 + 总量 + 关键分配\n"
        "📈 价格 | 市值 | FDV | TVL | Twitter粉丝\n\n"
        "🔥 近期催化剂：\n"
        "• 事件1（日期）\n"
        "• 事件2（日期）\n"
        "```\n\n"
        "## 要求\n"
        f"- 催化剂只取 {date_30d_ago} 之后的事件，旧事件不要\n"
        "- 标题只写项目名称和 @X账号，不写代币符号和赛道\n"
        "- 不写可信度评分\n"
        "- 不写建议动作、投资建议\n"
        "- 不附带 URL 和来源链接\n"
        "- 金额用简写：$670万、$1.08亿、$0.035，不要写 6700000 USD 这种长数字\n"
        "- 粉丝数用简写：10.2万粉，不要写 102145\n"
        "- 没有数据的行直接跳过\n"
    )

    user_prompt = (
        f"今日投研的 {len(projects)} 个项目：{', '.join(project_names)}\n\n"
        f"投研简报内容：\n{summary[:3000]}"
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

        # 解析: 按 🔍 分割为各项目推文
        import re
        tweets = []

        # 按 🔍 分割（每个项目一条推文）
        blocks = re.split(r"(?=🔍)", result.strip())
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            # 提取项目名（🔍 后面的第一个词）
            name_match = re.match(r"🔍\s*(.+?)(?:\s*@|\n)", block)
            name = name_match.group(1).strip() if name_match else "Unknown"
            tweets.append({
                "name": name,
                "text": block,
                "char_count": len(block),
            })

        # fallback: 如果解析失败，整段作为推文
        if not tweets:
            tweets.append({
                "name": "Alpha日报",
                "text": result,
                "char_count": len(result),
            })

        logger.info(f"🐦 推文完成: {len(tweets)} 条项目推文")
        return tweets

    except Exception as e:
        logger.error(f"🐦 推文失败: {e}")
        return []


def _save_tweets(tweets: list[dict], date_str: str) -> str:
    """保存推文到文件"""
    _ensure_dirs()
    path = REPORTS_DIR / f"tweets_{date_str}.md"
    content = f"# 🐦 推文文案 — {date_str}\n\n"
    for t in tweets:
        content += f"## {t['name']}\n\n```\n{t['text']}\n```\n\n"
    path.write_text(content, encoding="utf-8")
    logger.info(f"📁 保存: {path}")
    return str(path)


# ============================================================
#  Step 7: 润色官 — 定稿
# ============================================================

def run_polisher(draft: str, api_config: dict = None) -> str:
    """
    润色日报最终版

    Args:
        draft: 写手输出的日报草稿
        api_config: AI 配置

    Returns:
        润色后的最终日报
    """
    api_config = api_config or {}
    logger.info("✨ 润色官: 润色定稿...")

    system_prompt = (
        "你是专业编辑。对以下投研日报做最终润色：\n"
        "1. 修正错别字和语法\n"
        "2. 统一格式和标点\n"
        "3. 确保数据引用准确\n"
        "4. 不改变内容和结构\n"
        "5. 去掉明显的 AI 痕迹（\"值得关注的是\"\"不可忽视\"等套话）\n\n"
        "直接输出润色后的完整日报。"
    )

    provider = api_config.get("provider", "volcengine")
    model_id = api_config.get("model_id")

    try:
        result = generate_text(
            prompt=draft,
            model_id=model_id,
            provider=provider,
            temperature=0.3,
            system_prompt=system_prompt,
            max_tokens=6000,
        )
        logger.info("✨ 润色官完成")
        return result
    except Exception as e:
        logger.error(f"✨ 润色官失败: {e}，使用写手原稿")
        return draft


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


def _save_project_report(name: str, content: str, date_str: str) -> str:
    """保存单项目完整报告"""
    _ensure_dirs()
    safe_name = name.replace(" ", "_").replace("/", "_")
    path = REPORTS_DIR / "projects" / f"{safe_name}_{date_str}.md"
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
#  主入口
# ============================================================

async def generate_daily_report(
    api_config: dict = None,
    concurrency: int = DEFAULT_CONCURRENCY,
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
    date_str = datetime.now().strftime("%Y%m%d")

    def _progress(step: str, detail: str):
        logger.info(f"[{step}] {detail}")
        if progress_callback:
            progress_callback(step, detail)

    try:
        # ===== Step 1: 侦察官 =====
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

        # ===== Step 2: 策略官（并发 N） =====
        _progress("strategist", f"开始分析 {len(projects)} 个项目（并发 {concurrency}）...")
        analysis_results = await run_strategist_batch(projects, concurrency)

        # 保存每个项目的完整报告
        project_paths = []
        for r in analysis_results:
            if r.get("content"):
                path = _save_project_report(r["name"], r["content"], date_str)
                project_paths.append(path)

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

        # ===== Step 3: 审核官（总结归纳） =====
        _progress("summarizer", "总结归纳分析报告...")
        summary = run_summarizer(analysis_results, api_config)

        # ===== Step 4: 写手（组装日报） =====
        _progress("writer", "组装日报...")
        draft = run_writer(summary, projects, date_str, api_config)

        # ===== Step 4.5: 从策略官报告回填 summary + catalyst =====
        _progress("enrich", "提取项目定位与催化剂...")
        enriched_projects = _enrich_projects_from_analysis(projects, analysis_results)

        # ===== Step 5: 配图生成 =====
        _progress("card", "生成配图...")
        card_path = run_card_generator(enriched_projects, date_str)

        # ===== Step 6: 推文文案 =====
        _progress("tweets", "生成推文文案...")
        tweets = run_tweet_writer(summary, enriched_projects, api_config)
        tweets_path = ""
        if tweets:
            tweets_path = _save_tweets(tweets, date_str)

        # ===== Step 7: 润色官（定稿） =====
        _progress("polisher", "润色定稿...")
        final_report = run_polisher(draft, api_config)

        # 保存日报
        report_path = _save_daily_report(final_report, date_str)

        elapsed = time.time() - start_time
        _progress("done", f"日报生成完成！{ok_count} 个项目, {elapsed:.0f}s")

        return {
            "status": "success",
            "date": date_str,
            "projects_count": ok_count,
            "report_path": report_path,
            "card_path": card_path,
            "tweets_path": tweets_path,
            "project_paths": project_paths,
            "report_content": final_report,
            "tweets": tweets,
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
