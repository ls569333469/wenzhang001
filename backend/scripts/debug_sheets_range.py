"""
Google Sheets 数据范围深度排查
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("="*70)
    print("  Google Sheets 数据范围深度排查")
    print("="*70)
    
    from app.services.google_sheets_source import GoogleSheetsDataSource
    
    gs = GoogleSheetsDataSource()
    
    # 直接检查原始 spreadsheet
    print("\n📊 原始 Spreadsheet 检查:")
    if gs._init_client():
        spreadsheet = gs._spreadsheet
        print(f"   电子表格名称: {spreadsheet.title}")
        
        # 列出所有工作表
        worksheets = spreadsheet.worksheets()
        print(f"\n   📋 所有工作表:")
        for ws in worksheets:
            print(f"      - {ws.title}: {ws.row_count} 行 x {ws.col_count} 列")
        
        # 详细检查 banfo 工作表
        print("\n   --- banfo 工作表详细检查 ---")
        try:
            banfo_ws = spreadsheet.worksheet("banfo")
            print(f"      定义行数: {banfo_ws.row_count}")
            print(f"      定义列数: {banfo_ws.col_count}")
            
            # 获取所有记录
            records = banfo_ws.get_all_records()
            print(f"      ✅ get_all_records() 返回: {len(records)} 条")
            
            if records:
                print(f"      字段: {list(records[0].keys())}")
                
                # 检查空行情况
                non_empty = [r for r in records if r.get("content")]
                print(f"      非空记录: {len(non_empty)} 条")
                
                # 显示第一条和最后一条
                print(f"\n      第 1 条: {records[0].get('content', '')[:60]}...")
                if len(records) > 1:
                    print(f"      第 {len(records)} 条: {records[-1].get('content', '')[:60]}...")
                
                # 检查随机采样是否覆盖全部
                print(f"\n   📈 随机采样测试 (10 轮):")
                from app.services.google_sheets_source import GoogleSheetsDataSource
                gs2 = GoogleSheetsDataSource()
                
                all_indices = set()
                for i in range(10):
                    samples = gs2.get_samples("banfo", count=3)
                    for s in samples:
                        # 尝试找到原始索引
                        content = s.get("content", "")[:50]
                        for j, r in enumerate(records):
                            if r.get("content", "")[:50] == content:
                                all_indices.add(j)
                                break
                
                print(f"      10 轮采样覆盖: {len(all_indices)}/{len(records)} 条")
                print(f"      采样索引范围: {min(all_indices) if all_indices else 0} - {max(all_indices) if all_indices else 0}")
                
        except Exception as e:
            print(f"      ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        
        # 检查 mimeng 工作表
        print("\n   --- mimeng 工作表详细检查 ---")
        try:
            mimeng_ws = spreadsheet.worksheet("mimeng")
            print(f"      定义行数: {mimeng_ws.row_count}")
            records = mimeng_ws.get_all_records()
            print(f"      ✅ get_all_records() 返回: {len(records)} 条")
        except Exception as e:
            print(f"      ❌ 错误: {e}")
    else:
        print("   ❌ 无法连接 Google Sheets")
    
    print("\n" + "="*70)
    print("  结论")
    print("="*70)

if __name__ == "__main__":
    main()
