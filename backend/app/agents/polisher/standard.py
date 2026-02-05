"""
标准 Polisher - P18 模块化架构
适用于: mid_article, long_article, tutorial, rewrite
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_prompt


def standard_polisher(draft: str, critique_feedback: str, api_config: dict = None, 
                      custom_prompts: dict = None, mode: str = "mid_article",
                      length_constraints: dict = None) -> str:
    """
    标准 Polisher - 最终润色和语言风格注入
    约束已烘焙到模板中
    """
    if api_config is None:
        api_config = {}
    if custom_prompts is None:
        custom_prompts = {}
    if length_constraints is None:
        length_constraints = {"min": 150, "max": 800, "target": 500}
    
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    max_words = length_constraints.get("max", 800)
    
    context = {"current_time_str": datetime.now().isoformat()}

    # P15: Custom Prompt Support
    if custom_prompts.get("polisher"):
        from jinja2 import Environment
        env = Environment()
        combined_input = f"Draft:\n{draft}\n\nFeedback:\n{critique_feedback}"
        system_prompt = env.from_string(custom_prompts["polisher"]).render(
            **context,
            raw_input=combined_input
        )
        # P18: 硬性约束追加
        system_prompt += f"\n\n【字数：{max_words}字以内 | 语言：中文】"
        user_prompt = "请现在润色内容。【重要：必须使用中文输出！】"
    else:
        system_prompt = render_prompt("polisher", context)
        user_prompt = f"""草稿: {draft}

编辑反馈: {critique_feedback}

请现在润色内容。【重要：必须使用中文输出！字数上限: {max_words}字】"""
    
    calculated_max_tokens = min(int(max_words * 1.5), 16384)
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.7,
            system_prompt=system_prompt,
            max_tokens=calculated_max_tokens
        )
        return response_text
    except Exception as e:
        return f"Error polishing content: {str(e)}"
