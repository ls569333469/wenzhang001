from datetime import datetime
from ..core.llm import generate_text
from ..core.prompts import render_prompt

def polisher_agent(draft: str, critique_feedback: str, api_config: dict = None, 
                   custom_prompts: dict = None, mode: str = "mid_article",
                   length_constraints: dict = None) -> str:
    """
    Step 4: Polish
    Final touches and slang injection. P16.1: Added length constraint enforcement.
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
    
    # P16.1: 字数约束注入
    max_words = length_constraints.get("max", 800)
    length_instruction = f"\n\n⚠️ 【重要】最终输出必须控制在 {max_words} 字以内！当前草稿如果超过此字数，请精简内容而非扩展。"
    
    context = {"current_time_str": datetime.now().isoformat()}

    # P15: Custom Prompt Support
    if custom_prompts.get("polisher"):
        from jinja2 import Environment
        env = Environment()
        # Combine input for polisher
        combined_input = f"Draft:\n{draft}\n\nFeedback:\n{critique_feedback}"
        system_prompt = env.from_string(custom_prompts["polisher"]).render(
            **context,
            raw_input=combined_input
        )
        # P16.1: 强制注入中文要求和字数限制
        system_prompt += f"\n\n【系统强制要求】\n1. 必须使用中文输出！\n2. 字数控制在 {max_words} 字以内！" + length_instruction
        user_prompt = "请现在润色内容。【重要：必须使用中文输出！】"
    else:
        system_prompt = render_prompt("polisher", context) + length_instruction
        user_prompt = f"""草稿: {draft}

编辑反馈: {critique_feedback}

请现在润色内容。【重要：必须使用中文输出！字数上限: {max_words}字】"""
    
    # P16.1: 计算 max_tokens 限制
    calculated_max_tokens = min(int(max_words * 1.5), 16384)
    print(f">>> [Polisher Debug] max_tokens={calculated_max_tokens} (max_words={max_words})")
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.7,
            system_prompt=system_prompt,
            max_tokens=calculated_max_tokens  # P16.1: 强制 token 限制
        )
        print(f">>> [Polisher Debug] Output length: {len(response_text)} chars")
        return response_text
    except Exception as e:
        return f"Error polishing content: {str(e)}"
