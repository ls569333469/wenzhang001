"""
Critic 模块路由入口
P18: 方案 B - 全模块独立架构

导出:
- get_critic(mode) - 获取对应模式的 Critic 函数
"""
from .standard import standard_critic
from .skip import skip_critic
from .research_cleaner import research_cleaner  # P31

CRITIC_REGISTRY = {
    "short_article": standard_critic,  # P24: 补注册
    "mid_article": standard_critic,
    "long_article": standard_critic,
    "tutorial": standard_critic,
    "hot_take": skip_critic,  # 锐评跳过评分
    "bullish_take": standard_critic,   # P27: 吹捧模式 — 专用模板
    "kaito_yap": standard_critic,      # P27: Kaito 嘴撸 — 专用模板
    "project_research": research_cleaner,  # P31: 投研 — 数据清洗（不打分）
    "binance_square": standard_critic,  # P34: 币安广场 — 合规审查
}


def get_critic(mode: str):
    """获取对应模式的 Critic 函数"""
    return CRITIC_REGISTRY.get(mode, standard_critic)



