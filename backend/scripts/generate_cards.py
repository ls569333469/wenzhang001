"""
P31: Layer 4 扩展 — HTML 配图 + 推文文案生成
从 JSON 中间数据 → 渲染 HTML 配图 + 生成推文

用法: python scripts/generate_cards.py [json_path]
默认: 使用今天的 data_YYYYMMDD.json
"""
import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research"
TODAY = datetime.now().strftime("%Y%m%d")
TODAY_DISPLAY = datetime.now().strftime("%Y.%m.%d")


def clean_name(name: str) -> str:
    """清理项目名中的多余字符"""
    return name.strip().strip("|").strip()


def extract_card_info(project: dict) -> dict:
    """从项目分析文本中提取配图所需的关键信息（3 条）"""
    analysis = project.get("analysis", "")
    name = project.get("name", "")
    category = project.get("category", "")
    stage = project.get("stage", "concept")
    twitter = project.get("twitter", "")

    # 提取各章节
    sections = {}
    current = None
    for line in analysis.split("\n"):
        h2 = re.match(r"^##\s+(.+)", line)
        if h2:
            current = h2.group(1).strip()
            sections[current] = []
        elif current:
            sections[current].append(line)

    def get_section_text(keywords: list) -> str:
        for key, lines in sections.items():
            for kw in keywords:
                if kw in key:
                    text = "\n".join(lines).strip()
                    # 清理 Markdown 表格残留
                    text = re.sub(r"\|[^|\n]+\|[^|\n]+\|[^|\n]*\|", "", text)
                    text = re.sub(r"\|[-\s:]+\|", "", text)
                    text = re.sub(r"^\|.*\|$", "", text, flags=re.MULTILINE)
                    text = re.sub(r"\n{2,}", "\n", text).strip()
                    return text[:200]
        return ""

    # 提取 3 条关键信息 — 根据项目阶段选择不同维度
    items = []

    if stage == "pre_tge":
        dims = [
            ("参与机会", ["关键事件", "参与机会"]),
            ("筹码结构", ["筹码结构"]),
            ("风险提示", ["风险清单", "风险"]),
        ]
    elif stage == "launched":
        dims = [
            ("市场数据", ["市场数据"]),
            ("近期催化", ["近期催化", "催化剂"]),
            ("风险提示", ["风险清单", "风险"]),
        ]
    elif stage == "mature":
        dims = [
            ("一句话定位", ["一句话定位"]),
            ("近期催化", ["近期催化", "催化剂"]),
            ("结论", ["结论"]),
        ]
    else:  # concept, funded
        dims = [
            ("一句话定位", ["一句话定位"]),
            ("参与机会", ["关键事件", "参与机会"]),
            ("团队背书", ["团队", "背书"]),
        ]

    for label, keywords in dims:
        text = get_section_text(keywords)
        if text:
            # 截取第一段有效内容
            first_para = text.split("\n")[0].strip()
            if first_para and len(first_para) > 10:
                items.append({"label": label, "value": first_para[:40]})

    # 确保至少有 1 条
    if not items:
        conclusion = get_section_text(["结论"])
        if conclusion:
            items.append({"label": "结论", "value": conclusion[:120]})
        else:
            items.append({"label": "简介", "value": f"{name} - {category}"})

    return {
        "name": clean_name(name),
        "twitter": twitter,
        "category": category,
        "stage": stage,
        "items": items[:3],
    }


def extract_conclusion(analysis: str) -> str:
    """提取结论文本"""
    match = re.search(r"##.*?结论\s*\n(.+?)(?:\n##|\Z)", analysis, re.DOTALL)
    if match:
        return match.group(1).strip().split("\n")[0]
    return ""


def generate_tweet(project: dict) -> str:
    """为单个项目生成推文文案（280 字内）"""
    name = project.get("name", "")
    twitter = project.get("twitter", "")
    category = project.get("category", "")
    stage = project.get("stage", "")
    kol = project.get("kol_24h", 0)
    analysis = project.get("analysis", "")

    # 提取一句话定位
    positioning = ""
    match = re.search(r"一句话定位\s*\n(.+?)(?:\n##|\n\n)", analysis, re.DOTALL)
    if match:
        positioning = match.group(1).strip()

    # 提取结论
    conclusion = extract_conclusion(analysis)

    # 阶段 emoji
    stage_tag = {
        "concept": "💡 早期",
        "funded": "💰 已融资",
        "pre_tge": "🎯 Pre-TGE",
        "launched": "🚀 已上线",
        "mature": "🏛️ 成熟",
    }.get(stage, "")

    # 组装推文
    parts = []
    parts.append(f"🔥 {name} ({twitter})")
    if stage_tag:
        parts.append(f"{stage_tag} | {category}")
    if kol:
        parts.append(f"📊 24h KOL 关注 +{kol}")
    if positioning:
        parts.append(f"\n{positioning[:100]}")
    if conclusion:
        parts.append(f"\n🎯 {conclusion[:80]}")
    parts.append(f"\n#Web3 #Alpha #{name.replace(' ', '')}")

    tweet = "\n".join(parts)
    # 截断到 280 字
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    return tweet


