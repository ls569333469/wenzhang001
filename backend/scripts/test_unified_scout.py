"""P32-C: Test scout pipeline with unified prompt"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.surf_service import SurfService

print("=" * 60)
print("  P32-C: 侦察官统一流程测试")
print("=" * 60)

# Step 1: Test Sheets sources
print("\n--- Step 1: 读取信源账号 ---")
try:
    from app.services.research_sheet import research_sheet_service
    sources = research_sheet_service.get_scout_sources()
    print(f"✅ 读取到 {len(sources)} 个信源")
    for s in sources:
        print(f"   {s['handle']} — {s['desc']}")
except Exception as e:
    print(f"⚠️ Sheets 失败: {e}")
    sources = [
        {"handle": "@leakmealpha", "desc": "Crypto KOL Tracker"},
    ]

# Step 2: Test template rendering
print("\n--- Step 2: 渲染 scout.jinja2 模板 ---")
from app.services.daily_report_service import _render_research_template

accounts_text = "\n".join(
    f"{i+1}. {s['handle']} — {s['desc']}"
    for i, s in enumerate(sources)
)
prompt = _render_research_template("scout.jinja2", {
    "accounts": accounts_text,
    "account_count": len(sources),
})
if prompt:
    print(f"✅ 模板渲染成功 ({len(prompt)} 字符)")
    print(f"   前 200 字:\n   {prompt[:200]}")
else:
    print("❌ 模板渲染失败")
    sys.exit(1)

# Step 3: Call Surf API
print("\n--- Step 3: 调用 Surf API ---")
surf = SurfService()
result = surf.call(
    model="surf-1.5",
    user_prompt=prompt,
    abilities=["search"],
    timeout=300,
)

print(f"Status: {result['status']}")
print(f"Elapsed: {result.get('elapsed', 0):.1f}s")

if result.get("error"):
    print(f"Error: {result['error'][:500]}")

if result.get("content"):
    content = result["content"]
    print(f"Content length: {len(content)} 字符")
    print(f"\n--- 原始输出 ---")
    print(content[:2000])
else:
    print("❌ 无内容返回")

# Step 4: Parse projects
print("\n--- Step 4: 解析项目 ---")
if result.get("content"):
    from app.agents.research.scout import _parse_projects_from_text
    projects = _parse_projects_from_text(result["content"])
    print(f"✅ 解析出 {len(projects)} 个项目")
    for p in projects:
        print(f"   {p.get('name', '?')} ({p.get('twitter', '')}) — {p.get('category', '')}")

print("\n" + "=" * 60)
print("  测试完成！")
print("=" * 60)
