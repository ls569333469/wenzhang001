"""
Direct LLM Call Test - Bypass HTTP to test LLM directly
"""
import sys
sys.path.insert(0, 'backend')

from app.core.llm import generate_text
from app.core.config import get_api_key

def test_direct_llm():
    print("="*50)
    print("🔧 Direct LLM Call Test")
    print("="*50)
    
    # Get Doubao API key
    api_key = get_api_key("doubao")
    print(f"Using Doubao API Key: {api_key[:10]}...{api_key[-4:]}")
    
    prompt = "用一句话介绍比特币。"
    
    print(f"\nPrompt: {prompt}")
    print("Calling generate_text with volcengine provider...")
    
    try:
        result = generate_text(
            prompt=prompt,
            api_key=api_key,
            provider="volcengine",
            model_id="doubao-1.5-pro-32k-250115",
            temperature=0.7,
            max_tokens=100
        )
        print(f"\n✅ SUCCESS!")
        print(f"Response: {result[:200]}")
        return True
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_llm()
