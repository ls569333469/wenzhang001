import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source as gs

data = gs._load_sheet_data("风格_半佛")
print(f"半佛样本总数: {len(data)}")

has_ev = [x for x in data if x.get("emotional_valence")]
has_lp = [x for x in data if x.get("logic_pattern")]
print(f"有情绪标注: {len(has_ev)}")
print(f"有逻辑公式: {len(has_lp)}")

if has_lp:
    print("\n前3条带逻辑公式的样本:")
    for x in has_lp[:3]:
        ev = x.get("emotional_valence", "")
        lp = x.get("logic_pattern", "")
        content = str(x.get("content", ""))[:50]
        print(f"  [{ev}] {lp} | {content}")
else:
    print("\n半佛样本中没有逻辑公式数据")
    if data:
        print("第一条样本的所有字段:")
        for k, v in data[0].items():
            print(f"  {k}: {str(v)[:60]}")
