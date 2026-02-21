"""
Polisher 模块路由入口
P18: 方案 B - 全模块独立架构

导出:
- get_polisher(mode) - 获取对应模式的 Polisher 函数
- polisher_agent - 旧版统一 Polisher (向后兼容)
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
}


def get_polisher(mode: str):
    """获取对应模式的 Polisher 函数"""
    return POLISHER_REGISTRY.get(mode, standard_polisher)


def polisher_agent(draft: str, critique_feedback: str, api_config: dict = None, 
                   custom_prompts: dict = None, mode: str = "mid_article",
                   length_constraints: dict = None) -> str:
    """
    旧版统一 Polisher - 向后兼容
    @deprecated 将在 P18 Phase 4 被替换为模块化调用
    """
    polisher_fn = get_polisher(mode)
    return polisher_fn(
        draft=draft,
        critique_feedback=critique_feedback,
        api_config=api_config or {},
        custom_prompts=custom_prompts or {},
        mode=mode,
        length_constraints=length_constraints
    )
