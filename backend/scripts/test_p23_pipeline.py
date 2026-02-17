"""
P23 Phase 1d: 集成测试脚本
测试: 爬虫 → AI分析 → Sheets写入 完整管线

运行: python scripts/test_p23_pipeline.py [--dry-run] [--count N]
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def test_fetcher(count: int):
    """测试爬虫模块"""
    print("\n" + "=" * 50)
    print("📥 Step 1: 测试 ChainCatcher 爬虫")
    print("=" * 50)

    from app.services.material_fetcher import get_fetcher
    fetcher = get_fetcher("chaincatcher")

    materials = fetcher.fetch_latest(count=count)
    print(f"\n📊 列表结果: {len(materials)} 条素材")

    if not materials:
        return materials

    # Enrich with article details (content + published_at)
    print(f"\n📥 获取文章详情 (最多 {min(count, 10)} 篇)...")
    materials = fetcher.enrich_with_details(materials, max_items=min(count, 10))

    sample = materials[0]
    print(f"\n📌 示例 (第1条):")
    print(f"  标题: {sample.get('title', '')[:60]}")
    print(f"  URL:  {sample.get('url', '')}")
    print(f"  类型: {sample.get('content_type', '')}")
    print(f"  时间: {sample.get('published_at', '')}")
    print(f"  内容: {sample.get('content', '')[:100]}...")

    return materials


def test_analyzer(materials: list, max_analyze: int = 3):
    """测试 AI 分析模块"""
    print("\n" + "=" * 50)
    print("🔍 Step 2: 测试 AI 预筛选")
    print("=" * 50)

    from app.services.material_analyzer import analyze_batch

    # Only analyze a few to save tokens
    subset = materials[:max_analyze]
    analyzed = analyze_batch(subset)

    print(f"\n📊 结果: {len(analyzed)}/{len(subset)} 条已分析")

    for item in analyzed:
        print(f"\n  📌 {item.get('title', '')[:40]}")
        print(f"     摘要: {item.get('summary', '')}")
        print(f"     评分: {item.get('quality_score', '?')}/10")
        print(f"     类型: {item.get('fact_type', '')}")
        print(f"     推荐: {item.get('suggested_modes', [])}")
        print(f"     时效: {item.get('timeliness', '')}")

    return analyzed


def test_sheet_write(analyzed: list, dry_run: bool):
    """测试 Sheets 写入"""
    print("\n" + "=" * 50)
    print("📝 Step 3: 测试 Sheets 写入")
    print("=" * 50)

    from app.services.material_sheet import material_sheet

    # Check dedup
    existing = material_sheet.get_existing_urls()
    print(f"  已有 URL: {len(existing)} 条")

    # Filter out existing
    new_materials = [m for m in analyzed if m.get("url") not in existing]
    print(f"  新素材: {len(new_materials)} 条 (去重后)")

    if dry_run:
        print("  ⏭️  DRY RUN — 跳过实际写入")
        for m in new_materials:
            print(f"     → {m.get('title', '')[:50]}")
        return 0

    if new_materials:
        written = material_sheet.write_materials(new_materials)
        print(f"  ✅ 写入 {written} 条")
        return written
    else:
        print("  ℹ️  无新素材需要写入")
        return 0


def test_sheet_read():
    """测试 Sheets 读取"""
    print("\n" + "=" * 50)
    print("📖 Step 4: 测试 Sheets 读取")
    print("=" * 50)

    from app.services.material_sheet import material_sheet
    items = material_sheet.list_materials()
    print(f"  总计: {len(items)} 条素材")

    if items:
        print(f"  最近一条: {items[-1].get('title', '')[:50]}")
        print(f"  评分分布: ", end="")
        scores = [i.get("quality_score", 0) for i in items]
        for s in range(1, 11):
            count = scores.count(s)
            if count:
                print(f"{s}分×{count} ", end="")
        print()

    return items


def main():
    parser = argparse.ArgumentParser(description="P23 Pipeline Integration Test")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to Sheets")
    parser.add_argument("--count", type=int, default=5, help="Number of items per type to fetch")
    parser.add_argument("--analyze-count", type=int, default=3, help="Max items to analyze with LLM")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip fetching, only test read")
    args = parser.parse_args()

    print("🔧 P23 集成测试")
    print(f"   count={args.count}, analyze={args.analyze_count}, dry_run={args.dry_run}")

    if args.skip_fetch:
        test_sheet_read()
        return

    # Full pipeline
    materials = test_fetcher(args.count)
    if not materials:
        print("\n❌ 爬虫返回空结果，终止")
        return

    analyzed = test_analyzer(materials, max_analyze=args.analyze_count)
    if not analyzed:
        print("\n❌ 分析返回空结果，终止")
        return

    test_sheet_write(analyzed, dry_run=args.dry_run)
    test_sheet_read()

    print("\n" + "=" * 50)
    print("🎉 集成测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
