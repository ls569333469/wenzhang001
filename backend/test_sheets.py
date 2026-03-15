#!/usr/bin/env python3
"""
容器内 Google Sheets + 去重 诊断脚本
docker cp test_sheets.py quantum-studio-backend-1:/app/test_sheets.py
docker exec quantum-studio-backend-1 python /app/test_sheets.py
"""
import sys, os
sys.path.insert(0, "/app")

print("=" * 60)
print("🔍 Google Sheets + 去重诊断")
print("=" * 60)

# 1. 测试 Sheets 连接
print("\n📋 1. Google Sheets 连接测试:")
try:
    from app.services.google_sheets_source import google_sheets_source as gs
    ok = gs._init_client()
    print(f"  连接: {'✅ 成功' if ok else '❌ 失败'}")
    if ok and gs._spreadsheet:
        print(f"  表格: {gs._spreadsheet.title}")
        tabs = [ws.title for ws in gs._spreadsheet.worksheets()]
        print(f"  Tabs: {tabs}")
except Exception as e:
    print(f"  ❌ 连接失败: {e}")

# 2. 读取投研记录 Tab
print("\n📋 2. 投研记录 Tab 数据:")
try:
    from app.services.research_sheet import research_sheet_service as rss
    records = rss.get_all_records(use_cache=False)
    print(f"  记录数: {len(records)}")
    if records:
        print(f"  列名: {list(records[0].keys())}")
        print(f"\n  最近 5 条记录:")
        for r in records[-5:]:
            name = r.get("项目名", "?")
            time = r.get("上次分析时间", "?")
            cat = r.get("催化剂摘要", "")[:30]
            count = r.get("侦察次数", 0)
            print(f"    {name:20s} | {time} | {cat} | 次数:{count}")
    else:
        print("  ⚠️ 无记录（去重无法生效）")
except Exception as e:
    print(f"  ❌ 读取失败: {e}")
    import traceback
    traceback.print_exc()

# 3. ChromaDB 去重检查
print("\n📋 3. ChromaDB 48h 去重数据:")
try:
    from app.services.chroma_service import chroma_service
    recent = chroma_service.get_recent_analyzed_handles(hours=48)
    print(f"  近48h分析过的项目: {len(recent)}")
    if recent:
        for h in recent[:10]:
            print(f"    - {h}")
    else:
        print("  ⚠️ 无记录（48h去重无法生效）")
except Exception as e:
    print(f"  ❌ ChromaDB 查询失败: {e}")

# 4. 模拟去重
print("\n📋 4. 去重模拟（用上次侦察的项目名）:")
try:
    import glob, re
    # 从最新的 daily_research 中提取项目名
    reports = sorted(glob.glob("/app/reports/research/daily_research_*.md"))
    if reports:
        latest = reports[-1]
        content = open(latest, encoding="utf-8").read()
        projects = re.findall(r"^## \d+\.\s*(.+)", content, re.MULTILINE)
        if not projects:
            projects = re.findall(r"^## (.+)", content, re.MULTILINE)
        
        if projects:
            mock = [{"name": p.strip(), "buzz": "test"} for p in projects[:5]]
            print(f"  模拟项目: {[p['name'] for p in mock]}")
            result = rss.dedup_filter(mock)
            print(f"  去重结果: {len(result)}/{len(mock)} 保留")
        else:
            print("  无法从报告中提取项目名")
    else:
        print("  无报告文件")
except Exception as e:
    print(f"  ❌ 模拟失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
