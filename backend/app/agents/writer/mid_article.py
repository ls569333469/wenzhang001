"""
中篇 Writer - P18 模块化架构
字数: 150-800字
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.services.sample_service import sample_service

# P18: 硬性约束 (自定义提示词时追加)
HARD_CONSTRAINTS = "\n\n【字数：150-800字 | 语言：中文】"


def mid_article_writer(state: dict) -> dict:
    """
    中篇 Writer - 150-800字分析文章
    约束已烘焙到模板中，无需运行时注入
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    style = state.get("style", "mimeng")
    
    # 获取模式配置
    mode_config = get_mode_config("mid_article")
    length_constraints = mode_config.get("length", {"min": 150, "max": 800, "target": 500})
    
    # P16: 支持自定义字数覆盖
    custom_length = state.get("custom_length", 0)
    if custom_length and custom_length > 0:
        margin = int(custom_length * 0.2)
        length_constraints = {
            "min": max(50, custom_length - margin),
            "max": custom_length + margin,
            "target": custom_length
        }
    
    # 获取样本
    samples = sample_service.get_samples(style=style, count=3)
    rag_context = ""
    if samples:
        rag_context = "\n\n".join([f"--- 样本 ---\n{s.get('content', '')[:500]}" for s in samples])
    
    # P20: 从策略 JSON 中提取 context_card
    context_card = None
    try:
        import json
        strategy_obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
        context_card = strategy_obj.get("context_card")
        if context_card:
            from app.core.config import get_logger
            logger = get_logger("writer")
            logger.info(f"[P20] ✅ Writer 收到 context_card: time_context={context_card.get('time_context')}")
    except:
        pass
    
    # 构建上下文
    context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "style": style,
        "length": length_constraints,
        "retention_level": state.get("retention_level", 3),
        "raw_input": raw_input,
        "strategy_plan": strategy_json,
        "rag_context": rag_context,
        "context_card": context_card,  # P20: 事件脉络卡片
    }
    
    # P15: 自定义提示词支持
    custom_prompts = state.get("custom_prompts", {})
    if custom_prompts.get("writer"):
        from jinja2 import Environment
        env = Environment()
        system_prompt = env.from_string(custom_prompts["writer"]).render(**context)
        system_prompt += HARD_CONSTRAINTS  # 强制追加约束
    else:
        # 使用标准模板 (约束已烘焙)
        system_prompt = render_modular_prompt("writer/mid_article.jinja2", context)
    
    user_prompt = f"""策略规划：
{strategy_json}

原始素材：
{raw_input}

请现在开始撰写文章。【重要：必须使用中文撰写！】"""

    # 调用 LLM
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    max_tokens = min(int(length_constraints.get("max", 800) * 1.5), 4096)
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.65,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        return {"draft_content": response_text}
    except Exception as e:
        return {"error": f"Error generating content: {str(e)}"}
