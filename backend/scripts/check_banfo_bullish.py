import sys, os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()
from app.services.google_sheets_source import google_sheets_source as gs

data = gs._load_sheet_data("风格_半佛")
print(f"半佛样本总数: {len(data)}")

# 搜索与币安/交易所/捧人相关的关键词
keywords = ["币安", "Binance", "CZ", "何一", "BNB", "交易所", "合规", "上市", "上线"]
matches = []
for r in data:
    content = str(r.get("content", ""))
    for kw in keywords:
        if kw.lower() in content.lower():
            matches.append(r)
            break

print(f"与币安/交易所相关: {len(matches)} 条")
for i, r in enumerate(matches[:8]):
    ev = r.get("emotional_valence", "")
    lp = r.get("logic_pattern", "")
    content = str(r.get("content", ""))[:200]
    print(f"\n--- 样本 {i+1} [{ev} | {lp}] ---")
    print(content)

# 也看看"积极"情绪的样本（适合吹捧风格参考）
positive = [r for r in data if r.get("emotional_valence") == "积极"]
print(f"\n\n积极情绪样本总数: {len(positive)}")
print("前3条积极样本:")
for i, r in enumerate(positive[:3]):
    lp = r.get("logic_pattern", "")
    content = str(r.get("content", ""))[:200]
    print(f"\n--- 积极 {i+1} [{lp}] ---")
    print(content)
