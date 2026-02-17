"""
BaseFetcher - 素材源抽象基类
P23: 所有数据源爬虫继承此类
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseFetcher(ABC):
    """素材源抽象基类"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源名称 (中文)"""
        ...

    @abstractmethod
    def fetch_latest(self, count: int = 100) -> List[Dict]:
        """
        抓取最新素材

        Returns: [{
            "source": "链捕手",
            "title": "标题",
            "url": "https://...",
            "content": "正文内容",
            "published_at": "2026-02-08T14:30:00",
            "content_type": "快讯" | "长文",
        }, ...]
        """
        ...
