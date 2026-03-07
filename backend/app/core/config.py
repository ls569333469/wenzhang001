import os
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone, timedelta

# P33: 统一时区 — VPS 在美国，业务时间用中国时区 (UTC+8)
CN_TZ = timezone(timedelta(hours=8))

def cn_now() -> datetime:
    """返回中国时区的当前时间"""
    return datetime.now(CN_TZ)

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
        logger.setLevel(logging.INFO)
        
        # 1. Stream Handler (Console)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
        # 2. File Handler (Monitor Log)
        try:
            log_dir = BASE_DIR / "logs"
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "app_monitor.log", encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
            
    return logger


def get_feature_flag(flag_name: str, default: bool = False) -> bool:
    """
    获取 Feature Flag 配置
    
    Args:
        flag_name: Feature flag 名称
        default: 默认值
        
    Returns:
        Feature flag 的值
    """
    config = load_config()
    flags = config.get("feature_flags", {})
    return flags.get(flag_name, default)


def set_feature_flag(flag_name: str, value: bool):
    """
    设置 Feature Flag 配置
    
    Args:
        flag_name: Feature flag 名称
        value: 要设置的值
    """
    config = load_config()
    if "feature_flags" not in config:
        config["feature_flags"] = {}
    config["feature_flags"][flag_name] = value
    save_config(config)
