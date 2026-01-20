"""
Test script to verify dynamic settings are properly passed through the backend.
"""
import requests
import json

def test_generate_endpoint():
    """Test the /generate endpoint with dynamic settings"""
    url = "http://localhost:8000/generate"
    
    payload = {
        "input": "Test dynamic settings with narrative type: Bitcoin reached $100k today",
        "mode": "insider",
        "narrative_type": "micro_novel",
        "api_config": {
            "api_key": "",  # Empty = use env variable
            "model_id": "",  # Empty = use default
            "provider": "google"
        }
    }
    
    print(f"Sending request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            event_count = 0
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        event_data = decoded[6:]  # Remove "data: " prefix
                        try:
                            parsed = json.loads(event_data)
                            event_type = parsed.get("type", "unknown")
                            print(f"\n[Event {event_count}] Type: {event_type}")
                            
                            if event_type == "thinking_step":
                                print(f"  Agent: {parsed.get('agent')}")
                                print(f"  Step: {parsed.get('step')}")
                                print(f"  Progress: {parsed.get('progress')}%")
                            elif event_type == "agent_update":
                                print(f"  Step: {parsed.get('step')}")
                                print(f"  Status: {parsed.get('status')}")
                            elif event_type == "final_result":
                                content = parsed.get("payload", "")[:200]
                                print(f"  Content preview: {content}...")
                            elif event_type == "end":
                                print(f"  {parsed.get('payload')}")
                            elif event_type == "error":
                                print(f"  Error: {parsed.get('message')}")
                        except json.JSONDecodeError:
                            print(f"  Raw: {event_data[:100]}")
                        
                        event_count += 1
                        if event_count > 20:  # Limit output
                            print("\n... (limiting output)")
                            break
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("Request timed out after 60 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def test_health():
    """Test health endpoint"""
    response = requests.get("http://localhost:8000/health")
    print(f"Health check: {response.json()}")

if __name__ == "__main__":
    test_health()
    print("=" * 50)
    test_generate_endpoint()
