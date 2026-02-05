"""
Writer 模块路由入口
P18: 方案 B - 全模块独立架构

导出:
- get_writer(mode) - 获取对应模式的 Writer 函数
- writer_agent - 旧版统一 Writer (用于修订循环，即将废弃)
"""
from .mid_article import mid_article_writer
from .long_article import long_article_writer
from .tutorial import tutorial_writer
from .rewrite import rewrite_writer

# hot_take 保持独立 (Option A)，不纳入此路由

WRITER_REGISTRY = {
    "mid_article": mid_article_writer,
    "long_article": long_article_writer,
    "tutorial": tutorial_writer,
    "rewrite": rewrite_writer,
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

