"""
Polisher 模块路由入口
P18: 方案 B - 全模块独立架构

导出:
- get_polisher(mode) - 获取对应模式的 Polisher 函数
"""
from .standard import standard_polisher
from .skip import skip_polisher
from .short_article import short_article_polisher

POLISHER_REGISTRY = {
    "mid_article": standard_polisher,
    "long_article": standard_polisher,
    "tutorial": standard_polisher,
    "hot_take": skip_polisher,   # 锐评跳过润色
    "short_article": short_article_polisher,  # P26: 代码预扫+LLM最小修复
    "bullish_take": standard_polisher,   # P27: 吹捧模式 — 专用模板
    "kaito_yap": standard_polisher,      # P27: Kaito 嘴撸 — 专用模板
    "project_research": standard_polisher,  # P27: 投研 — 专业化打磨
    "binance_square": skip_polisher,  # P34: 币安广场 — 跳过润色（短内容）
}


def get_polisher(mode: str):
    """获取对应模式的 Polisher 函数"""
    return POLISHER_REGISTRY.get(mode, standard_polisher)