def render_html(cards: list, date_str: str) -> str:
    """渲染 HTML 配图"""
    card_html = ""
    for card in cards:
        items_html = ""
        for item in card["items"]:
            # 高亮数字和关键词
            value = item["value"]
            value = re.sub(r"(\$[\d,.]+[MBK]?)", r'<span class="highlight">\1</span>', value)
            value = re.sub(r"(\d+%\+?)", r'<span class="highlight">\1</span>', value)
            # 高亮警告词
            value = re.sub(r"(高度匿名|rug pull|风险|高波动)", r'<span class="warning">\1</span>', value)

            items_html += f"""
                    <div class="info-item">
                        <span class="info-label">{item['label']}</span>
                        <span class="info-value">{value}</span>
                    </div>"""

        stage_labels = {
            "concept": "💡", "funded": "💰", "pre_tge": "🎯",
            "launched": "🚀", "mature": "🏛️",
        }
        stage_icon = stage_labels.get(card["stage"], "")

        card_html += f"""
            <div class="card">
                <div class="tag">{stage_icon} {card['category']}</div>
                <div class="project-name">{card['name']}</div>
                <div class="info-list">{items_html}
                </div>
            </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web3 Alpha Daily - {date_str}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: #050505;
            background-image:
                radial-gradient(circle at 15% 50%, rgba(20, 25, 35, 1), transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(15, 20, 25, 1), transparent 50%);
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            display: flex; justify-content: center; align-items: center;
            padding: 40px; min-height: 100vh; color: #e5e7eb;
        }}
        .canvas {{
            width: 1200px; height: 675px;
            background: rgba(10, 10, 12, 0.4);
            border: 1px solid #1f2025; border-radius: 24px;
            padding: 40px 48px; display: flex; flex-direction: column;
            box-shadow: 0 40px 80px rgba(0, 0, 0, 0.8);
            position: relative; overflow: hidden;
        }}
        .header {{
            display: flex; justify-content: space-between; align-items: flex-end;
            margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 20px;
        }}
        .header-left {{ display: flex; flex-direction: column; gap: 8px; }}
        .title {{
            font-size: 28px; font-weight: 800; letter-spacing: 2px;
            background: linear-gradient(90deg, #ffffff, #a1a1aa);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            font-size: 14px; color: #6b7280; letter-spacing: 4px; text-transform: uppercase;
        }}
        .date-badge {{
            background: #f5b300; color: #000; padding: 6px 16px;
            border-radius: 20px; font-size: 14px; font-weight: 700; letter-spacing: 1px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px; flex: 1; align-content: start;
        }}
        .card {{
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px; padding: 32px 24px;
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            display: flex; flex-direction: column; position: relative;
        }}
        .card::before {{
            content: ''; position: absolute; top: 0; left: 24px; right: 24px;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        }}
        .tag {{
            font-size: 12px; color: #9ca3af; margin-bottom: 16px;
            display: flex; align-items: center; gap: 6px;
        }}
        .project-name {{
            font-size: 22px; font-weight: 700; color: #ffffff;
            margin-bottom: 24px; line-height: 1.3;
        }}
        .info-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .info-item {{ display: flex; flex-direction: column; gap: 6px; }}
        .info-label {{
            font-size: 12px; color: #52525b; text-transform: uppercase;
            letter-spacing: 1px; font-weight: 600;
        }}
        .info-value {{ font-size: 13px; color: #d4d4d8; line-height: 1.4; }}
        .highlight {{ color: #38bdf8; font-weight: 500; }}
        .warning {{ color: #fbbf24; }}
    </style>
</head>
<body>
    <div class="canvas">
        <div class="header">
            <div class="header-left">
                <div class="subtitle">Institutional Grade Intel</div>
                <div class="title">WEB3 ALPHA DAILY</div>
            </div>
            <div class="date-badge">{date_str}</div>
        </div>
        <div class="grid">
{card_html}
        </div>
    </div>
</body>
</html>"""
    return html


def main():
    # 读取 JSON
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        json_path = OUTPUT_DIR / f"data_{TODAY}.json"

    if not json_path.exists():
        print(f"❌ JSON 文件不存在: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    projects = data.get("projects", [])
    # 统一清理项目名（去除 Markdown 表格解析残留的 | 前缀）
    for p in projects:
        p["name"] = clean_name(p.get("name", ""))
    print(f"📦 加载 {len(projects)} 个项目: {json_path.name}")

    # === 生成配图 ===
    print("\n🎨 生成 HTML 配图...")
    cards = [extract_card_info(p) for p in projects]
    html = render_html(cards, TODAY_DISPLAY)

    html_path = OUTPUT_DIR / f"card_{TODAY}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   ✅ HTML 已保存: {html_path}")
    print(f"   📊 {len(cards)} 张卡片")

    # === 生成推文 ===
    print("\n✍️  生成推文文案...")
    tweets = []
    for p in projects:
        tweet = generate_tweet(p)
        tweets.append({"name": p["name"], "tweet": tweet})
        print(f"\n   📝 {p['name']}:")
        print(f"   {'-'*40}")
        for line in tweet.split("\n"):
            print(f"   {line}")
        print(f"   {'-'*40}")
        print(f"   字数: {len(tweet)}")

    # 保存推文文件
    tweet_path = OUTPUT_DIR / f"tweets_{TODAY}.md"
    with open(tweet_path, "w", encoding="utf-8") as f:
        f.write(f"# 推文文案 - {TODAY_DISPLAY}\n\n")
        for t in tweets:
            f.write(f"## {t['name']}\n\n")
            f.write(f"```\n{t['tweet']}\n```\n\n")
            f.write(f"字数: {len(t['tweet'])}\n\n---\n\n")

    print(f"\n   💾 推文已保存: {tweet_path}")
    print(f"\n✅ Done! 文件:")
    print(f"   HTML 配图: {html_path}")
    print(f"   推文文案: {tweet_path}")


if __name__ == "__main__":
    main()
