"""
Test script for Volcengine (火山引擎) API - Standard chat.completions format
Based on official documentation
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_volcengine_chat_completions():
    """Test using standard chat.completions.create API"""
    from openai import OpenAI
    
    api_key = os.getenv('ARK_API_KEY')
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key not found!")
    
    client = OpenAI(
        base_url='https://ark.cn-beijing.volces.com/api/v3',
        api_key=api_key
    )
    
    print("\nTesting chat.completions.create API...")
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-v3-2-251201",  # 火山引擎托管的 DeepSeek V3
            messages=[
                {"role": "system", "content": "你是一个专业的 Web3 内容创作助手。"},
                {"role": "user", "content": "用一句话介绍比特币。"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"\nResponse type: {type(completion)}")
        print(f"Model: {completion.model}")
        print(f"Content: {completion.choices[0].message.content}")
        print(f"Usage: {completion.usage}")
        
        print("\n✅ chat.completions.create API successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_text_function():
    """Test our unified generate_text function"""
    from app.core.llm import generate_text
    
    print("\n" + "="*50)
    print("Testing generate_text function...")
    
    try:
        result = generate_text(
            prompt="请用简短的话解释什么是以太坊。",
            provider="volcengine",
            temperature=0.7,
            system_prompt="你是一个专业的区块链专家。"
        )
        
        print(f"\nResult: {result}")
        print("\n✅ generate_text function successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*50)
    print("Volcengine API Test")
    print("="*50)
    
    test1 = test_volcengine_chat_completions()
    test2 = test_generate_text_function()
    
    print("\n" + "="*50)
    print(f"Results: chat.completions={'✅' if test1 else '❌'}, generate_text={'✅' if test2 else '❌'}")
