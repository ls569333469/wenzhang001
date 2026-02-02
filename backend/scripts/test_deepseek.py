"""
DeepSeek API 诊断测试
"""
import sys
sys.path.insert(0, ".")

from app.core.llm import generate_text

print("=" * 60)
print("DeepSeek API 诊断测试")
print("=" * 60)

try:
    print("\n[1] 调用 DeepSeek API...")
    
    result = generate_text(
        prompt="你好，请用一句话介绍1INCH项目。",
        provider="deepseek",
        temperature=0.7,
        system_prompt="你是一个Web3专家。"
    )
    
    print(f"\n[2] 返回结果:")
    print(f"    类型: {type(result)}")
    print(f"    长度: {len(result) if result else 0}")
    print(f"    内容: {result[:200] if result else 'None'}...")
    
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
