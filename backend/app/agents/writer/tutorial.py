"""
教程 Writer - P18 模块化架构
字数: 400-1500字
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns  # P21

# P18: 硬性约束 (自定义提示词时追加)
HARD_CONSTRAINTS = "\n\n【字数：400-1500字 | 语言：中文】"


def tutorial_writer(state: dict) -> dict:
    """
    教程 Writer - 400-1500字实操教程
    约束已烘焙到模板中，无需运行时注入
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    
    # 获取模式配置
    mode_config = get_mode_config("tutorial")
    length_constraints = mode_config.get("length", {"min": 400, "max": 1500, "target": 800})
    
    # P16: 支持自定义字数覆盖
    custom_length = state.get("custom_length", 0)
    if custom_length and custom_length > 0:
        margin = int(custom_length * 0.2)
        length_constraints = {
            "min": max(100, custom_length - margin),
            "max": custom_length + margin,
            "target": custom_length
        }
    
    # 构建上下文
    context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "length": length_constraints,
        "raw_input": raw_input,
        "strategy_plan": strategy_json,
        "forbidden_patterns": load_forbidden_patterns(),  # P21: 禁用词库
    }
    
    # P15: 自定义提示词支持
    custom_prompts = state.get("custom_prompts", {})
    if custom_prompts.get("writer"):
        from jinja2 import Environment
        env = Environment()
        system_prompt = env.from_string(custom_prompts["writer"]).render(**context)
        system_prompt += HARD_CONSTRAINTS
    else:
        system_prompt = render_modular_prompt("writer/tutorial.jinja2", context)
    
    user_prompt = f"""策略规划：
{strategy_json}

原始素材：
{raw_input}

请现在开始撰写教程。【重要：必须使用中文撰写！】"""

    # 调用 LLM
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    max_tokens = min(int(length_constraints.get("max", 1500) * 1.5), 6144)
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.6,  # 教程需要更稳定的输出
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        return {"draft_content": response_text}
    except Exception as e:
        return {"error": f"Error generating content: {str(e)}"}
