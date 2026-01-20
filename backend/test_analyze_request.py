import requests
import json

url = "http://localhost:8000/analyze"
with open("test_payload_analyze.json", "r", encoding="utf-8") as f:
    payload = json.load(f)

print(f"🚀 Sending Request to {url}...")
try:
    with requests.post(url, json=payload, stream=True) as response:
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
        else:
            print("✅ Connection Established. Streaming response:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        try:
                            data = json.loads(decoded_line[6:])
                            if data.get("type") == "analysis_result":
                                print("\n🎯 [ANALYSIS RESULT RECEIVED]")
                                payload_data = data.get("payload")
                                print(json.dumps(payload_data, indent=2, ensure_ascii=False))
                                with open("analysis_result.json", "w", encoding="utf-8") as outfile:
                                    json.dump(payload_data, outfile, indent=2, ensure_ascii=False)
                                    print("\n✅ Saved to analysis_result.json")
                            elif data.get("type") == "error":
                                print(f"\n❌ [ERROR]: {data.get('message')}")
                            else:
                                # Print thinking steps concisely
                                detail = data.get("detail", "")
                                if detail:
                                    print(f"   > {detail}")
                        except:
                            print(f"   {decoded_line}")
except Exception as e:
    print(f"❌ Exception: {e}")
