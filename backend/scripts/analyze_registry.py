"""
分析 _registry 工作表中的赛道分类
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import gspread
from google.oauth2.service_account import Credentials
from collections import Counter

def analyze_registry():
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "config/google_service_account.json")
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET")
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    
    spreadsheet = gc.open_by_key(spreadsheet_id)
    registry = spreadsheet.worksheet("_registry")
    
    print("📡 加载 _registry 数据...")
    records = registry.get_all_records()
    print(f"   共 {len(records)} 条记录")
    
    # 分析字段
    if records:
        print(f"\n📋 字段列表:")
        for key in records[0].keys():
            print(f"   - {key}")
    
    # 分析赛道分类
    categories = Counter()
    for r in records:
        cat = r.get('赛道分类', '') or r.get('category', '') or 'Unknown'
        categories[cat] += 1
    
    print(f"\n🏷️ 赛道分类分布 (共 {len(categories)} 类):")
    for cat, count in categories.most_common(20):
        print(f"   {cat}: {count} 条")
    
    # 检查内容字段
    print(f"\n📝 内容字段检查:")
    content_fields = ['content', '内容', '正文', 'text', '原文']
    for field in content_fields:
        has_field = any(field in r for r in records[:10])
        if has_field:
            print(f"   ✅ 找到 '{field}' 字段")

if __name__ == "__main__":
    analyze_registry()
