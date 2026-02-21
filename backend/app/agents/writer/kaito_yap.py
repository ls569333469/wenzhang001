from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
import re

def _post_process(text: str) -> str:
    """统一后处理"""
    if not text:
        return text
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'——', '，', text)
    text = re.sub(r'—', '，', text)
    text = text.replace('；', '。')
    text = re.sub(r'^#+\s*.*\n', '', text, flags=re.MULTILINE)
    return text.strip()

def kaito_yap_writer(state: dict) -> dict:
    """
    Kaito 嘴撸模式 Writer - 数据分析与 Degen 视角
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    web3_knowledge = state.get("web3_knowledge", "")

    mode_config = get_mode_config("kaito_yap")
    length_constraints = mode_config.get("length", {"min": 150, "max": 400, "target": 250})

    shared_context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "length": length_constraints,
        "raw_input": raw_input,
        "strategy_json": strategy_json,
        "web3_knowledge": web3_knowledge,
        "forbidden_patterns": load_forbidden_patterns(),
    }

    system_prompt = render_modular_prompt("writer/kaito_yap.jinja2", shared_context)
    
    user_prompt = f"""分析目标：
{raw_input}

要求：直接输出你的推文或内容，无需任何前言、后记、Markdown 代码块或标题。目标字数 {length_constraints['target']} 字左右。"""

    provider = api_config.get("provider", "grok")  # 默认 Grok
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints.get("max", 600) * 1.5), 2048)

    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.8, # Kaito Yapper 稍微高点的温度带来更多的阴阳怪气或幽默
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )
        content = _post_process(response_text)
    except Exception as e:
        print(f"--- [kaito_yap] Writer Error: {e} ---")
        content = f"[生成失败: {e}]"

    return {
        "draft_content": content,
    }
