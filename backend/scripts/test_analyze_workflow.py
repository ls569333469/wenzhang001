import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from backend root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

import json
from pathlib import Path

def get_api_config():
    # Try loading from user_config.json
    config_path = Path(__file__).parent.parent / "config" / "user_config.json"
    api_key = None
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            api_key = cfg.get("api_keys", {}).get("doubao")
    
    # Fallback to env
    if not api_key:
        api_key = os.getenv("VOLC_API_KEY")
        
    model_id = os.getenv("VOLC_MODEL_ENDPOINT", "ep-20250111171732-kp925") # Updated default from project knowledge or previous default
    # If previous default was deepseek-v3-2-251201, I will use that.
    # Actually, let's just use "ep-20241224164344-mqh8r" or similar if known, 
    # BUT better to use the one from cleaner_cli: "deepseek-v3-2-251201" is likely a placeholder name? 
    # NO, "deepseek-v3-2-251201" looks like a specific endpoint name.
    # Let's check cleaner_cli.py again. 
    # Line 93: os.getenv("VOLC_MODEL_ENDPOINT", "deepseek-v3-2-251201")
    
    return api_key, "deepseek-v3-2-251201"

async def test_analyze():
    api_key, model_id = get_api_config()
    print(f"DEBUG: API Key found: {bool(api_key)}")
    print(f"DEBUG: Model ID: {model_id}")
    
    print("🚀 Testing /analyze endpoint (Strategist)...")
    
    url = "http://localhost:8002/analyze" 
    
    payload = {
        "input": "如何看待当代年轻人的躺平文化？",
        "references": [],
        "mode": "mimeng",
        "narrative_type": "opinion",
        "agent_config": {
            "strategist": {
                "provider": "doubao", 
                "api_key": api_key,
                "model_id": model_id
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"❌ Error: Status {response.status}")
                    text = await response.text()
                    print(text)
                    return

                print("✅ Connection established. Streaming response...")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or not line.startswith("data: "):
                        continue
                        
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if data['type'] == 'thinking_step':
                            print(f"   🧠 [Thinking]: {data['detail']}")
                        elif data['type'] == 'analysis_result':
                            print(f"   ✨ [Result]: Options generated: {len(data['payload']['options'])}")
                            print(f"   📦 [Anchors]: {len(data['payload'].get('info_anchors', []))} anchors found")
                    except json.JSONDecodeError:
                        pass
                        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_analyze())
