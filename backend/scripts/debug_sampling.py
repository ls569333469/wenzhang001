"""
验证随机采样范围
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import random

def main():
    print("="*70)
    print("  随机采样范围验证")
    print("="*70)
    
    from app.services.google_sheets_source import GoogleSheetsDataSource
    
    gs = GoogleSheetsDataSource()
    
    if gs._init_client():
        ws = gs._spreadsheet.worksheet("banfo")
        records = ws.get_all_records()
        
        print(f"\n总记录数: {len(records)}")
        
        # 检查 content 字段
        has_content = 0
        for r in records:
            if r.get("内容"):  # 注意是中文列名
                has_content += 1
        
        print(f"有内容的记录: {has_content}")
        
        # 查看第 1, 100, 1000, 5000, 10000, 15000 条
        indices = [0, 99, 999, 4999, 9999, min(14999, len(records)-1)]
        
        print("\n抽样检查:")
        for i in indices:
            if i < len(records):
                content = records[i].get("内容", "")[:50]
                logic = records[i].get("逻辑公式", "无")
                print(f"  行 {i+2}: [{logic}] {content}...")
        
        # 测试实际采样
        print("\n\n实际采样测试（调用 get_samples）:")
        print("-"*50)
        
        samples = gs.get_samples("banfo", count=3)
        print(f"返回样本数: {len(samples)}")
        
        if samples:
            for i, s in enumerate(samples, 1):
                content = s.get("content", "无内容")[:60]
                logic = s.get("logic_pattern", "无")
                print(f"  样本 {i}: [{logic}] {content}...")
        else:
            # 调试：直接调用内部方法
            print("\n调试 - 直接查看 _cache:")
            if "banfo" in gs._cache:
                cached = gs._cache["banfo"]
                print(f"  缓存记录数: {len(cached)}")
                if cached:
                    print(f"  第一条字段: {list(cached[0].keys())}")
                    print(f"  第一条 content: {cached[0].get('content', '无')[:50]}")

if __name__ == "__main__":
    main()
