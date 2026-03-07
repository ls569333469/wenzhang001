"""
P31: 投研配图生成器
生成 1200×675 浅色瑞士金融报纸风 HTML 卡片，适配 X(Twitter) 分享

前端用 html2canvas 截图为 PNG
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from app.core.config import cn_now

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


def _abbreviate_numbers(text: str) -> str:
    """将大数字缩写：82000000美元 → $82M, 小数字和已缩写的不动"""
    import re
    def _shorten(m):
        prefix = m.group(1) or ''  # $ or empty
        num_str = m.group(2)
        suffix = m.group(3) or ''  # 美元 etc.
        # 跳过后面紧跟 K/M/B/万/亿 的（已缩写）
        num = int(num_str)
        if num >= 1_000_000_000:
            short = f"${num / 1_000_000_000:g}B"
        elif num >= 1_000_000:
            short = f"${num / 1_000_000:g}M"
        elif num >= 100_000:
            short = f"${num / 10_000:g}万"
        else:
            return m.group(0)  # 10万以下不缩写
        # 如果原文有"美元"等后缀，去掉（已在$M里体现）
        if suffix in ('美元', '美金', 'USD'):
            return short
        return short + suffix
    # 只匹配 6位及以上的纯数字，且后面不是 K/M/B/万/亿（避免重复缩写）
    text = re.sub(r'(\$?)(\d{6,})(美元|美金|USD)?(?![KMBkmbWw万亿])', _shorten, text)
    return text


def _clip(text: str, max_len: int) -> str:
    """智能截断：不在括号中间断开，优先在标点处断开"""
    if len(text) <= max_len:
        return text
    chunk = text[:max_len]
    # 检查是否在未闭合的括号中间，如果是则回退到括号前
    for open_b, close_b in [('(', ')'), ('（', '）'), ('[', ']'), ('【', '】')]:
        last_open = chunk.rfind(open_b)
        last_close = chunk.rfind(close_b)
        if last_open > last_close and last_open > max_len // 3:
            chunk = chunk[:last_open].rstrip('，、 ,')
            return chunk
    # 在标点处断开
    for sep in ['，', '、', '。', '；', ',', ' ']:
        idx = chunk.rfind(sep)
        if idx > max_len // 3:
            return chunk[:idx]
    return chunk


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

    today = today or cn_now()
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
    date_str = date_str or cn_now().strftime("%Y%m%d")
    date_display = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
    display_projects = projects[:max_projects]
    total = len(projects)

    # 生成项目卡片
    cards_html = ""
    for p in display_projects:
        name = _clip(p.get("name", "Unknown"), 20)
        category = p.get("category", "Web3")
        emoji = _get_emoji(category)
        summary = _clip(p.get("summary", p.get("buzz", "")), 40)
        twitter = p.get("twitter", "")
        catalyst_raw = p.get("catalyst", "")
        catalyst = _clip(_abbreviate_numbers(catalyst_raw), 50)

        catalyst_html = ""
        if catalyst:
            catalyst_html = f'<div class="catalyst">🔥 {catalyst}</div>'

        cards_html += f"""
            <div class="card">
                <div class="card-top"><span>{emoji} {_clip(category, 12)}</span><span class="twitter">{twitter}</span></div>
                <h2 class="project-name">{name}</h2>
                <div class="desc">{summary}</div>
                {catalyst_html}
            </div>"""


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
.desc {{ font-size: 15px; color: #1C1C1C; line-height: 1.4; flex-grow: 1;
    overflow: hidden; max-height: 2.8em;
}}
.catalyst {{
    background-color: #FF3A2D; color: #FFF;
    font-size: 12px; font-weight: 700;
    padding: 5px 10px; display: inline-block;
    overflow: hidden; max-height: 3.36em;
    overflow-wrap: break-word; word-break: break-all;
    margin-top: 10px;
    border-radius: 4px; line-height: 1.4;
    max-width: 95%;
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
</div>
</body>
</html>"""

    return html


def generate_card_image(html: str, output_path: str) -> str:
    """
    用 Playwright 无头浏览器渲染 HTML 配图并截取 .canvas 元素为 PNG

    注意: Playwright Sync API 不能在 asyncio 事件循环中运行，
    因此用 subprocess 启动独立 Python 进程执行截图。

    Args:
        html: 完整 HTML 字符串
        output_path: PNG 保存路径

    Returns:
        保存路径
    """
    import subprocess
    import tempfile
    import logging
    logger = logging.getLogger("card_generator")

    # 把 HTML 写入临时文件（避免命令行转义问题）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        html_tmp = f.name

    # 截图脚本
    script = f"""
import sys
from playwright.sync_api import sync_playwright

html_path = r"{html_tmp}"
output_path = r"{output_path}"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{"width": 1400, "height": 800}}, device_scale_factor=4)
    page.set_content(html, wait_until="networkidle")
    page.wait_for_timeout(1500)
    canvas = page.query_selector(".canvas")
    if canvas:
        canvas.screenshot(path=output_path, type="png")
    else:
        page.screenshot(path=output_path, type="png")
    browser.close()

import os
os.unlink(html_path)
print("OK")
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script)
        script_path = f.name

    try:
        import sys
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            logger.info(f"🖼️ 配图 PNG: {output_path}")
        else:
            logger.error(f"PNG 生成失败: {result.stderr}")
    finally:
        import os
        try:
            os.unlink(script_path)
        except OSError:
            pass
        try:
            os.unlink(html_tmp)
        except OSError:
            pass

    return output_path


def save_card(projects: list[dict], date_str: str = None) -> str:
    """
    生成并保存配图 HTML + PNG 文件

    Returns:
        HTML 保存路径
    """
    date_str = date_str or cn_now().strftime("%Y%m%d")
    html = generate_card_html(projects, date_str)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 保存 HTML
    html_path = REPORTS_DIR / f"card_{date_str}.html"
    html_path.write_text(html, encoding="utf-8")

    # 用 Playwright 生成 PNG
    png_path = REPORTS_DIR / f"card_{date_str}.png"
    try:
        generate_card_image(html, str(png_path))
    except Exception as e:
        import logging
        logging.getLogger("card_generator").error(f"PNG 生成失败: {e}")

    return str(html_path)
