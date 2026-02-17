"""
P23 Phase 0: Google Sheets 初始化脚本
- 0a: 重命名现有 Tab (mimeng→style_mimeng, banfo→style_banfo)
- 0b: 新建 materials Tab + 17列表头

运行: python backend/scripts/setup_p23_sheets.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.services.google_sheets_source import google_sheets_source

RENAMES = {
    "_registry": "web3_knowledge",
    "mimeng": "style_mimeng",
    "banfo": "style_banfo",
}

MATERIALS_HEADERS = [
    "抓取日期",
    "发布时间",
    "时效性",
    "来源",
    "内容类型",
    "标题",
    "URL",
    "正文原文",
    "核心摘要",
    "质量评分",
    "评分理由",
    "事实类型",
    "关键词",
    "项目/人名/代币",
    "推荐模式",
    "内容指纹",
    "状态",
]


def run():
    print("🔧 P23 Phase 0: Google Sheets 初始化\n" + "=" * 50)

    if not google_sheets_source._init_client():
        print("❌ Google Sheets 连接失败")
        sys.exit(1)

    spreadsheet = google_sheets_source._spreadsheet

    # List current worksheets
    worksheets = spreadsheet.worksheets()
    ws_names = [ws.title for ws in worksheets]
    print(f"\n📋 现有 Tab: {ws_names}")

    # ===== 0a: 重命名 =====
    print("\n--- 0a: 重命名 Tab ---")
    for old_name, new_name in RENAMES.items():
        if old_name in ws_names:
            if new_name in ws_names:
                print(f"  ⏭️  '{old_name}' 已是 '{new_name}'，跳过")
            else:
                ws = spreadsheet.worksheet(old_name)
                ws.update_title(new_name)
                print(f"  ✅ '{old_name}' → '{new_name}'")
        elif new_name in ws_names:
            print(f"  ✅ '{new_name}' 已存在（可能已重命名过）")
        else:
            print(f"  ⚠️  '{old_name}' 不存在，跳过")

    # Refresh worksheet list
    worksheets = spreadsheet.worksheets()
    ws_names = [ws.title for ws in worksheets]

    # ===== 0b: 新建 materials Tab =====
    print("\n--- 0b: 新建 materials Tab ---")
    if "materials" in ws_names:
        print("  ✅ 'materials' Tab 已存在")
        ws = spreadsheet.worksheet("materials")
        # Check if headers are set
        existing_headers = ws.row_values(1)
        if not existing_headers or len(existing_headers) < len(MATERIALS_HEADERS):
            ws.update('A1', [MATERIALS_HEADERS])
            print(f"  ✅ 表头已更新 ({len(MATERIALS_HEADERS)} 列)")
        else:
            print(f"  ✅ 表头已存在 ({len(existing_headers)} 列)")
    else:
        ws = spreadsheet.add_worksheet(
            title="materials",
            rows=1000,
            cols=len(MATERIALS_HEADERS)
        )
        ws.update('A1', [MATERIALS_HEADERS])
        print(f"  ✅ 'materials' Tab 创建成功 ({len(MATERIALS_HEADERS)} 列表头)")

    # ===== Summary =====
    worksheets = spreadsheet.worksheets()
    ws_names = [ws.title for ws in worksheets]
    print(f"\n📋 最终 Tab 列表: {ws_names}")
    print("\n🎉 Phase 0a/0b 完成！")


if __name__ == "__main__":
    run()
