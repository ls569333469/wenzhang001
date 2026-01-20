import requests
import json

url = "http://localhost:8000/generate"
# Reuse the payload file we just created
with open("test_payload_generate.json", "r", encoding="utf-8") as f:
    payload = json.load(f)

print(f"🚀 Sending Generate Request to {url}...")
try:
    with requests.post(url, json=payload, stream=True) as response:
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
        else:
            print("✅ Connection Established. Streaming response:")
            final_content = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        try:
                            data = json.loads(decoded_line[6:])
                            event_type = data.get("type")
                            
                            if event_type == "final_result":
                                print("\n📝 [FINAL CONTENT RECEIVED]")
                                final_content = data.get("payload")
                                print(final_content[:200] + "...") # Print preview
                                
                                # Use UTF-8 for saving content
                                with open("generation_result.md", "w", encoding="utf-8") as outfile:
                                    outfile.write(final_content)
                                    print("\n✅ Saved full content to generation_result.md")
                                    
                            elif event_type == "agent_update":
                                status = data.get("status")
                                step = data.get("step")
                                print(f"🔄 [{step.upper()}] Status: {status}")
                                
                            elif event_type == "error":
                                print(f"\n❌ [ERROR]: {data.get('message')}")
                                
                            elif event_type == "thinking_step":
                                # Concise progress
                                agent = data.get("agent", "system")
                                detail = data.get("detail", "")
                                print(f"   [{agent}] {detail}")
                                
                        except Exception as e:
                             pass # Ignore parse errors for log lines

except Exception as e:
    print(f"❌ Exception: {e}")
