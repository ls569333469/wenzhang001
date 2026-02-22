"""
P28: 重命名 Google Sheets Tab — 英文名 → 中文名

执行一次即可，将现有 Tab 统一为中文命名。

映射：
  style_mimeng      → 风格_咪蒙
  style_banfo       → 风格_半佛
  style_insider     → 风格_圈内人
  style_xinshixiang → 风格_新世相
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import gspread
from google.oauth2.service_account import Credentials

RENAME_MAP = {
    "style_mimeng": "风格_咪蒙",
    "style_banfo": "风格_半佛",
    "style_insider": "风格_圈内人",
    "style_xinshixiang": "风格_新世相",
    # 旧名 (如果存在)
    "mimeng": "风格_咪蒙",
    "banfo": "风格_半佛",
}

def main():
    creds_path = os.path.join(os.path.dirname(__file__), "..", "config", "google_service_account.json")
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET", "")
    
    if not spreadsheet_id:
        print("[ERROR] GOOGLE_SHEETS_SPREADSHEET not set")
        return
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    
    # 获取所有现有 Tab 名
    existing_tabs = [ws.title for ws in spreadsheet.worksheets()]
    print(f"现有 Tab ({len(existing_tabs)}): {existing_tabs}")
    
    renamed = 0
    for old_name, new_name in RENAME_MAP.items():
        if old_name in existing_tabs:
            if new_name in existing_tabs:
                print(f"  [SKIP] {old_name} -> {new_name} (目标已存在)")
                continue
            ws = spreadsheet.worksheet(old_name)
            ws.update_title(new_name)
            print(f"  [OK] {old_name} -> {new_name}")
            renamed += 1
        else:
            pass  # Tab 不存在，跳过
    
    # 检查是否所有目标 Tab 都存在
    final_tabs = [ws.title for ws in spreadsheet.worksheets()]
    expected = ["风格_咪蒙", "风格_半佛", "风格_圈内人", "风格_新世相",
                "吹捧素材", "嘴撸项目", "投研项目"]
    
    print(f"\n重命名完成：{renamed} 个 Tab")
    print(f"最终 Tab 列表: {final_tabs}")
    
    missing = [t for t in expected if t not in final_tabs]
    if missing:
        print(f"[WARNING] 缺失 Tab: {missing}")
    else:
        print("[OK] 所有中文 Tab 均存在")

if __name__ == "__main__":
    main()
