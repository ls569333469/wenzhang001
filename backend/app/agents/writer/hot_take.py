"""
锐评 Writer - P27 迁入完整管线
字数: 50-150字
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
import re
import json

def _post_process(text: str) -> str:
    """统一后处理"""
    if not text:
        return text
    # 移除思考标签
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 移除破折号
    text = re.sub(r'——', '，', text)
    text = re.sub(r'—', '，', text)
    # 分号转句号
    text = text.replace('；', '。')
    # 移除 Markdown 标题
    text = re.sub(r'^#+\s*.*\n', '', text, flags=re.MULTILINE)
    return text.strip()


def hot_take_writer(state: dict) -> dict:
    """
    锐评 Writer - 50-150字极简短评
    P27: 迁入标准 LangGraph 管线 (从独立 /hot_take API 迁入)
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    style = state.get("style", "mimeng")

    mode_config = get_mode_config("hot_take")
    length_constraints = mode_config.get("length", {"min": 50, "max": 150, "target": 80})

    # P20: 从策略 JSON 中提取 context_card
    context_card = None
    try:
        strategy_obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
        context_card = strategy_obj.get("context_card")
    except:
        pass

    shared_context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "style": style,
        "length": length_constraints,
        "retention_level": state.get("retention_level", 3),
        "raw_input": raw_input,
        "strategy_plan": strategy_json,
        "context_card": context_card,
        "forbidden_patterns": load_forbidden_patterns(),
    }

    # 渲染 Prompt
    system_prompt = render_modular_prompt("writer/hot_take.jinja2", shared_context)

    user_prompt = f"""素材输入：
{raw_input}

要求：直接输出你的锐评短评，无需任何前言、后记、Markdown 代码块或标题。目标字数 {length_constraints['target']} 字左右。"""

    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints.get("max", 150) * 2), 1024)

    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.8,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )
        content = _post_process(response_text)
    except Exception as e:
        print(f"--- [hot_take] Writer Error: {e} ---")
        content = f"[内容生成失败: {e}]"

    return {
        "draft_content": content,
    }
