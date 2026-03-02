"""
测试 _enrich_projects_from_analysis — 用 02-28 的真实数据
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.daily_report_service import _enrich_projects_from_analysis

PROJECTS_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "projects"

# 模拟侦察官输出（只有基础信息）
scout_projects = [
    {"name": "Dicey", "twitter": "@diceyhq", "category": "", "buzz": "Web3"},
    {"name": "NEAR AI", "twitter": "@near_ai", "category": "", "buzz": "AI/Web3"},
    {"name": "Perplexity", "twitter": "@perplexity_ai", "category": "", "buzz": "AI"},
    {"name": "DX Research Group", "twitter": "@dxrgai", "category": "", "buzz": "AI"},
]

# 模拟策略官输出（读取真实报告文件）
analysis_results = []
for p in scout_projects:
    # 文件名匹配
    name = p["name"].replace(" ", "_")
    path = PROJECTS_DIR / f"{name}_20260228.md"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        analysis_results.append({"name": p["name"], "content": content, "error": None})
    else:
        print(f"⚠️ 文件不存在: {path}")
        analysis_results.append({"name": p["name"], "content": "", "error": "file not found"})

# 测试 enrichment
enriched = _enrich_projects_from_analysis(scout_projects, analysis_results)

print("\n📋 Enrichment 结果:\n")
for p in enriched:
    print(f"  {p['name']:20s}")
    print(f"    summary:  {p.get('summary', '(无)')}")
    print(f"    catalyst: {p.get('catalyst', '(无)')}")
    print()
