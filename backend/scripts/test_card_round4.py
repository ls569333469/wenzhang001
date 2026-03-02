"""Generate card from round4 enriched data (no LLM calls)"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.daily_report_service import _enrich_projects_from_analysis
from app.services.card_generator import generate_card_html

R4 = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round4"
files = [
    ("Giza", "strat_FINAL_Giza_20260301_192229.md", "DeFi AI", "@gizatechxyz"),
    ("Taiko", "strat_FINAL_Taiko_20260301_193113.md", "Layer2", "@taikoxyz"),
    ("Kaito AI", "strat_FINAL_Kaito AI_20260301_193338.md", "AI", "@KaitoAI"),
    ("Chiliz", "strat_FINAL_Chiliz_20260301_194518.md", "SportFi", "@chiliz"),
    ("Kyber Network", "strat_FINAL_Kyber Network_20260301_194743.md", "DeFi", "@KyberNetwork"),
    ("Parallel", "strat_FINAL_Parallel_20260301_193952.md", "GameFi", "@ParallelTCG"),
]
projects, analysis = [], []
for name, fname, cat, tw in files:
    full = (R4 / fname).read_text(encoding="utf-8")
    m = re.search(r"##\s*Surf.*?\n+(.*)", full, re.DOTALL)
    content = m.group(1).strip() if m else full
    projects.append({"name": name, "category": cat, "buzz": "", "twitter": tw})
    analysis.append({"name": name, "content": content})

enriched = _enrich_projects_from_analysis(projects, analysis)

# Print summaries
print("\n=== Enrichment Results ===")
for p in enriched:
    s = p.get("summary", "(none)")
    c = p.get("catalyst", "")
    print(f"  {p['name']:16s} | {s}")
    if c:
        print(f"  {'':16s} | catalyst: {c}")

# Generate card
html = generate_card_html(enriched, "20260302")
out = R4.parent.parent / "card_round4_enriched.html"
out.write_text(html, encoding="utf-8")
print(f"\nCard saved: {out}")
