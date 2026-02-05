"""
改写 Writer - P18 模块化架构
字数: 无限制 (保持原文长度)
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config

# P18: 硬性约束 (自定义提示词时追加)
HARD_CONSTRAINTS = "\n\n【语言：中文 | 保持原文长度】"


def rewrite_writer(state: dict) -> dict:
    """
    改写 Writer - 保持原文长度的润色改写
    约束已烘焙到模板中，无需运行时注入
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    style = state.get("style", "mimeng")
    
    # 改写模式不使用 Strategist 输出
    # 估算原文长度
    original_length = len(raw_input)
    
    # 构建上下文
    context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "style": style,
        "original_length": original_length,
        "raw_input": raw_input,
        "retention_level": state.get("retention_level", 3),
    }
    
    # P15: 自定义提示词支持
    custom_prompts = state.get("custom_prompts", {})
    if custom_prompts.get("writer"):
        from jinja2 import Environment
        env = Environment()
        system_prompt = env.from_string(custom_prompts["writer"]).render(**context)
        system_prompt += HARD_CONSTRAINTS
    else:
        system_prompt = render_modular_prompt("writer/rewrite.jinja2", context)
    
    user_prompt = f"""原始文本：
{raw_input}

请进行改写润色，保持原意，提升表达。【重要：必须使用中文！】"""

    # 调用 LLM
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    # 改写模式 max_tokens 基于原文长度
    max_tokens = min(int(original_length * 2), 8192)
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.5,  # 改写需要更稳定
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        return {"draft_content": response_text}
    except Exception as e:
        return {"error": f"Error generating content: {str(e)}"}
