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
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 相比于其他轻量级短篇，投研分析允许保留更多的标点符号，我们只清理think tag
    return text.strip()

def project_research_writer(state: dict) -> dict:
    """
    投研分析 Writer - 机构级客观研究简报
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    web3_knowledge = state.get("web3_knowledge", "")

    mode_config = get_mode_config("project_research")
    length_constraints = mode_config.get("length", {"min": 800, "max": 1500, "target": 1000})

    shared_context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "length": length_constraints,
        "raw_input": raw_input,
        "strategy_json": strategy_json,
        "web3_knowledge": web3_knowledge,
        "forbidden_patterns": load_forbidden_patterns(),
    }

    system_prompt = render_modular_prompt("writer/project_research.jinja2", shared_context)
    
    user_prompt = f"""投研标的：
{raw_input}

要求：直接输出你的高质量投研分析正文，无需任何前言、后记（可以使用 Markdown 标题进行分点）。目标字数 {length_constraints['target']} 字左右。"""

    provider = api_config.get("provider", "grok")  # 默认 Grok
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints.get("max", 1500) * 1.5), 3000)

    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.4, # 投研模式温度较低，追求客观严谨
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )
        content = _post_process(response_text)
    except Exception as e:
        print(f"--- [project_research] Writer Error: {e} ---")
        content = f"[生成失败: {e}]"

    return {
        "draft_content": content,
    }
