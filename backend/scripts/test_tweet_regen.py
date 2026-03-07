"""Quick test: re-run tweet writer with existing report data"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from dotenv import load_dotenv
load_dotenv()

from app.services.daily_report_service import run_tweet_writer
from pathlib import Path

report = Path("../reports/research/daily_research_20260303.md").read_text(encoding="utf-8")
projects = [
    {"name":"XOOB","twitter":"@xoobnetwork","category":"Infra"},
    {"name":"Qwen","twitter":"@alibaba_qwen","category":"AI"},
    {"name":"VoidCo","twitter":"@voidcoai","category":"AI"},
    {"name":"Archer","twitter":"@archer_money","category":"DeFi"},
    {"name":"Algod","twitter":"@algodtrading","category":"Infra"},
    {"name":"Quantu","twitter":"@quantu_ai","category":"AI"},
    {"name":"Math Academy","twitter":"@_mathacademy_","category":"AI"},
]

print("Running tweet writer...")
tweets = run_tweet_writer(report, projects)
print(f"\nTotal tweets: {len(tweets)}")
for t in tweets:
    print(f"\n=== {t['name']} ({t['char_count']} chars) ===")
    print(t["text"][:300])
