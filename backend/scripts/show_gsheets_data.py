"""查看本次测试实际调用的 Google Sheets 数据"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.sample_service import sample_service

print("=== 1. 公式菜单（传给策略师选择）===\n")
menu = sample_service.get_pattern_menu("banfo")
for i, p in enumerate(menu):
    print(f"  {i+1}. {p}")
print(f"\n共 {len(menu)} 个公式")

print("\n\n=== 2. 随机样本（传给写手学习，每次2条）===\n")
samples = sample_service.get_samples(style="banfo", count=2)
for i, s in enumerate(samples):
    print(f"--- 样本{i+1} ---")
    print(f"  content: {s.get('content', '')[:200]}")
    print(f"  logic_pattern: {s.get('logic_pattern', '')}")
    print(f"  emotional_valence: {s.get('emotional_valence', '')}")
    print(f"  snippet_type: {s.get('snippet_type', '')}")
    print()
