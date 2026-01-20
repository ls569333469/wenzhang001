import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_analyze():
    print("Testing /analyze endpoint (SSE)...")
    payload = {
        "input": "Write a review of the new iPhone 16 Pro Max",
        "mode": "mimeng",
        "narrative_type": "project_review",
        "references": ["Some reference about camera specs"]
    }
    
    options = []
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload, stream=True)
        response.raise_for_status()
        
        print("Streaming response...")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                    try:
                        data = json.loads(json_str)
                        if data["type"] == "thinking_step":
                            print(f"[Thinking] {data['agent']}: {data['step']} - {data.get('detail', '')}")
                        elif data["type"] == "analysis_result":
                            payload_data = data["payload"]
                            if "options" in payload_data:
                                options = payload_data["options"]
                                print(f"[Result] Received {len(options)} options.")
                        elif data["type"] == "error":
                            print(f"[Error] {data['message']}")
                    except Exception as e:
                        pass
                        
        if len(options) == 0:
            print("FAILED: No options received")
            sys.exit(1)
            
        print(f"SUCCESS: Analysis completed with {len(options)} options.")
        return options[0] 
        
    except Exception as e:
        print(f"FAILED: {e}")
        try:
             print(response.text)
        except:
            pass
        sys.exit(1)

def test_generate(selected_option):
    print("\nTesting /generate endpoint with selected option...")
    payload = {
        "input": "Write a review of the new iPhone 16 Pro Max",
        "mode": "mimeng",
        "narrative_type": "project_review",
        "references": [],
        "selected_option": selected_option
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=payload, stream=True)
        response.raise_for_status()
        
        print("Streaming response...")
        received_thinking = False
        received_result = False
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                    try:
                        data = json.loads(json_str)
                        if data["type"] == "thinking_step":
                            received_thinking = True
                            print(f"[Thinking] {data['agent']}: {data['step']}")
                        elif data["type"] == "final_result":
                            received_result = True
                            print(f"[Result] Generated content length: {len(data['payload'])}")
                    except:
                        pass
        
        if not received_thinking:
            print("WARNING: Did not receive thinking steps (might be fast forwarded?)")
        
        if not received_result:
            print("FAILED: Did not receive final result")
            sys.exit(1)
            
        print("SUCCESS: Generation completed.")
        
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for server...")
    time.sleep(5) 
    
    try:
        requests.get(f"{BASE_URL}/health")
    except:
        print("Server not up yet. Waiting more...")
        time.sleep(5)
        
    option = test_analyze()
    test_generate(option)
