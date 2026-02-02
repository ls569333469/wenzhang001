"""
分析 Google Sheets 样本分布
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("="*70)
    print("  Google Sheets 样本分布分析")
    print("="*70)
    
    from app.services.google_sheets_source import GoogleSheetsDataSource
    
    gs = GoogleSheetsDataSource()
    
    if not gs._init_client():
        print("无法连接")
        return
    
    for sheet_name in ["banfo", "mimeng"]:
        print(f"\n--- {sheet_name} 工作表 ---")
        
        try:
            ws = gs._spreadsheet.worksheet(sheet_name)
            records = ws.get_all_records()
            
            print(f"总记录数: {len(records)}")
            
            if not records:
                continue
            
            # 分析片段类型分布
            snippet_types = {}
            emotions = {}
            logic_patterns = {}
            
            for r in records:
                # 片段类型
                st = r.get("片段类型", "未标注")
                snippet_types[st] = snippet_types.get(st, 0) + 1
                
                # 情绪
                em = r.get("情绪", "未标注")
                emotions[em] = emotions.get(em, 0) + 1
                
                # 逻辑公式
                lp = r.get("逻辑公式", "")
                if lp:
                    logic_patterns[lp] = logic_patterns.get(lp, 0) + 1
            
            # 打印结果
            print(f"\n片段类型分布 (Top 10):")
            for st, cnt in sorted(snippet_types.items(), key=lambda x: -x[1])[:10]:
                print(f"  {st}: {cnt}")
            
            print(f"\n情绪分布:")
            for em, cnt in sorted(emotions.items(), key=lambda x: -x[1]):
                print(f"  {em}: {cnt}")
            
            print(f"\n逻辑公式分布 (Top 10):")
            for lp, cnt in sorted(logic_patterns.items(), key=lambda x: -x[1])[:10]:
                print(f"  {lp}: {cnt}")
                
        except Exception as e:
            print(f"  错误: {e}")

if __name__ == "__main__":
    main()
