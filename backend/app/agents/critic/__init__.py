"""
Critic 模块路由入口
P18: 方案 B - 全模块独立架构

导出:
- get_critic(mode) - 获取对应模式的 Critic 函数
- critic_agent - 旧版统一 Critic (向后兼容)
"""
from .standard import standard_critic
from .skip import skip_critic

CRITIC_REGISTRY = {
    "short_article": standard_critic,  # P24: 补注册
    "mid_article": standard_critic,
    "long_article": standard_critic,
    "tutorial": standard_critic,
    "hot_take": skip_critic,  # 锐评跳过评分
}


def get_critic(mode: str):
    """获取对应模式的 Critic 函数"""
    return CRITIC_REGISTRY.get(mode, standard_critic)


def critic_agent(draft: str, mode: str, api_config: dict = None, 
                 length: str = "thread", style: str = "auto", custom_prompts: dict = None,
                 strategy_json: str = None) -> dict:
    """
    旧版统一 Critic - 向后兼容
    @deprecated 将在 P18 Phase 4 被替换为模块化调用
    """
    critic_fn = get_critic(mode)
    return critic_fn(
        draft=draft,
        mode=mode,
        api_config=api_config or {},
        length=length,
        style=style,
        custom_prompts=custom_prompts or {},
        strategy_json=strategy_json
    )
