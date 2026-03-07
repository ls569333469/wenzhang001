"""P32-C: 创建 侦察源 Tab + 初始数据"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source

TAB_NAME = "侦察源"
HEADERS = ["账号", "描述", "启用"]
INITIAL_DATA = [
    ["@leakmealpha", "Crypto KOL Tracker，追踪 KOL 新关注行为", "TRUE"],
    ["@top7ico", "项目早期融资与 ICO 信息", "TRUE"],
    ["@Eli5defi", "DeFi 项目科普与分析", "TRUE"],
    ["@Web3Alerts", "Web3 生态动态与项目预警", "TRUE"],
    ["@WY_mask", "中文 Crypto 投研与项目分析", "TRUE"],
]

print(f"{'='*60}")
print(f"  P32-C: 创建 {TAB_NAME} Tab")
print(f"{'='*60}")

source = google_sheets_source
if not source._init_client():
    print("❌ Google Sheets 连接失败")
    sys.exit(1)
print("✅ 已连接到 Google Sheets")

spreadsheet = source._spreadsheet

# 检查 Tab 是否已存在
try:
    ws = spreadsheet.worksheet(TAB_NAME)
    existing = ws.get_all_records()
    print(f"\n📋 Tab '{TAB_NAME}' 已存在，{len(existing)} 条数据")
    if len(existing) == 0:
        print("  → 写入初始数据...")
        ws.update("A1", [HEADERS] + INITIAL_DATA)
        print(f"  ✅ 写入 {len(INITIAL_DATA)} 条信源")
    else:
        print("  ⚠️ 已有数据，跳过写入")
        for r in existing:
            status = "✅" if str(r.get("启用", "")).upper() in ("TRUE", "是") else "❌"
            print(f"    {status} {r.get('账号', '')} — {r.get('描述', '')}")
except Exception:
    # Tab 不存在，创建
    print(f"\n📋 创建 Tab '{TAB_NAME}'...")
    ws = spreadsheet.add_worksheet(title=TAB_NAME, rows=50, cols=3)
    ws.update("A1", [HEADERS] + INITIAL_DATA)
    print(f"✅ 创建完成，写入 {len(INITIAL_DATA)} 条信源")

print("\n✅ 完成！")
