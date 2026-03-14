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
from ...services.card_generator import _catalyst_importance


# ============================================================
#  项目列表解析器
# ============================================================

def _parse_projects_from_text(text: str) -> list[dict]:
    """
    从 Surf 返回的 Markdown 表格中解析项目列表

    支持 G 版 7 列表格:
    | 项目名称 | Twitter | 赛道 | KOL 关注数 | 代币 | 阶段 | 近期催化剂 |

    也兼容旧版 5 列表格和列表项格式。
    """
    projects = []
    seen = set()

    # ---- 尝试解析 Markdown 表格 ----
    lines = text.strip().split("\n")
    header_idx = -1
    col_count = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and "项目" in stripped:
            header_idx = i
            col_count = len([c for c in stripped.split("|") if c.strip()])
            break

    # 跳过表头行和分隔行
    data_start = header_idx + 2 if header_idx >= 0 else -1

    if data_start > 0:
        for line in lines[data_start:]:
            stripped = line.strip()
            if not stripped.startswith("|"):
                break  # 表格结束
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if not cells or cells[0].startswith("---"):
                continue

            # P35: 跳过序号列（如 "1" "2"），LLM 有时输出带序号的表格
            if cells[0].isdigit() and len(cells) > 3:
                cells = cells[1:]

            name = cells[0].strip("** ").strip()
            twitter = cells[1].strip() if len(cells) > 1 else ""

            # 跳过表头误匹配
            if name.lower() in ("项目名称", "project", "项目", "-"):
                continue
            # 确保 twitter 以 @ 开头
            if twitter and not twitter.startswith("@"):
                twitter = f"@{twitter}"

            key = twitter.lower()
            if key in seen:
                continue
            seen.add(key)

            # 7 列 G 版格式
            if len(cells) >= 7:
                raw_cat = cells[6].strip()
                # P36: 评分过滤 — 只有高价值催化事件(≥4分)才标红
                cat_score = _catalyst_importance(raw_cat)
                projects.append({
                    "name": name,
                    "twitter": twitter,
                    "category": cells[2].strip(),
                    "kol_24h": _safe_int(cells[3]),
                    "token": cells[4].strip(),
                    "stage": cells[5].strip(),
                    "catalyst": raw_cat if cat_score >= 4 else "",
                    "buzz": raw_cat,  # 兼容旧字段，始终保留原文
                })
            # 6 列格式
            elif len(cells) >= 6:
                raw_cat = cells[5].strip()
                cat_score = _catalyst_importance(raw_cat)
                projects.append({
                    "name": name,
                    "twitter": twitter,
                    "category": cells[2].strip(),
                    "kol_24h": _safe_int(cells[3]),
                    "token": "",
                    "stage": cells[4].strip(),
                    "catalyst": raw_cat if cat_score >= 4 else "",
                    "buzz": raw_cat,
                })
            # 5 列旧版格式
            elif len(cells) >= 5:
                projects.append({
                    "name": name,
                    "twitter": twitter,
                    "category": cells[2].strip(),
                    "kol_24h": _safe_int(cells[3]),
                    "token": "",
                    "stage": "",
                    "catalyst": "",
                    "buzz": cells[4].strip()[:100],
                })
            else:
                projects.append({
                    "name": name,
                    "twitter": twitter,
                    "category": "",
                    "kol_24h": 0,
                    "token": "",
                    "stage": "",
                    "catalyst": "",
                    "buzz": " | ".join(cells[2:])[:100],
                })

    # ---- 兼容：列表项格式 ----
    if not projects:
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
                "token": "",
                "stage": "",
                "catalyst": "",
                "buzz": item[2].strip()[:100],
            })

    return projects


def _safe_int(s: str) -> int:
    """安全提取数字，处理 '高' '未知' '估算5-10' 等非标准值"""
    m = re.search(r"(\d+)", s)
    return int(m.group(1)) if m else 0


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
            f"赛道: {p.get('category', '')}\n"
            f"代币: {p.get('token', '')}\n"
            f"阶段: {p.get('stage', '')}\n"
            f"近期催化剂: {p.get('catalyst', p.get('buzz', ''))}"
        )

    return {
        "scout_projects": projects,
        "raw_input": raw_input_for_strategist,
        "logs": [f"[{datetime.now().isoformat()}] Scout discovered {len(projects)} projects."],
        "thinking_steps": [{"agent": "scout", "steps": steps, "status": "completed"}],
    }
