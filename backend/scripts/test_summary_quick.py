"""Quick test: check enrichment summary quality with round4 data"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.daily_report_service import _enrich_projects_from_analysis

R4 = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round4"
files = [
    ("Giza", "strat_FINAL_Giza_20260301_192229.md", "DeFi AI"),
    ("Taiko", "strat_FINAL_Taiko_20260301_193113.md", "Layer2"),
    ("Kaito AI", "strat_FINAL_Kaito AI_20260301_193338.md", "AI"),
    ("Chiliz", "strat_FINAL_Chiliz_20260301_194518.md", "SportFi"),
    ("Kyber Network", "strat_FINAL_Kyber Network_20260301_194743.md", "DeFi"),
    ("Parallel", "strat_FINAL_Parallel_20260301_193952.md", "GameFi"),
]
projects, analysis = [], []
for name, fname, cat in files:
    full = (R4 / fname).read_text(encoding="utf-8")
    m = re.search(r"##\s*Surf.*?\n+(.*)", full, re.DOTALL)
    content = m.group(1).strip() if m else full
    projects.append({"name": name, "category": cat, "buzz": ""})
    analysis.append({"name": name, "content": content})

enriched = _enrich_projects_from_analysis(projects, analysis)
for p in enriched:
    print(f"{p['name']:16s} | {p.get('summary', '(none)')}")
    if p.get("catalyst"):
        print(f"{'':16s} | catalyst: {p['catalyst']}")
