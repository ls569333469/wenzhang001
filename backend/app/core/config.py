import os
import json
from pathlib import Path
from typing import Dict, Any

# 配置文件路径: backend/config/user_config.json
# 假设当前文件在 backend/app/core/config.py，向前推 3 级目录到 backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "user_config.json"

def ensure_config_dir():
    """Ensure the configuration directory exists."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Config] Error loading config: {e}")
        return {}

def save_config(config: Dict[str, Any]):
    """Save configuration to JSON file."""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"[Config] Error saving config: {e}")
        raise e

def get_api_key(key_name: str) -> str:
    """
    Get API key with priority:
    1. Config file (user_config.json)
    2. Environment variable
    """
    # 1. Try config file
    config = load_config()
    api_keys = config.get("api_keys", {})
    if key_name in api_keys and api_keys[key_name]:
        return api_keys[key_name]
    
    # 2. Try environment variable
    # Map common key names to environment variables if needed
    env_map = {
        "gemini": "GOOGLE_GENAI_API_KEY",
        "doubao": "ARK_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY"
    }
    env_var = env_map.get(key_name, key_name.upper())
    return os.environ.get(env_var, "")

import logging

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
