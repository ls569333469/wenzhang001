"""
P31: Surf API 连通性测试脚本
测试 Surf AI 的 OpenAI-compatible API (使用 httpx 避免 Python 3.14 SSL 问题)
"""
import os
import sys
import json
import time
import httpx
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SURF_API_KEY = os.getenv("SURF_API_KEY")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"

if not SURF_API_KEY:
    print("ERROR: SURF_API_KEY not found in .env")
    sys.exit(1)

print(f"API Key loaded: {SURF_API_KEY[:12]}...")
print(f"Endpoint: {SURF_BASE_URL}")
print("=" * 60)


def test_surf_api(model: str, query: str, abilities: list = None, reasoning: str = "medium"):
    """测试 Surf API 调用"""
    print(f"\nTest: model={model}, reasoning={reasoning}")
    print(f"   Query: {query[:80]}...")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": query}
        ],
        "stream": False,
        "reasoning_effort": reasoning,
    }
    
    if abilities:
        payload["ability"] = abilities
        payload["citation"] = ["source"]
    
    headers = {
        "Authorization": f"Bearer {SURF_API_KEY}",
        "Content-Type": "application/json",
    }
    
    start = time.time()
    try:
        with httpx.Client(timeout=180) as client:
            resp = client.post(
                SURF_BASE_URL,
                headers=headers,
                json=payload,
            )
        elapsed = time.time() - start
        
        print(f"   Status: {resp.status_code} ({elapsed:.1f}s)")
        
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            reasoning_text = data["choices"][0]["message"].get("reasoning", "")
            
            print(f"   Tokens: prompt={usage.get('prompt_tokens', '?')}, "
                  f"completion={usage.get('completion_tokens', '?')}, "
                  f"total={usage.get('total_tokens', '?')}")
            
            if reasoning_text:
                print(f"   Reasoning: {reasoning_text[:200]}...")
            
            print(f"\n--- Response ({len(content)} chars) ---")
            # 安全打印，避免 Windows 终端编码问题
            try:
                print(content[:1500])
            except UnicodeEncodeError:
                print(content[:1500].encode('utf-8', errors='replace').decode('utf-8'))
            if len(content) > 1500:
                print(f"\n... ({len(content) - 1500} more chars)")
            print("--- End ---")
            return data
        else:
            print(f"   Error: {resp.text[:500]}")
            return None
            
    except httpx.TimeoutException:
        elapsed = time.time() - start
        print(f"   Timeout after {elapsed:.1f}s")
        return None
    except Exception as e:
        elapsed = time.time() - start
        print(f"   Exception ({elapsed:.1f}s): {e}")
        return None


# ===== 测试 1: surf-ask 快速问答 =====
print("\n" + "=" * 60)
print("TEST 1: surf-ask (Quick Q&A)")
print("=" * 60)
test_surf_api(
    model="surf-ask",
    query="What is Hyperliquid? Brief overview: TVL, daily volume, key features. Keep it under 200 words.",
    abilities=["search", "market_analysis"],
    reasoning="low"
)

# ===== 测试 2: surf-1.5-instant 投研查询 =====
print("\n" + "=" * 60)
print("TEST 2: surf-1.5-instant (Research Query)")
print("=" * 60)
test_surf_api(
    model="surf-1.5-instant",
    query="Give me a concise analysis of Ethena (ENA): price, market cap, TVL, funding rounds, key risks. Under 300 words.",
    abilities=["search", "evm_onchain", "market_analysis"],
    reasoning="medium"
)

print("\n\nAll tests completed!")
