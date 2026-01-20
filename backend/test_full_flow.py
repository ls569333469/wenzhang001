"""
Test the complete generation flow with API config
"""
import requests
import json

def test_generate_flow():
    print("=" * 60)
    print("Testing /generate endpoint with volcengine provider...")
    print("=" * 60)
    
    payload = {
        "input": "Bitcoin突破10万美元",
        "mode": "mimeng",
        "narrative_type": "project_review",
        "api_config": {
            "api_key": "",  # 空字符串，应从环境变量读取
            "model_id": "",
            "provider": "volcengine"
        }
    }
    
    print(f"\nPayload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/generate",
            json=payload,
            stream=True,
            timeout=120
        )
        
        print(f"\nResponse status: {response.status_code}")
        print("\n--- Streaming Events ---")
        
        event_count = 0
        error_count = 0
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    event_count += 1
                    try:
                        event = json.loads(line_str[6:])
                        event_type = event.get("type", "unknown")
                        
                        if event_type == "thinking_step":
                            agent = event.get("agent", "?")
                            step = event.get("step", {})
                            content = step.get("content", "") if isinstance(step, dict) else str(step)
                            print(f"  [{event_count}] THINKING ({agent}): {content[:60]}...")
                        elif event_type == "agent_update":
                            print(f"  [{event_count}] AGENT: {event.get('step')} -> {event.get('status')}")
                        elif event_type == "final_result":
                            result = event.get("payload", "")
                            print(f"  [{event_count}] FINAL RESULT: {result[:100]}...")
                        elif event_type == "error":
                            print(f"  [{event_count}] ERROR: {event.get('message')}")
                            error_count += 1
                        elif event_type == "end":
                            print(f"  [{event_count}] END: {event.get('payload')}")
                        else:
                            print(f"  [{event_count}] {event_type}: {str(event)[:80]}")
                    except json.JSONDecodeError as e:
                        print(f"  [{event_count}] JSON ERROR: {e}")
            
            # Stop after 50 events to prevent infinite loop
            if event_count > 50:
                print("  ... (truncated)")
                break
        
        print("\n" + "=" * 60)
        print(f"Total events: {event_count}, Errors: {error_count}")
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_generate_flow()
