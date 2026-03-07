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
from ..core.config import get_logger, cn_now

logger = get_logger("daily_report")

# 默认配置
DEFAULT_MODEL = "surf-1.5"
DEFAULT_CONCURRENCY = 3
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
            f"检索以下 {len(sources)} 个 Twitter/X 账号近 7 天推文，找出热门 Crypto 项目：\n"
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

    # P32-C: 从 writer.jinja2 模板渲染（P15 可编辑）
    system_prompt = _render_research_template("writer.jinja2", {})

    if not system_prompt:
        system_prompt = (
            "你是投研日报写手。将项目总览和精简分析组装成一份结构清晰的每日投研快报。\n\n"
            "日报格式要求：\n1. 标题：# 🌊 每日投研快报\n2. 元信息（日期、项目数）\n"
            "3. 📋 项目总览表格\n4. 每个项目的分析，严格只保留 4 个板块：\n"
            "   📊 一句话定位 / 🎯 关键事件与参与机会 / 👥 团队与背书 / 🔥 近期催化剂\n"
            "5. 没有数据的板块直接省略\n6. 每个板块 2-4 句话\n7. 末尾加免责声明\n\n"
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

    # ---- 正则模式 ----
    # Summary: 新格式 ## 📊 项目定位   旧格式 ## 1. 项目概要
    POS_PATTERN = re.compile(
        r"##\s*(?:📊\s*项目定位|\d+\.\s*项目概要[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        re.DOTALL,
    )
    # Catalyst: 只匹配专门的催化剂段，不匹配 "风险与机会"
    # 新格式: ## 🔥 近期催化剂   旧格式: ## X. 近期催化剂
    CAT_PATTERN = re.compile(
        r"##\s*(?:🔥\s*近期催化剂|\d+\.\s*近期催化剂[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        re.DOTALL,
    )

    enriched = []
    for p in projects:
        p = dict(p)  # shallow copy
        name_key = p.get("name", "").lower().strip()
        content = analysis_map.get(name_key, "")

        if content:
            # ---------- 提取一句话定位（短版，适配配图卡片） ----------
            pos_match = POS_PATTERN.search(content)
            if pos_match:
                text = pos_match.group(1).strip()
                # 取第一段有效文字
                lines = [
                    l.strip() for l in text.split("\n")
                    if l.strip()
                    and not l.strip().startswith("|")
                    and not l.strip().startswith("-")
                    and not l.strip().startswith("**")
                ]
                if lines:
                    # 跳过模板指令行（如 "是什么、做什么、核心产品、目标市场"）
                    lines = [
                        l for l in lines
                        if len(l) > 8
                        and "是什么" not in l
                        and "用表格" not in l
                    ]
                if lines:
                    raw = lines[0]
                    # 去掉来源标注
                    raw = re.sub(r"[（(]来源[：:].*?[）)]", "", raw).strip()
                    # 去掉项目名开头（如 "Dicey 定位为..." → "定位为..."）
                    raw = re.sub(
                        r"^[A-Za-z0-9\s\$]+(?:定位为|是)",
                        "",
                        raw,
                    ).strip()
                    # 截断策略：保留前 2 个逗号分句（兼顾信息量和卡片空间）
                    # 例如 "非托管 DeFi AI 代理基础设施，支持跨协议自动执行收益策略"
                    commas = [m.start() for m in re.finditer("，", raw)]
                    if len(commas) >= 2 and commas[1] < 50:
                        # 取到第 2 个逗号
                        raw = raw[:commas[1]]
                    elif len(commas) >= 1 and commas[0] < 45:
                        # 只有 1 个逗号在合理范围内
                        raw = raw[:commas[0]]
                    elif "。" in raw:
                        idx = raw.index("。")
                        if idx < 50:
                            raw = raw[:idx]
                    # 最终限制 45 字符
                    p["summary"] = raw[:45]

            # ---------- 提取催化剂（催化剂段 + 代币经济学解锁） ----------
            cat_lines = []

            # 来源 1: 专门催化剂段 ## 🔥 近期催化剂
            cat_match = CAT_PATTERN.search(content)
            if cat_match:
                for l in cat_match.group(1).strip().split("\n"):
                    l = l.strip().lstrip("-•·* ")
                    if not l or l.startswith("|") or l.startswith("#"):
                        continue
                    if any(kw in l for kw in ["风险", "推理", "局限", "不确定"]):
                        continue
                    cat_lines.append(l)

            # 来源 2: 代币经济学段中的解锁日期
            token_match = re.search(
                r"##\s*(?:🪙\s*代币经济学|代币经济)\s*\n+(.*?)(?=\n##|\Z)",
                content, re.DOTALL,
            )
            if token_match:
                token_text = token_match.group(1)
                # 提取 "YYYY-MM-DD 解锁 X%" 格式
                for m in re.finditer(
                    r"(202[4-9]-\d{2}-\d{2})\s*解锁\s*([\d.]+%)",
                    token_text,
                ):
                    cat_lines.append(f"{m.group(1)} 解锁 {m.group(2)}")

            if cat_lines:
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

        # 解析: 按行首「项目名称：」分割为各项目推文（兼容旧版🔍格式）
        import re
        tweets = []

        # 按行首「项目名称：」或「🔍」分割（避免内容中的"项目"误触发）
        blocks = re.split(r"(?=^项目名称：|^🔍)", result.strip(), flags=re.MULTILINE)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            # 提取项目名
            name_match = re.match(r"(?:项目名称：|🔍)\s*(.+?)(?:\s*@|\n)", block)
            if not name_match:
                continue
            name = name_match.group(1).strip()
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
                    provider=provider,
                    model_id=model_id,
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
            except Exception as e:
                logger.warning(f"🐦 主推文 LLM 失败，使用 fallback: {e}")
                names = " | ".join(t.get("name", "?") for t in tweets[:6])
                body_text = f"今日 {n} 个项目：{names}"

            # 组装：固定标语 + LLM内容 + 固定结尾
            hook_text = f"今日发现，值得细看\n\n{body_text}\n\n⬇️\n\n#Web3Alpha"

            main_tweet = {
                "name": "Alpha日报",
                "text": hook_text,
                "char_count": len(hook_text),
            }
            tweets.insert(0, main_tweet)
            logger.info(f"🐦 主推文: {main_tweet['char_count']}字, 含 {n} 个项目")

        logger.info(f"🐦 推文完成: {len(tweets)} 条（含主推文）")
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
        # P33: 主推文只包含配图中显示的项目（max_projects=6）
        card_projects = enriched_projects[:6]
        tweets = run_tweet_writer(summary, card_projects, api_config)
        tweets_path = ""
        if tweets:
            tweets_path = _save_tweets(tweets, date_str)

        # ===== Step 7: 润色官（定稿） =====
        _progress("polisher", "润色定稿...")
        final_report = run_polisher(draft, api_config)

        # 保存日报
        report_path = _save_daily_report(final_report, date_str)

        # ===== Step 7.5: 回写 Sheets（P32-B） =====
        try:
            from app.services.research_sheet import research_sheet_service
            _progress("writeback", "回写分析记录到 Sheets...")
            research_sheet_service.write_analysis_records(enriched_projects, date_str)
            _progress("writeback", f"回写 {len(enriched_projects)} 条记录完成")
        except Exception as e:
            logger.warning(f"Sheets 回写跳过: {e}")

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
