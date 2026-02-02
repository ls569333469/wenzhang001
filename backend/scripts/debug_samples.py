"""
调试脚本：查看 Google Sheets 素材详情
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("="*70)
    print("  Google Sheets 素材调用调试")
    print("="*70)
    
    # 1. 检查配置
    print("\n📋 环境配置:")
    print(f"   SAMPLE_SOURCE: {os.getenv('SAMPLE_SOURCE', 'Not Set')}")
    print(f"   GOOGLE_SHEETS_SPREADSHEET: {os.getenv('GOOGLE_SHEETS_SPREADSHEET', 'Not Set')[:20]}...")
    
    # 2. 检查 Google Sheets 数据源
    print("\n📊 Google Sheets 数据检查:")
    
    from app.services.google_sheets_source import GoogleSheetsDataSource
    
    try:
        gs = GoogleSheetsDataSource()
        print(f"   ✅ Google Sheets 连接成功")
        
        # 检查 banfo 工作表
        print("\n   --- banfo 工作表 ---")
        banfo_samples = gs.get_samples("banfo", count=3)
        print(f"   获取样本数: {len(banfo_samples)}")
        
        if banfo_samples:
            for i, s in enumerate(banfo_samples, 1):
                content = s.get("content", "")[:100]
                logic = s.get("logic_pattern", "无")
                print(f"\n   样本 {i}:")
                print(f"      逻辑公式: {logic}")
                print(f"      内容预览: {content}...")
        
        # 检查 mimeng 工作表
        print("\n   --- mimeng 工作表 ---")
        mimeng_samples = gs.get_samples("mimeng", count=3)
        print(f"   获取样本数: {len(mimeng_samples)}")
        
        if mimeng_samples:
            for i, s in enumerate(mimeng_samples, 1):
                content = s.get("content", "")[:100]
                print(f"\n   样本 {i}: {content}...")
        
        # 检查总行数
        print("\n📈 工作表行数统计:")
        for sheet_name in ["banfo", "mimeng"]:
            try:
                if sheet_name not in gs._cache:
                    gs._cache[sheet_name] = gs._load_sheet_data(sheet_name)
                records = gs._cache.get(sheet_name, [])
                print(f"   {sheet_name}: {len(records)} 行")
            except Exception as e:
                print(f"   {sheet_name}: 无法加载 - {e}")
        
    except Exception as e:
        print(f"   ❌ Google Sheets 错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 检查 sample_service
    print("\n📦 Sample Service 检查:")
    
    from app.services.sample_service import sample_service
    
    print(f"   当前数据源模式: {sample_service.get_source_mode()}")
    
    # 强制使用 Google Sheets
    sample_service.set_source_mode("google_sheets")
    print(f"   已切换到: {sample_service.get_source_mode()}")
    
    # 获取 banfo 样本
    print("\n   测试 banfo 样本获取:")
    samples = sample_service.get_samples("banfo", count=3)
    print(f"   获取样本数: {len(samples)}")
    
    for i, s in enumerate(samples, 1):
        print(f"\n   样本 {i}:")
        print(f"      字段: {list(s.keys())}")
        content = s.get("content", "")[:150]
        print(f"      内容: {content}...")

if __name__ == "__main__":
    main()
