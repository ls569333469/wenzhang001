r"""
P31: 从写手开始测试日报拼接效果
跳过侦察官+策略官，直接用 02-28 现有报告跑 审核官→写手→配图→推文→润色

用法:
    cd d:\AI_Projects\2026001\backend
    python scripts/test_pipeline_from_writer.py
"""
import sys
import time
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.daily_report_service import (
    run_summarizer,
    run_writer,
    run_card_generator,
    run_tweet_writer,
    run_polisher,
    _enrich_projects_from_analysis,
    _save_daily_report,
    _save_tweets,
    _ensure_dirs,
)

PROJECTS_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "projects"
SOURCE_DATE = "20260228"  # 策略官报告的日期
OUTPUT_DATE = "20260303"  # 输出日期


def load_existing_data():
    """从现有 02-28 策略官报告加载数据"""

    # 模拟侦察官输出（scout_20260228.md 的项目列表，只取6个）
    scout_projects = [
        {"name": "Dicey", "twitter": "@diceyhq", "category": "Web3", "buzz": "Web3 iGaming"},
        {"name": "NEAR AI", "twitter": "@near_ai", "category": "AI/Web3", "buzz": "隐私AI代理"},
        {"name": "Perplexity", "twitter": "@perplexity_ai", "category": "AI", "buzz": "AI搜索"},
        {"name": "DX Research Group", "twitter": "@dxrgai", "category": "AI", "buzz": "AI交易代理"},
        {"name": "techdollar", "twitter": "@techdollarhq", "category": "AI/Web3", "buzz": "AI/Web3"},
        {"name": "sealaunch intelligence", "twitter": "@sealaunch_", "category": "Web3", "buzz": "Launch Intelligence"},
    ]

    # 读取已有策略官报告
    analysis_results = []
    for p in scout_projects:
        name = p["name"]
        # 尝试多种文件名
        candidates = [
            PROJECTS_DIR / f"{name.replace(' ', '_')}_{SOURCE_DATE}.md",
            PROJECTS_DIR / f"{name}_{SOURCE_DATE}.md",
        ]
        content = ""
        for path in candidates:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                print(f"  ✅ {path.name} ({len(content)} chars)")
                break
        if not content:
            print(f"  ❌ 未找到: {name}")

        analysis_results.append({
            "name": name,
            "content": content,
            "elapsed": 0,
            "error": None if content else "file not found",
        })

    return scout_projects, analysis_results


async def main():
    start = time.time()
    _ensure_dirs()

    print("=" * 60)
    print("🧪 P31 日报拼接测试（从写手开始）")
    print(f"📅 输出日期: {OUTPUT_DATE}")
    print("=" * 60)

    # Step 0: 加载现有数据
    print("\n📂 加载策略官报告...")
    projects, analysis_results = load_existing_data()
    ok_count = sum(1 for r in analysis_results if r.get("content"))
    print(f"\n📊 成功加载 {ok_count}/{len(projects)} 个报告")

    if ok_count == 0:
        print("❌ 无可用报告，退出")
        return

    # Step 4.5: 数据回填
    print("\n📋 Step 4.5: 从策略官报告提取 summary + catalyst...")
    enriched = _enrich_projects_from_analysis(projects, analysis_results)
    for p in enriched:
        print(f"  {p['name']:25s} | summary: {p.get('summary', '(无)')[:40]}")
        if p.get("catalyst"):
            print(f"  {'':25s} | catalyst: {p['catalyst']}")

    # Step 3: 审核官
    print("\n📝 Step 3: 审核官总结归纳...")
    summary = run_summarizer(analysis_results)
    print(f"  ✅ 审核官输出 {len(summary)} 字符")

    # Step 4: 写手
    print("\n✍️ Step 4: 写手组装日报...")
    draft = run_writer(summary, enriched, OUTPUT_DATE)
    print(f"  ✅ 日报草稿 {len(draft)} 字符")

    # Step 5: 配图
    print("\n📸 Step 5: 生成配图...")
    card_path = run_card_generator(enriched, OUTPUT_DATE)
    print(f"  ✅ 配图: {card_path}")

    # Step 6: 推文
    print("\n🐦 Step 6: 生成推文...")
    tweets = run_tweet_writer(summary, enriched)
    if tweets:
        _save_tweets(tweets, OUTPUT_DATE)
        print(f"  ✅ {len(tweets)} 条推文")
        for t in tweets[:3]:
            print(f"    - {t['name']}: {t['char_count']} chars")
    else:
        print("  ⚠️ 推文生成失败")

    # Step 7: 润色官
    print("\n✨ Step 7: 润色定稿...")
    final = run_polisher(draft)
    report_path = _save_daily_report(final, OUTPUT_DATE)
    print(f"  ✅ 日报: {report_path}")

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"🎉 完成！耗时 {elapsed:.0f}s")
    print(f"  📄 日报: reports/research/daily_research_{OUTPUT_DATE}.md")
    print(f"  📸 配图: reports/research/card_{OUTPUT_DATE}.html")
    print(f"  🐦 推文: reports/research/tweets_{OUTPUT_DATE}.md")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
