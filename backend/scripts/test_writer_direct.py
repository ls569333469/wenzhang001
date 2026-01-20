import sys
import os
import json
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.writer import writer_agent
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_api_config():
    config_path = Path(__file__).parent.parent / "config" / "user_config.json"
    api_key = None
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            api_key = cfg.get("api_keys", {}).get("doubao")
    
    if not api_key:
        api_key = os.getenv("VOLC_API_KEY")
        
    return api_key, "deepseek-v3-2-251201"

def test_writer_direct():
    print("🚀 Starting Isolation Test: Writer Agent")
    
    api_key, model_id = get_api_config()
    print(f"DEBUG: API Key loaded: {bool(api_key)}")
    print(f"DEBUG: Model ID: {model_id}")

    # Mock State mimicking what Strategist output
    mock_state = {
        "raw_input": "Test Input (max 50 chars)",
        "mode": "mimeng",
        "narrative_type": "opinion",
        "api_config": {
            "provider": "doubao",
            "api_key": api_key,
            "model_id": model_id
        },
        "strategy_json": json.dumps({
            "hook_angle": "Test Angle",
            "pain_point": "Test Pain",
            "outline": ["Point 1", "Point 2"],
            "info_anchors": {"must_mention": [], "key_data": []}
        }),
        "emotion": None
    }
    
    print(">>> Calling writer_agent()...")
    try:
        result = writer_agent(mock_state)
        print(">>> Writer returned:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Exception in writer_agent: {e}")

if __name__ == "__main__":
    test_writer_direct()
