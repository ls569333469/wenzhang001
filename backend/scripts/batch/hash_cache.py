"""
Hash Cache Module
=================
本地缓存已处理的内容 Hash，避免重复上传到 Lark。
比 Lark API 查重快 100 倍+。
"""

import json
import hashlib
from pathlib import Path
from typing import Set, Optional
from app.core.config import get_logger

logger = get_logger("hash_cache")


class HashCache:
    """本地 Hash 缓存，用于快速查重"""
    
    def __init__(self, cache_file: str = "processed_hashes.json"):
        """
        初始化 Hash 缓存
        
        Args:
            cache_file: 缓存文件路径 (相对于 backend 目录)
        """
        self.cache_file = Path(__file__).parent.parent.parent / "data" / cache_file
        self.hashes: Set[str] = self._load()
        logger.info(f"Loaded {len(self.hashes)} hashes from cache")
    
    def _load(self) -> Set[str]:
        """从文件加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data) if isinstance(data, list) else set()
            except Exception as e:
                logger.warning(f"Failed to load hash cache: {e}")
                return set()
        return set()
    
    def contains(self, content_hash: str) -> bool:
        """检查 hash 是否已存在"""
        return content_hash in self.hashes
    
    def add(self, content_hash: str) -> None:
        """添加新的 hash 到缓存"""
        self.hashes.add(content_hash)
    
    def add_many(self, hashes: list) -> None:
        """批量添加 hash"""
        self.hashes.update(hashes)
    
    def save(self) -> None:
        """保存缓存到文件"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(list(self.hashes), f, indent=2)
            logger.info(f"Saved {len(self.hashes)} hashes to cache")
        except Exception as e:
            logger.error(f"Failed to save hash cache: {e}")
    
    def clear(self) -> None:
        """清空缓存"""
        self.hashes.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Hash cache cleared")
    
    def __len__(self) -> int:
        return len(self.hashes)
    
    def __contains__(self, item: str) -> bool:
        return self.contains(item)


def compute_content_hash(content: str) -> str:
    """计算内容的 MD5 哈希"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


# 单例实例
_cache_instance: Optional[HashCache] = None


def get_hash_cache() -> HashCache:
    """获取全局 HashCache 单例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = HashCache()
    return _cache_instance
