"""
P21: 禁用词库加载器
集中管理 AI 高频禁用词库，供所有 Agent 使用
"""
from pathlib import Path
import yaml
from typing import Dict, Any, List

# 定位到 backend/data/config
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "config"
PATTERNS_FILE = DATA_DIR / "forbidden_patterns.yaml"

_cache = None


def load_forbidden_patterns() -> Dict[str, Any]:
    """
    加载禁用词库 (带缓存)
    
    Returns:
        禁用词库字典，按类别分组
    """
    global _cache
    if _cache is None:
        if PATTERNS_FILE.exists():
            try:
                with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
                    _cache = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[P21] Warning: Failed to load forbidden patterns: {e}")
                _cache = {}
        else:
            print(f"[P21] Warning: forbidden_patterns.yaml not found at {PATTERNS_FILE}")
            _cache = {}
    return _cache


def get_all_forbidden_words() -> List[str]:
    """
    获取所有禁用词的扁平列表 (去重)
    
    Returns:
        所有禁用词的列表
    """
    patterns = load_forbidden_patterns()
    words = []
    for category in patterns.values():
        if isinstance(category, dict):
            for lang_list in category.values():
                if isinstance(lang_list, list):
                    words.extend(lang_list)
        elif isinstance(category, list):
            words.extend(category)
    return list(set(words))


def get_forbidden_summary(max_per_category: int = 10) -> str:
    """
    获取禁用词摘要文本 (用于注入提示词)
    
    Args:
        max_per_category: 每类最多显示多少个词
        
    Returns:
        格式化的禁用词摘要
    """
    patterns = load_forbidden_patterns()
    if not patterns:
        return ""
    
    lines = ["【禁用词约束】严禁使用以下 AI 高频词："]
    for category, items in patterns.items():
        if isinstance(items, dict):
            for lang, words in items.items():
                if isinstance(words, list) and words:
                    sample = words[:max_per_category]
                    lines.append(f"- {category}({lang}): {', '.join(sample)}")
        elif isinstance(items, list) and items:
            sample = items[:max_per_category]
            lines.append(f"- {category}: {', '.join(sample)}")
    
    return "\n".join(lines)


def clear_cache():
    """清除缓存 (用于测试或热重载)"""
    global _cache
    _cache = None
