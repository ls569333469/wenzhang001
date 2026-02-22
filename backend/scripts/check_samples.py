"""查看样本服务返回的实际内容"""
from dotenv import load_dotenv
load_dotenv()

from app.services.sample_service import sample_service

print("=" * 60)
print("  查看 mimeng 风格样本实际内容")
print("=" * 60)

samples = sample_service.get_samples(style='mimeng', count=3)
print(f"\n获取到 {len(samples)} 条样本\n")

for i, s in enumerate(samples):
    print(f"{'='*60}")
    print(f"样本 {i+1}")
    print(f"{'='*60}")
    print(f"字段名: {list(s.keys())}")
    print(f"作者: {s.get('author', '无')}")
    print(f"风格: {s.get('style', '无')}")
    print(f"情绪: {s.get('emotion', '无')}")
    print(f"类型: {s.get('type', '无')}")
    print(f"状态: {s.get('status', '无')}")
    content = s.get('content', '')
    print(f"内容长度: {len(content)} 字")
    print(f"内容全文:")
    print(content[:500])
    if len(content) > 500:
        print(f"... (截断，全文 {len(content)} 字)")
    print()
