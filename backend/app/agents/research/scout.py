"""
P31: Scout 智能体（选题发现）
从 leak.me 数据源自动发现热门 Web3 项目

在 LangGraph 中的位置:
    Scout → Strategist → Critic(清洗) → Writer → Polisher
    仅 project_research 模式 + 空输入时触发
"""
import re
from datetime import datetime
from ...services.surf_service import SurfService


# ============================================================
#  项目列表解析器
# ============================================================

def _parse_projects_from_text(text: str) -> list[dict]:
    """
    从 Surf 返回的 Markdown 中解析项目列表

    支持两种格式:
    1. Markdown 表格: | Name | @handle | ... |
    2. 列表项: - **Name** (@handle): ...
    """
    projects = []
    seen = set()

    # 解析 Markdown 表格行
    table_rows = re.findall(r"\|\s*(.+?)\s*\|\s*(@\w+)\s*\|(.+?)\|", text)
    for row in table_rows:
        name = row[0].strip().strip("**").strip("| ").strip()
        twitter = row[1].strip()
        rest = row[2].strip()
        # 跳过表头
        if name.lower() in ("项目名称", "project", "项目", "姓名", "-", "（无）"):
            continue
        key = twitter.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            "name": name,
            "twitter": twitter,
            "category": "",
            "kol_24h": 0,
            "buzz": rest[:100].strip(" |"),
        })

    # 解析列表项
    list_items = re.findall(
        r"[-•]\s*\*{0,2}(.+?)\*{0,2}\s*\((@\w+)\)[：:]\s*(.+?)(?:\n|$)", text
    )
    for item in list_items:
        name = item[0].strip()
        twitter = item[1].strip()
        key = twitter.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            "name": name,
            "twitter": twitter,
            "category": "",
            "kol_24h": 0,
            "buzz": item[2].strip()[:100],
        })

    # 提取 KOL 关注数
    for p in projects:
        kol_match = re.search(r"(\d+)\s*(?:位?\s*)?KOL", p["buzz"], re.IGNORECASE)
        if kol_match:
            p["kol_24h"] = int(kol_match.group(1))

    return projects


# ============================================================
#  Scout 智能体
# ============================================================

def scout_agent(state: dict) -> dict:
    """
    🔭 Scout — 自动选题发现

    调用 Surf API 搜索 leak.me，返回热门项目列表。
    如果 raw_input 已有具体项目名，则不应进入此节点
    （由 graph.py entry_router 控制）。
    """
    steps = []

    # 加载 Scout prompt 模板
    try:
        from ...core.prompts import render_modular_prompt
        user_prompt = render_modular_prompt("research/scout.jinja2", {})
    except Exception:
        # Fallback：硬编码基础 prompt
        user_prompt = (
            "请访问和分析 leak.me（https://leak.me/）网站的当前 trending 数据。"
            "请整理出所有被 KOL 关注的 Web3 和 AI 项目，"
            "用表格列出：项目名称、Twitter 账号、类别、24h KOL 新关注数、热度原因。"
            "排除个人 KOL 账号、交易所和媒体。"
        )

    steps.append({"step": "searching", "content": "正在搜索 leak.me 热门项目..."})

    # 调用 Surf API
    surf = SurfService()
    result = surf.call(
        model="surf-1.5",
        user_prompt=user_prompt,
        abilities=["search"],
        reasoning="high",
    )

    if result["status"] != 200:
        error_msg = result.get("error", "Unknown error")[:100]
        steps.append({"step": "error", "content": f"Surf API 调用失败: {error_msg}"})
        return {
            "scout_projects": [],
            "logs": [f"[{datetime.now().isoformat()}] Scout failed: {error_msg}"],
            "thinking_steps": [{"agent": "scout", "steps": steps, "status": "error"}],
        }

    content = result["content"]
    elapsed = result.get("elapsed", 0)
    tokens = result.get("usage", {}).get("total_tokens", "?")

    # 解析项目列表
    projects = _parse_projects_from_text(content)

    steps.append({
        "step": "parsed",
        "content": f"发现 {len(projects)} 个项目 ({elapsed:.0f}s, {tokens} tokens)",
    })
    for i, p in enumerate(projects[:5], 1):
        kol_info = f" KOL+{p['kol_24h']}" if p["kol_24h"] else ""
        steps.append({"step": "project", "content": f"{i}. {p['name']} ({p['twitter']}){kol_info}"})
    steps.append({"step": "completed", "content": "选题发现完成"})

    # 将第一个项目格式化为 raw_input 传给 Strategist
    raw_input_for_strategist = ""
    if projects:
        p = projects[0]
        raw_input_for_strategist = (
            f"项目名称: {p['name']}\n"
            f"Twitter: {p['twitter']}\n"
            f"类别: {p.get('category', '')}\n"
            f"KOL关注: +{p.get('kol_24h', 0)}\n"
            f"热度原因: {p.get('buzz', '')}"
        )

    return {
        "scout_projects": projects,
        "raw_input": raw_input_for_strategist,
        "logs": [f"[{datetime.now().isoformat()}] Scout discovered {len(projects)} projects."],
        "thinking_steps": [{"agent": "scout", "steps": steps, "status": "completed"}],
    }
