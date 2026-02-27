"""
P31: Scout 智能体（选题发现）
从 leak.me 数据源自动发现热门 Web3 项目
"""
from datetime import datetime
from . import call_surf, parse_projects_from_text


def scout_agent(state: dict) -> dict:
    """
    🔭 Scout — 自动选题发现

    调用 Surf API 搜索 leak.me，返回热门项目列表。
    如果 raw_input 已有具体项目名，则跳过。
    """
    steps = []

    # 加载 prompt 模板
    try:
        from ...core.prompts import render_modular_prompt
        user_prompt = render_modular_prompt("research/scout.jinja2", {})
    except Exception:
        user_prompt = (
            "请访问和分析 leak.me（https://leak.me/）网站的当前 trending 数据。"
            "请整理出所有被 KOL 关注的 Web3 和 AI 项目，"
            "用表格列出：项目名称、Twitter 账号、类别、24h KOL 新关注数、热度原因。"
            "排除个人 KOL 账号、交易所和媒体。"
        )

    steps.append({"step": "searching", "content": "正在搜索 leak.me 热门项目..."})

    result = call_surf(
        model="surf-1.5",
        system_prompt="",
        user_prompt=user_prompt,
        abilities=["search"],
        reasoning="high",
    )

    if result["status"] != 200:
        steps.append({"step": "error", "content": f"Surf API 调用失败: {result.get('error', '')[:100]}"})
        return {
            "scout_projects": [],
            "logs": [f"[{datetime.now().isoformat()}] Scout failed: {result.get('error', '')}"],
            "thinking_steps": [{"agent": "scout", "steps": steps, "status": "error"}],
        }

    content = result["content"]
    elapsed = result.get("elapsed", 0)
    tokens = result.get("usage", {}).get("total_tokens", "?")

    # 解析项目列表
    projects = parse_projects_from_text(content)

    steps.append({"step": "parsed", "content": f"发现 {len(projects)} 个项目 ({elapsed:.0f}s, {tokens} tokens)"})
    for i, p in enumerate(projects[:5], 1):
        steps.append({"step": "project", "content": f"{i}. {p['name']} ({p['twitter']})"})
    steps.append({"step": "completed", "content": "选题发现完成"})

    # 将第一个项目作为 raw_input 传给 Strategist
    raw_input_for_strategist = ""
    if projects:
        p = projects[0]
        raw_input_for_strategist = f"项目名称: {p['name']}\nTwitter: {p['twitter']}\n类别: {p.get('category', '')}\nKOL关注: +{p.get('kol_24h', 0)}\n热度原因: {p.get('buzz', '')}"

    return {
        "scout_projects": projects,
        "raw_input": raw_input_for_strategist,
        "logs": [f"[{datetime.now().isoformat()}] Scout discovered {len(projects)} projects."],
        "thinking_steps": [{"agent": "scout", "steps": steps, "status": "completed"}],
    }
