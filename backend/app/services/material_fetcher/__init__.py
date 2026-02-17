"""
Material Fetcher module - 素材源爬虫
P23: 预留多数据源扩展接口

get_fetcher(source) → BaseFetcher 子类实例
"""

from .chaincatcher import ChainCatcherFetcher

FETCHER_REGISTRY = {
    "chaincatcher": ChainCatcherFetcher,
}


def get_fetcher(source: str):
    """获取指定数据源的 Fetcher 实例"""
    cls = FETCHER_REGISTRY.get(source)
    if not cls:
        raise ValueError(f"Unknown source: {source}. Available: {list(FETCHER_REGISTRY.keys())}")
    return cls()
