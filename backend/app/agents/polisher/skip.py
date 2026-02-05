"""
跳过 Polisher - P18 模块化架构
适用于: hot_take (锐评模式跳过润色)
"""


def skip_polisher(draft: str, critique_feedback: str = "", api_config: dict = None,
                  custom_prompts: dict = None, mode: str = "hot_take",
                  length_constraints: dict = None) -> str:
    """
    跳过 Polisher - 锐评模式直接返回原始内容
    """
    return draft
