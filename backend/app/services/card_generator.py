"""
P31: 投研配图生成器
生成 1200×675 浅色瑞士金融报纸风 HTML 卡片，适配 X(Twitter) 分享

前端用 html2canvas 截图为 PNG
"""
import re
from datetime import datetime, timedelta
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "research"

# 赛道 emoji 映射
CATEGORY_EMOJI = {
    "AI": "🤖", "Web3": "🔗", "Web3 AI": "🧠", "Web3/AI": "🧠",
    "DeFi": "💰", "DeFi AI": "🤖", "Layer1": "⛓️", "Layer2": "🔷",
    "NFT": "🎨", "Gaming": "🎮", "GameFi": "🎮",
    "SportFi": "⚽", "Infra": "🏗️", "Social": "💬", "RWA": "🏦",
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


def pick_best_catalyst(catalysts: list[str], today: datetime = None) -> str:
    """
    从催化剂列表中选出最适合展示在卡片上的一条。

    优先级：
    1. 未来事件（最近的一条）
    2. 7 天内已发生的事件（最近的一条）
    3. 模糊未来事件（如 "2026年 xxx"）
    4. 都不满足 → 返回空字符串

    Args:
        catalysts: 催化剂文本列表，例如 ["2026-02-03 Vision 2030", "2026年 美国市场重入"]
        today: 当前日期（默认 now）
    """
    if not catalysts:
        return ""

    today = today or datetime.now()
    today_date = today.date()
    cutoff = today_date - timedelta(days=7)

    future_events = []    # (date, text)
    recent_events = []    # (date, text)
    vague_future = []     # 模糊未来事件

    for c in catalysts:
        c = c.strip().lstrip("•·- ")
        if not c:
            continue

        # 尝试提取 YYYY-MM-DD
        m = re.search(r"(202[4-9])-(\d{2})-(\d{2})", c)
        if m:
            try:
                event_date = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
                # 去掉日期前缀，保留事件描述
                desc = re.sub(r"^\s*202[4-9]-\d{2}-\d{2}\s*[:：]?\s*", "", c).strip()
                display = f"{m.group(2)}-{m.group(3)} {desc}"
                if event_date > today_date:
                    future_events.append((event_date, display))
                elif event_date >= cutoff:
                    recent_events.append((event_date, display))
                # else: 太旧，丢弃
                continue
            except ValueError:
                pass

        # 尝试匹配 YYYY-MM（月份） 或 XX月
        m_month = re.search(r"(202[4-9])-(\d{2})\b|(\d{1,2})月", c)
        if m_month:
            try:
                if m_month.group(1):  # YYYY-MM
                    year, month = int(m_month.group(1)), int(m_month.group(2))
                else:  # X月
                    year, month = today.year, int(m_month.group(3))
                if year > today.year or (year == today.year and month >= today.month):
                    desc = re.sub(r"^\s*202[4-9]-\d{2}\s*[:：]?\s*|\s*\d{1,2}月\s*", "", c).strip()
                    display = f"{month}月 {desc}" if desc else c
                    vague_future.append(display)
                    continue
            except ValueError:
                pass

        # 模糊年份（如 "2026年 xxx"）
        m_year = re.search(r"(202[5-9])年", c)
        if m_year and int(m_year.group(1)) >= today.year:
            vague_future.append(c)
            continue

    # 清理催化剂文本：截断到第一个逗号/分号，去掉尾部标点
    def _clean(text: str) -> str:
        for sep in ["，", "；", "。", ",", ";"]:
            idx = text.find(sep)
            if idx > 4:
                text = text[:idx]
                break
        return text.rstrip("。，；.、：: ")

    # 按优先级返回
    if future_events:
        future_events.sort(key=lambda x: x[0])
        return _clean(future_events[0][1])
    if recent_events:
        recent_events.sort(key=lambda x: x[0], reverse=True)
        return _clean(recent_events[0][1])
    if vague_future:
        return _clean(vague_future[0])
    return ""


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
        summary = _truncate(p.get("summary", p.get("buzz", "")), 60)
        twitter = p.get("twitter", "")
        catalyst = _truncate(p.get("catalyst", ""), 25)

        catalyst_html = ""
        if catalyst:
            catalyst_html = f'<div class="catalyst">🔥 {catalyst}</div>'

        cards_html += f"""
            <div class="card">
                <div class="card-top"><span>{emoji} {_truncate(category, 12)}</span><span class="twitter">{twitter}</span></div>
                <h2 class="project-name">{name}</h2>
                <div class="desc">{summary}</div>
                {catalyst_html}
            </div>"""

    # 底部提示
    extra_note = ""
    if total > max_projects:
        extra_note = f'<div style="text-align:center;font-size:13px;color:#666;margin-top:8px;">+{total - max_projects} 个项目见完整报告</div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: #E5E5E5;
    font-family: 'Inter', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh;
}}
.canvas {{
    width: 1200px; height: 675px;
    background-color: #F4F3EE;
    color: #1C1C1C;
    padding: 40px 60px;
    display: flex; flex-direction: column;
    overflow: hidden;
}}
.header {{
    display: flex; justify-content: space-between; align-items: flex-end;
    padding-bottom: 20px;
    border-bottom: 3px solid #1C1C1C;
}}
.title-group {{ display: flex; flex-direction: column; }}
.subtitle {{ font-size: 16px; letter-spacing: 4px; font-weight: 500; margin-bottom: 4px; }}
.main-title {{ font-size: 42px; font-weight: 900; letter-spacing: -1px; }}
.main-title .accent {{ color: #FF3A2D; }}
.date {{ font-size: 24px; font-weight: 700; border-bottom: 2px solid #1C1C1C; padding-bottom: 4px; }}
.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
    flex-grow: 1;
    border-bottom: 1px solid #1C1C1C;
    border-left: 1px solid #1C1C1C;
}}
.card {{
    border-right: 1px solid #1C1C1C;
    border-bottom: 1px solid #1C1C1C;
    padding: 24px;
    display: flex; flex-direction: column;
}}
.card-top {{
    display: flex; justify-content: space-between;
    margin-bottom: 16px; font-size: 14px; font-weight: 500;
}}
.twitter {{ color: #666; }}
.project-name {{
    font-size: 32px; font-weight: 900; margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}}
.desc {{ font-size: 15px; color: #1C1C1C; line-height: 1.4; flex-grow: 1; }}
.catalyst {{
    background-color: #FF3A2D; color: #FFF;
    font-size: 13px; font-weight: 700;
    padding: 6px 10px; display: inline-block;
    align-self: flex-start; margin-top: 12px;
}}
.footer {{
    display: flex; justify-content: space-between;
    padding-top: 16px; font-size: 14px; font-weight: 500;
}}
</style>
</head>
<body>
<div class="canvas">
    <div class="header">
        <div class="title-group">
            <span class="subtitle">每日投研精选</span>
            <div class="main-title"><span class="accent">ALPHA</span> 日报</div>
        </div>
        <div class="date">{date_display}</div>
    </div>
    <div class="grid">{cards_html}
    </div>
    <div class="footer">
        <span style="color:#999;">⚠️ 以上内容仅供参考，不构成投资建议</span>
        <span>雪球 @xueqiu88</span>
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
