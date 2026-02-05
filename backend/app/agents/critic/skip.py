"""
跳过 Critic - P18 模块化架构
适用于: hot_take (锐评模式跳过评分)
"""


def skip_critic(draft: str, mode: str = "hot_take", api_config: dict = None,
                length: str = "tweet", style: str = "auto", 
                custom_prompts: dict = None) -> dict:
    """
    跳过 Critic - 锐评模式不需要评分
    直接返回 PASS 状态
    """
    return {
        "score": 100,
        "verdict": "PASS",
        "dimensions": {},
        "penalties": [],
        "suggestions": ["锐评模式跳过评分"],
        "cot_analysis": "hot_take mode: Critic skipped",
        "initial_score": 100,
        "skipped": True
    }
