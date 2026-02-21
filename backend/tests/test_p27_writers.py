"""
P27 Test: Verify 3 new Writer modes through LangGraph pipeline
Tests: bullish_take, kaito_yap, project_research
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

TEST_CASES = [
    {
        "name": "bullish_take",
        "payload": {
            "input": "Binance just announced BNB Chain hit 30 million unique addresses and CZ tweeted about the importance of building during bear markets. TVL increased by 15% in the last month.",
            "mode": "bullish_take",
            "style": "auto",
            "api_config": {"provider": "grok", "model_id": "grok-4-1-fast-reasoning", "api_key": ""}
        }
    },
    {
        "name": "kaito_yap",
        "payload": {
            "input": "Berachain just launched their mainnet with over $2B in pre-deposits. The BERA token is trading at $8.50 with a fully diluted valuation of $4.2B. Their unique Proof of Liquidity mechanism has attracted 150+ protocols to build on the chain.",
            "mode": "kaito_yap",
            "style": "auto",
            "api_config": {"provider": "grok", "model_id": "grok-4-1-fast-reasoning", "api_key": ""}
        }
    },
    {
        "name": "project_research",
        "payload": {
            "input": "Ethena Labs USDe stablecoin has grown to $3.5B market cap. It uses a delta-neutral strategy combining staked ETH with short perpetual futures. The protocol generates yield from funding rates and staking rewards. Key risks include negative funding rate scenarios and custodial risk with centralized exchanges.",
            "mode": "project_research",
            "style": "auto",
            "api_config": {"provider": "volcengine", "model_id": "deepseek-v3-2-251201", "api_key": ""}
        }
    }
]

def test_mode(test_case):
    name = test_case["name"]
    payload = test_case["payload"]
    
    print(f"\n{'='*60}")
    print(f"  Testing: {name}")
    print(f"  Provider: {payload['api_config']['provider']}")
    print(f"  Model: {payload['api_config']['model_id']}")
    print(f"{'='*60}")
    
    start = time.time()
    
    try:
        resp = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            stream=True,
            timeout=120
        )
        
        if resp.status_code != 200:
            print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:200]}")
            return False
        
        events = []
        final_content = None
        draft_content = None
        error_msg = None
        
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data_str = line[6:]  # strip "data: "
            try:
                event = json.loads(data_str)
                events.append(event)
                
                etype = event.get("type", "")
                
                if etype == "thinking_step":
                    agent = event.get("agent", "?")
                    step = event.get("step", "?")
                    detail = event.get("detail", "")[:80]
                    print(f"  [{agent}] {step}: {detail}")
                    
                elif etype == "agent_update":
                    step = event.get("step", "?")
                    status = event.get("status", "?")
                    logs = event.get("logs", [])
                    log_preview = logs[0][:60] if logs else ""
                    print(f"  >> {step} = {status} | {log_preview}")
                    
                elif etype == "content_preview":
                    draft_content = event.get("payload", "")
                    print(f"  [DRAFT] {len(draft_content)} chars")
                    
                elif etype == "final_result":
                    final_content = event.get("payload", "")
                    print(f"  [FINAL] {len(final_content)} chars")
                    
                elif etype == "error":
                    error_msg = event.get("message", "unknown")
                    print(f"  [ERROR] {error_msg[:200]}")
                    
                elif etype == "end":
                    pass
                    
            except json.JSONDecodeError:
                pass
        
        elapsed = time.time() - start
        
        # Results
        print(f"\n  --- Results for {name} ---")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Events: {len(events)}")
        
        if error_msg:
            print(f"  STATUS: FAIL - {error_msg[:100]}")
            return False
        
        content = final_content or draft_content
        if content:
            print(f"  Content length: {len(content)} chars")
            # Print first 200 chars
            preview = content[:200].replace("\n", " ")
            print(f"  Preview: {preview}...")
            print(f"  STATUS: PASS")
            return True
        else:
            print(f"  STATUS: FAIL - No content generated")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] Cannot connect to {BASE_URL}. Is the backend running?")
        return False
    except requests.exceptions.Timeout:
        print(f"  [FAIL] Request timed out after 120s")
        return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  P27 Writer Pipeline Test")
    print("  Testing 3 new modes: bullish_take, kaito_yap, project_research")
    print("=" * 60)
    
    # Health check first
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n  Backend health: {health.json()}")
    except Exception as e:
        print(f"\n  [FATAL] Backend not reachable: {e}")
        exit(1)
    
    results = {}
    for tc in TEST_CASES:
        results[tc["name"]] = test_mode(tc)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    total_pass = sum(1 for v in results.values() if v)
    print(f"\n  Total: {total_pass}/{len(results)} passed")
