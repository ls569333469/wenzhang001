"""
Writer 模块路由入口
P18: 方案 B - 全模块独立架构

导出:
- get_writer(mode) - 获取对应模式的 Writer 函数
- writer_agent - 旧版统一 Writer (用于修订循环，即将废弃)
"""
from .mid_article import mid_article_writer
from .long_article import long_article_writer
from .short_article import short_article_writer
from .tutorial import tutorial_writer
from .bullish_take import bullish_take_writer
from .kaito_yap import kaito_yap_writer
from .project_research import project_research_writer
from .hot_take import hot_take_writer

# P27: hot_take 已迁入标准管线

WRITER_REGISTRY = {
    "hot_take": hot_take_writer,
    "short_article": short_article_writer,
    "mid_article": mid_article_writer,
    "long_article": long_article_writer,
    "tutorial": tutorial_writer,
    "bullish_take": bullish_take_writer,
    "kaito_yap": kaito_yap_writer,
    "project_research": project_research_writer,
}


def get_writer(mode: str):
    """获取对应模式的 Writer 函数"""
    return WRITER_REGISTRY.get(mode, mid_article_writer)


# P18: 导出旧版 writer_agent 用于修订循环 (从上级目录导入)
# 修订时需要完整的上下文处理逻辑
def writer_agent(state: dict) -> dict:
    """
    旧版统一 Writer - 用于修订循环
    @deprecated 将在 P18 Phase 4 被替换为模块化修订
    """
    # 获取模式并路由到对应 Writer
    mode = state.get("mode", "mid_article")
    writer_fn = get_writer(mode)
    return writer_fn(state)

