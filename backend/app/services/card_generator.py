"""
P31: 投研配图生成器
生成 1200×675 暗色卡片 HTML，适配 X(Twitter) 分享

前端用 html2canvas 截图为 PNG
"""
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "research"

# 赛道 emoji 映射
CATEGORY_EMOJI = {
    "AI": "🤖", "Web3": "🔗", "Web3 AI": "🧠", "Web3/AI": "🧠",
    "DeFi": "💰", "Layer1": "⛓️", "Layer2": "🔷", "NFT": "🎨",
    "Gaming": "🎮", "Infra": "🏗️", "Social": "💬",
}


def _get_emoji(category: str) -> str:
    for k, v in CATEGORY_EMOJI.items():
        if k.lower() in category.lower():
            return v
    return "📌"


def _truncate(text: str, max_len: int) -> str:
    """精确截断，避免截在中间"""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"


def generate_card_html(
    projects: list[dict],
    date_str: str = None,
    max_projects: int = 6,
) -> str:
    """
    生成 1200×675 配图 HTML

    Args:
        projects: 项目列表，每项需有 name, category, summary（一句话定位）
        date_str: 日期 YYYYMMDD
        max_projects: 最多显示几个（默认6）

    Returns:
        完整 HTML 字符串
    """
    date_str = date_str or datetime.now().strftime("%Y%m%d")
    date_display = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
    display_projects = projects[:max_projects]
    total = len(projects)

    # 生成项目卡片
    cards_html = ""
    for p in display_projects:
        name = _truncate(p.get("name", "Unknown"), 20)
        category = p.get("category", "Web3")
        emoji = _get_emoji(category)
        # 从日报精简版提取一句话定位（取前60字）
        summary = _truncate(p.get("summary", p.get("buzz", "")), 60)
        twitter = p.get("twitter", "")

        cards_html += f"""
            <div class="card">
                <div class="card-header">
                    <span class="card-emoji">{emoji}</span>
                    <span class="card-cat">{_truncate(category, 12)}</span>
                </div>
                <div class="card-name">{name}</div>
                {f'<div class="card-twitter">{twitter}</div>' if twitter else ''}
                <div class="card-summary">{summary}</div>
            </div>"""

    # 底部提示
    extra_note = ""
    if total > max_projects:
        extra_note = f'<div class="footer-note">+{total - max_projects} more projects in full report</div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: #050505;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "SF Pro Display", sans-serif;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; color: #e5e7eb;
}}
.canvas {{
    width: 1200px; height: 675px;
    background: linear-gradient(135deg, #0a0a0f 0%, #111118 50%, #0d0d14 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px; padding: 40px 48px;
    display: flex; flex-direction: column;
    position: relative; overflow: hidden;
}}
.canvas::before {{
    content: ''; position: absolute; top: -200px; right: -200px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(99,102,241,0.08), transparent 70%);
    pointer-events: none;
}}
.header {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 32px; padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.subtitle {{
    font-size: 11px; color: #6b7280; letter-spacing: 4px;
    text-transform: uppercase; margin-bottom: 4px;
}}
.title {{
    font-size: 26px; font-weight: 800; letter-spacing: 2px;
    background: linear-gradient(90deg, #fff, #a1a1aa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.date-badge {{
    background: #f5b300; color: #000; padding: 6px 16px;
    border-radius: 20px; font-size: 13px; font-weight: 700;
    letter-spacing: 1px;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px; flex: 1;
}}
.card {{
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 20px;
    display: flex; flex-direction: column;
    transition: border-color 0.2s;
}}
.card-header {{
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 10px;
}}
.card-emoji {{ font-size: 16px; }}
.card-cat {{
    font-size: 11px; color: #9ca3af;
    letter-spacing: 0.5px;
}}
.card-name {{
    font-size: 18px; font-weight: 700; color: #fff;
    margin-bottom: 4px; line-height: 1.3;
}}
.card-twitter {{
    font-size: 12px; color: #818cf8;
    margin-bottom: 8px;
}}
.card-summary {{
    font-size: 12px; color: #9ca3af;
    line-height: 1.6;
    display: -webkit-box; -webkit-line-clamp: 3;
    -webkit-box-orient: vertical; overflow: hidden;
}}
.footer {{
    display: flex; justify-content: space-between; align-items: center;
    margin-top: auto; padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.04);
}}
.footer-left {{
    font-size: 11px; color: #52525b;
    letter-spacing: 1px;
}}
.footer-right {{
    font-size: 11px; color: #52525b;
}}
.footer-note {{
    font-size: 11px; color: #6b7280;
    text-align: center; margin-top: 8px;
}}
</style>
</head>
<body>
<div class="canvas">
    <div class="header">
        <div>
            <div class="subtitle">Institutional Grade Intel</div>
            <div class="title">WEB3 ALPHA DAILY</div>
        </div>
        <div class="date-badge">{date_display}</div>
    </div>
    <div class="grid">{cards_html}
    </div>
    <div class="footer">
        <div class="footer-left">{total} PROJECTS ANALYZED</div>
        <div class="footer-right">Powered by Surf AI · leak.me</div>
    </div>
    {extra_note}
</div>
</body>
</html>"""

    return html


def save_card(projects: list[dict], date_str: str = None) -> str:
    """
    生成并保存配图 HTML 文件

    Returns:
        保存路径
    """
    date_str = date_str or datetime.now().strftime("%Y%m%d")
    html = generate_card_html(projects, date_str)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"card_{date_str}.html"
    path.write_text(html, encoding="utf-8")
    return str(path)
