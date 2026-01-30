
import requests
import json
import sys

def test_workflow():
    url = "http://localhost:8000/generate"
    payload = {
        "input": "分析以太坊Layer2的最新竞争格局，特别是Arbitrum和Optimism的对比",
        "mode": "deep_analysis",
        "style": "banfo",            # P2: Style Parameter
        "length": "short",           # P3: Length Parameter
        "retention_level": 2         # P5: Retention Level (High Retention)
    }
    
    print(f"--- Sending Request P1-P5 Verification ---")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        with requests.post(url, json=payload, stream=True) as response:
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return

            print("\n--- Streaming Response ---")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:]
                        try:
                            if data_str.strip() == "[DONE]":
                                print("\n[DONE]")
                                break
                            
                            data = json.loads(data_str)
                            
                            # Print Agent Steps
                            if "node" in data:
                                print(f"\n[Agent: {data['node']}]")
                            
                            # Print Content Updates (Strategist Plan or Writer Text)
                            if "plan" in data:
                                print(f"Strategist Plan: {data['plan'][:100]}...")
                            
                            if "content" in data:
                                # Just print a dot for content chunks to avoid flooding, or small chunks
                                print(data["content"], end="", flush=True)
                                
                        except json.JSONDecodeError:
                            print(f"Raw: {data_str}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_workflow()
