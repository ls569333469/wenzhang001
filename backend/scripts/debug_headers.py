"""
打印完整列名
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def main():
    from app.services.google_sheets_source import GoogleSheetsDataSource
    
    gs = GoogleSheetsDataSource()
    
    if gs._init_client():
        ws = gs._spreadsheet.worksheet("banfo")
        
        # 获取标题行
        headers = ws.row_values(1)
        print("="*70)
        print("banfo 工作表完整列名:")
        print("="*70)
        for i, h in enumerate(headers, 1):
            print(f"  列 {i}: '{h}'")
        
        print("\n" + "="*70)
        
        # 获取第2行数据（第一条记录）
        row2 = ws.row_values(2)
        print("第一条数据:")
        print("="*70)
        for i, (h, v) in enumerate(zip(headers, row2), 1):
            v_preview = v[:60] if v else "(空)"
            print(f"  列 {i} '{h}': {v_preview}")

if __name__ == "__main__":
    main()
