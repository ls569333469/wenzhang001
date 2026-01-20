import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_api_config():
    config_path = Path(__file__).parent.parent / "config" / "user_config.json"
    api_key_doubao = None
    api_key_gemini = None
    
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            api_key_doubao = cfg.get("api_keys", {}).get("doubao")
            api_key_gemini = cfg.get("api_keys", {}).get("gemini")
    
    if not api_key_doubao:
        api_key_doubao = os.getenv("VOLC_API_KEY")
    if not api_key_gemini:
        api_key_gemini = os.getenv("GOOGLE_API_KEY") # Fallback
        
    # Default model IDs
    model_doubao = os.getenv("VOLC_MODEL_ENDPOINT", "deepseek-v3-2-251201")
    model_gemini = "gemini-1.5-flash"
    
    return {
        "doubao_key": api_key_doubao,
        "doubao_model": model_doubao,
        "gemini_key": api_key_gemini,
        "gemini_model": model_gemini
    }

async def test_generate():
    print("🚀 Testing /generate endpoint (Writer -> Critic -> Polisher)...")
    
    cfg = get_api_config()
    url = "http://localhost:8002/generate"
    
    # Mock Strategy Option
    selected_option = {
        "id": "opt_test_1",
        "title": "Test Strategy: The Lie Flat Generation",
        "hook_angle": "Controversial",
        "pain_point": "Social Pressure",
        "target_audience": "Gen Z",
        "outline": [
            "Introduction: Define lying flat",
            "Core Argument: It's not laziness, it's resistance",
            "Conclusion: Acceptance"
        ]
    }
    
    # Mock Info Anchors (Simulating search results from Lark)
    info_anchors = [
        {"original_text": "Lying flat is a silent protest.", "clean_text": "Lying flat is resistance.", "quality_score": 5},
        {"original_text": "Young people are tired.", "clean_text": "Exhaustion drives this.", "quality_score": 4}
    ]
    
    payload = {
        "input": "用一句话解释躺平文化 (max 50 chars)",
        "references": [],
        "mode": "mimeng",
        "narrative_type": "opinion",
        "agent_config": {
            "writer": {
                "provider": "doubao", 
                "api_key": cfg["doubao_key"],
                "model_id": cfg["doubao_model"]
            },
            "critic": {
                "provider": "doubao", # Using doubao for all for simplicity/speed
                "api_key": cfg["doubao_key"],
                "model_id": cfg["doubao_model"]
            },
            "polisher": {
                "provider": "doubao",
                "api_key": cfg["doubao_key"],
                "model_id": cfg["doubao_model"]
            }
        },
        "selected_option": selected_option,
        "info_anchors": info_anchors
    }
    
    print(f"DEBUG: Doubao Key: {bool(cfg['doubao_key'])}")
    print(f"DEBUG: Doubao Model: {cfg['doubao_model']}")
    print(f"DEBUG: Gemini Key: {bool(cfg['gemini_key'])}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"❌ Error: Status {response.status}")
                    text = await response.text()
                    try:
                        err = json.loads(text)
                        print(json.dumps(err, indent=2, ensure_ascii=False))
                    except:
                        print(text)
                    return

                print("✅ Connection established. Streaming generation...")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or not line.startswith("data: "):
                        continue
                        
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if data['type'] == 'thinking_step':
                            print(f"   🧠 [{data['agent']}]: {data['step']}")
                        elif data['type'] == 'agent_update':
                            print(f"   🔄 Status Update: {data['step']} -> {data['status']}")
                        elif data['type'] == 'final_result':
                            print("   ✨ [Final Result]: Received generated content!")
                            print(f"   📝 Length: {len(data['payload'])} chars")
                            
                            # Write success marker
                            with open("generate_success.txt", "w", encoding="utf-8") as f:
                                f.write("SUCCESS")
                                
                            # print(data['payload'][:200] + "...")
                    except json.JSONDecodeError:
                        pass
                        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_generate())
