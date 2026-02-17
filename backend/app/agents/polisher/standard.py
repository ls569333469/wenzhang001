"""
标准 Polisher - P24 全模式独立管线
适用于: mid_article, long_article, tutorial, rewrite
每个模式使用独立 jinja2 模板（polisher/{mode}.jinja2）
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_prompt
from app.core.forbidden_patterns import load_forbidden_patterns  # P21


def standard_polisher(draft: str, critique_feedback: str, api_config: dict = None, 
                      custom_prompts: dict = None, mode: str = "mid_article",
                      length_constraints: dict = None) -> str:
    """
    标准 Polisher - P24 模式专用润色
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
    
    context = {
        "current_time_str": datetime.now().isoformat(),
        "forbidden_patterns": load_forbidden_patterns(),  # P21: 禁用词库
        # P24: 注入草稿和反馈到模板上下文
        "draft": draft,
        "critique_feedback": critique_feedback,
        "length_constraints": length_constraints,
        "mode": mode,
    }

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
        # P24: 加载模式专用模板 (polisher/mid_article.jinja2 等)
        system_prompt = render_prompt(f"polisher/{mode}", context)
        user_prompt = f"请现在润色内容。【重要：必须使用中文输出！字数上限: {max_words}字】"
    
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
        
        # P22 v4: 后处理 - 清除禁止符号
        import re
        if response_text:
            response_text = re.sub(r'——', '，', response_text)
            response_text = re.sub(r'—', '，', response_text)
        
        return response_text
    except Exception as e:
        return f"Error polishing content: {str(e)}"
