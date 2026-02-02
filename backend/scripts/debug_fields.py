"""
检查 Google Sheets 实际字段名
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("="*70)
    print("  Google Sheets 字段检查")
    print("="*70)
    
    from app.services.google_sheets_source import GoogleSheetsDataSource
    
    gs = GoogleSheetsDataSource()
    
    if gs._init_client():
        spreadsheet = gs._spreadsheet
        
        for sheet_name in ["banfo", "mimeng"]:
            print(f"\n--- {sheet_name} 工作表 ---")
            try:
                ws = spreadsheet.worksheet(sheet_name)
                
                # 获取第一行（标题行）
                headers = ws.row_values(1)
                print(f"列名 ({len(headers)} 列): {headers}")
                
                # 获取前 3 行数据
                records = ws.get_all_records()
                print(f"总记录数: {len(records)}")
                
                if records:
                    # 检查第一条记录的所有字段
                    first = records[0]
                    print(f"\n第一条记录的字段:")
                    for k, v in first.items():
                        val_preview = str(v)[:50] if v else "(空)"
                        print(f"   '{k}': {val_preview}")
                    
                    # 检查 content 字段存在情况
                    print(f"\n字段映射检查:")
                    print(f"   '内容' 列存在: {'内容' in first}")
                    print(f"   'content' 列存在: {'content' in first}")
                    
                    # 检查有内容的记录数
                    with_content = [r for r in records if r.get("内容") or r.get("content")]
                    print(f"   有内容的记录: {len(with_content)}/{len(records)}")
                    
                    # 查看最后一条记录
                    if len(records) > 1:
                        last = records[-1]
                        print(f"\n最后一条记录:")
                        for k, v in last.items():
                            if v:
                                val_preview = str(v)[:50]
                                print(f"   '{k}': {val_preview}")
                    
            except Exception as e:
                print(f"   ❌ 错误: {e}")

if __name__ == "__main__":
    main()
