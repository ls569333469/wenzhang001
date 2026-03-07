r"""
P31: 用 round4 策略官测试报告跑下游管道
使用 prompt_test/strategist/round4 的真实 Surf 输出

用法:
    cd d:\AI_Projects\2026001\backend
    python scripts/test_pipeline_round4.py
"""
import sys
import time
import asyncio
import re
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

ROUND4_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round4"
OUTPUT_DATE = "20260303"

# round4 报告 → (文件名, 项目在侦察官中的信息)
ROUND4_PROJECTS = [
    {
        "file": "strat_FINAL_Giza_20260301_192229.md",
        "name": "Giza",
        "twitter": "@gizatechxyz",
        "category": "DeFi AI",
        "buzz": "DeFi AI代理",
    },
    {
        "file": "strat_FINAL_Taiko_20260301_193113.md",
        "name": "Taiko",
        "twitter": "@taikoxyz",
        "category": "Layer2",
        "buzz": "ZK-Rollup L2",
    },
    {
        "file": "strat_FINAL_Kaito AI_20260301_193338.md",
        "name": "Kaito AI",
        "twitter": "@KaitoAI",
        "category": "AI",
        "buzz": "社交情报",
    },
    {
        "file": "strat_FINAL_Chiliz_20260301_194518.md",
        "name": "Chiliz",
        "twitter": "@chiliz",
        "category": "SportFi",
        "buzz": "体育粉丝代币",
    },
    {
        "file": "strat_FINAL_Kyber Network_20260301_194743.md",
        "name": "Kyber Network",
        "twitter": "@KyberNetwork",
        "category": "DeFi",
        "buzz": "DEX流动性聚合",
    },
    {
        "file": "strat_FINAL_Parallel_20260301_193952.md",
        "name": "Parallel",
        "twitter": "@ParallelTCG",
        "category": "GameFi",
        "buzz": "NFT卡牌游戏",
    },
]


def extract_surf_content(full_text: str) -> str:
    """从 round4 测试报告中提取 Surf 返回的原始内容（去掉元数据和 prompt 部分）"""
    # 找到 "## 📥 Surf 完整返回" 之后的内容
    match = re.search(r"##\s*📥\s*Surf\s*完整返回\s*\n+(.*)", full_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # fallback: 找第一个 ## 📊 之后的全部
    match2 = re.search(r"(##\s*📊.*)", full_text, re.DOTALL)
    if match2:
        return match2.group(1).strip()
    return full_text


def load_round4_data():
    """加载 round4 策略官报告"""
    scout_projects = []
    analysis_results = []

    for p in ROUND4_PROJECTS:
        path = ROUND4_DIR / p["file"]
        if not path.exists():
            print(f"  ❌ 未找到: {p['file']}")
            continue

        full_text = path.read_text(encoding="utf-8")
        content = extract_surf_content(full_text)
        print(f"  ✅ {p['name']:16s} ({len(content)} chars)")

        scout_projects.append({
            "name": p["name"],
            "twitter": p["twitter"],
            "category": p["category"],
            "buzz": p["buzz"],
        })
        analysis_results.append({
            "name": p["name"],
            "content": content,
            "elapsed": 0,
            "error": None,
        })

    return scout_projects, analysis_results


async def main():
    start = time.time()
    _ensure_dirs()

    print("=" * 60)
    print("🧪 P31 管道测试（Round4 策略官报告）")
    print(f"📅 输出日期: {OUTPUT_DATE}")
    print("=" * 60)

    # Step 0: 加载数据
    print("\n📂 加载 Round4 策略官报告...")
    projects, analysis_results = load_round4_data()
    print(f"\n📊 加载 {len(projects)} 个报告")

    if not projects:
        print("❌ 无可用报告，退出")
        return

    # Step 4.5: 数据回填
    print("\n📋 Step 4.5: 提取 summary + catalyst...")
    enriched = _enrich_projects_from_analysis(projects, analysis_results)
    for p in enriched:
        s = p.get("summary", "(无)")
        c = p.get("catalyst", "(无)")
        print(f"  {p['name']:16s} | summary: {s}")
        print(f"  {'':16s} | catalyst: {c}")

    # Step 3: 审核官
    print("\n📝 Step 3: 审核官总结归纳...")
    summary = run_summarizer(analysis_results)
    print(f"  ✅ 审核官输出 {len(summary)} 字符")

    # Step 4: 写手
    print(f"\n✍️ Step 4: 写手组装日报...")
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
    print(f"\n✨ Step 7: 润色定稿...")
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
