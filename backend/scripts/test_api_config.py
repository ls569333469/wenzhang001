"""
Quick API Test - Check if configured LLM APIs are working
"""
import sys
sys.path.insert(0, 'backend')

from app.core.config import get_api_key, load_config
import requests

def test_gemini_api():
    """Test Gemini API connectivity"""
    api_key = get_api_key("gemini")
    if not api_key:
        print("❌ Gemini: No API key configured")
        return False
    
    print(f"🔑 Gemini API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test with a simple request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": "Say 'API test successful' in exactly 3 words."}]}],
        "generationConfig": {"maxOutputTokens": 50}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            print(f"✅ Gemini: API working! Response: {text[:50]}")
            return True
        else:
            print(f"❌ Gemini: Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Gemini: Connection error - {e}")
        return False

def test_doubao_api():
    """Test Doubao (Ark) API connectivity"""
    api_key = get_api_key("doubao")
    if not api_key:
        print("❌ Doubao: No API key configured")
        return False
    
    print(f"🔑 Doubao API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # ARK API endpoint
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "doubao-1.5-pro-32k-250115",
        "messages": [{"role": "user", "content": "Say 'API test successful' in exactly 3 words."}],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✅ Doubao: API working! Response: {text[:50]}")
            return True
        else:
            print(f"❌ Doubao: Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Doubao: Connection error - {e}")
        return False

def main():
    print("="*50)
    print("🔍 API Configuration Test")
    print("="*50)
    
    # Show current config
    config = load_config()
    api_keys = config.get("api_keys", {})
    print(f"\n📋 Configured APIs: {list(api_keys.keys())}")
    
    print("\n--- Testing Gemini ---")
    gemini_ok = test_gemini_api()
    
    print("\n--- Testing Doubao ---")
    doubao_ok = test_doubao_api()
    
    print("\n" + "="*50)
    print("📊 Summary")
    print("="*50)
    print(f"  Gemini: {'✅ Working' if gemini_ok else '❌ Failed'}")
    print(f"  Doubao: {'✅ Working' if doubao_ok else '❌ Failed'}")
    
    if not gemini_ok and not doubao_ok:
        print("\n⚠️ Both APIs failed! This explains why creation workflow times out.")
    elif gemini_ok or doubao_ok:
        print("\n✅ At least one API is working.")

if __name__ == "__main__":
    main()
