"""
列出 Google Sheets 中的所有工作表
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import gspread
from google.oauth2.service_account import Credentials

def list_sheets():
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "config/google_service_account.json")
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET")
    
    print(f"Spreadsheet ID: {spreadsheet_id}")
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    
    spreadsheet = gc.open_by_key(spreadsheet_id)
    
    print(f"\n📋 工作表列表:")
    for i, ws in enumerate(spreadsheet.worksheets()):
        print(f"  {i+1}. {ws.title} ({ws.row_count} 行)")
        
    # 查看是否有 _registry 工作表
    print(f"\n🔍 检查 _registry 工作表...")
    try:
        registry = spreadsheet.worksheet("_registry")
        records = registry.get_all_records()
        print(f"   ✅ _registry 存在，共 {len(records)} 条记录")
        if records:
            print(f"   字段: {list(records[0].keys())}")
            print(f"\n   前 5 条记录:")
            for r in records[:5]:
                print(f"   - {r}")
    except Exception as e:
        print(f"   ❌ _registry 不存在或无法访问: {e}")

if __name__ == "__main__":
    list_sheets()
