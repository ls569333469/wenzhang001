"""Regenerate tweets + card from existing report markdown (no JSON needed)"""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from app.services.daily_report_service import run_tweet_writer, _save_tweets
from app.services.card_generator import generate_card_html, pick_best_catalyst

REPORT_DATE = "20260305"  # 报告数据来源日期
PUBLISH_DATE = "20260305"  # 发布日期（配图/推文显示的日期）
RESEARCH_DIR = Path("d:/AI_Projects/2026001/reports/research")

# 1. Load report markdown
report_file = RESEARCH_DIR / f"daily_research_{REPORT_DATE}.md"
report = report_file.read_text(encoding="utf-8")
print(f"Report loaded: {len(report)} chars")

# 2. Parse projects from markdown
# Extract from overview table: | 1 | **XOOB** (@xoobnetwork) | Infra | +2 | ... |
projects = []
table_pattern = re.compile(r'\| \d+ \| \*\*(.+?)\*\* \((@\w+)\) \| (.+?) \| \+(\d+) \| (.+?) \|')
for m in table_pattern.finditer(report):
    name, twitter, category, kol, buzz = m.groups()
    projects.append({
        "name": name.strip(),
        "twitter": twitter.strip(),
        "category": category.strip(),
        "kol_24h": int(kol),
        "buzz": buzz.strip(),
    })

print(f"Parsed {len(projects)} projects from table")

# 3. Extract summary and catalysts for each project  
for p in projects:
    name = p["name"]
    # Find project section: "## 1. edgeX_exchange (@edgeX_exchange)" or "## edgeX_exchange"
    section_match = re.search(
        rf'^## (?:\d+\.\s*)?{re.escape(name)}.*?(?=^## \d+\.|^## 📋|\Z)',
        report, re.MULTILINE | re.DOTALL
    )
    if not section_match:
        continue
    section = section_match.group(0)
    
    # Extract one-line summary (stops at next ## subsection)
    summary_match = re.search(r'📊 一句话定位\s*\n(.+?)(?:\n## |\n---|\Z)', section, re.DOTALL)
    if summary_match:
        p["summary"] = summary_match.group(1).strip()[:80]
    
    # Extract catalysts (stops at next ## subsection or ---)
    catalyst_match = re.search(r'🔥 近期催化剂\s*\n(.+?)(?:\n## |\n---|\Z)', section, re.DOTALL)
    if catalyst_match:
        catalyst_text = catalyst_match.group(1).strip()
        # Pick best catalyst
        catalysts = [c.strip() for c in catalyst_text.split('\n') if c.strip()]
        p["catalyst"] = pick_best_catalyst(catalysts) if catalysts else ""

for p in projects:
    print(f"  {p['name']}: summary={p.get('summary','')[:30]}... catalyst={p.get('catalyst','')[:30]}...")

# 4. Regenerate card (first 6 projects)
card_projects = projects[:6]
card_html = generate_card_html(card_projects, PUBLISH_DATE)
card_path = RESEARCH_DIR / f"card_{PUBLISH_DATE}.html"
card_path.write_text(card_html, encoding="utf-8")
print(f"\nCard saved: {card_path.name} ({len(card_projects)} projects)")

# 5. Regenerate tweets (same 6 projects)
print(f"Generating tweets for {len(card_projects)} projects...")
tweets = run_tweet_writer(report, card_projects)
if tweets:
    tweets_path = _save_tweets(tweets, PUBLISH_DATE)
    print(f"Tweets saved: {tweets_path}")
    print(f"Total: {len(tweets)} tweets")
    print(f"\n{'='*50}")
    print(f"Main Tweet ({tweets[0]['char_count']} chars):")
    print(f"{'='*50}")
    print(tweets[0]['text'])
else:
    print("Tweet generation FAILED")
