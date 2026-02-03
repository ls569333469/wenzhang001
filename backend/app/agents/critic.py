from datetime import datetime
import json
import logging
from ..core.llm import generate_text
from ..core.prompts import render_prompt
# P16: 移除旧的 calculate_length，改用 mode_configs
from ..core.mode_configs import get_mode_config  # P14

logger = logging.getLogger(__name__)

def critic_agent(draft: str, mode: str, api_config: dict = None, 
                 length: str = "thread", style: str = "auto", custom_prompts: dict = None) -> dict:
    """
    P12: Critic Agent - 5维度评分系统 (P15: Support Custom Prompts)
    """
    if api_config is None:
        api_config = {}
    if custom_prompts is None:
        custom_prompts = {}
    
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    # P16: 使用 mode_configs 字数配置 (统一来源)
    mode_config = get_mode_config(mode)
    length_constraints = mode_config.get("length", {"min": 400, "max": 800, "target": 500})
    word_count = len(draft)
    print(f">>> [Critic Debug] Using mode_config length: {length_constraints}")
    
    context = {
        "current_time_str": datetime.now().isoformat(),
        "mode": mode,
        "length": length,
        "length_constraints": length_constraints,
        "style": style,
        "word_count": word_count,
        "draft": draft
    }
    
    # P15: Custom Prompt Support
    if custom_prompts.get("critic"):
        from jinja2 import Environment
        env = Environment()
        # Custom prompt expects {{ raw_input }} which corresponds to draft here
        system_prompt = env.from_string(custom_prompts["critic"]).render(
            **context,
            raw_input=draft
        )
    else:
        system_prompt = render_prompt("critic", context)

    user_prompt = """请严格按照系统提示中的评审流程和输出格式进行评分，输出纯JSON。"""
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.1,  # 低温度保证评分稳定
            system_prompt=system_prompt
        )
        
        # Parse JSON result
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(text)
        
        # P12: 返回完整的评分结构
        return {
            "score": result.get("final_score", result.get("score", 0)),
            "verdict": result.get("verdict", _calculate_verdict(result.get("final_score", 0), mode)),
            "dimensions": result.get("dimensions", {}),
            "penalties": result.get("penalties", []),
            "suggestions": result.get("suggestions", []),
            "cot_analysis": result.get("cot_analysis", ""),
            "initial_score": result.get("initial_score", 0)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Critic JSON parse error: {e}, response: {response_text[:200]}")
        return _fallback_result(f"JSON解析失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"Critic Error: {e}")
        return _fallback_result(f"评审错误: {str(e)}")


def _calculate_verdict(score: int, mode: str = "mid_article") -> str:  # P16
    """根据分数和模式计算 verdict (P14: 使用 mode_configs 阈值)"""
    config = get_mode_config(mode)
    scoring = config.get("scoring", {})
    pass_threshold = scoring.get("pass_threshold", 85)
    refine_threshold = scoring.get("refine_threshold", 70)
    
    if score >= pass_threshold:
        return "PASS"
    elif score >= refine_threshold:
        return "REFINE"
    else:
        return "REWRITE"


def _fallback_result(error_msg: str) -> dict:
    """返回兜底结果，避免系统崩溃"""
    return {
        "score": 75,  # 兜底分数
        "verdict": "REFINE",
        "dimensions": {},
        "penalties": [],
        "suggestions": [error_msg],
        "cot_analysis": "",
        "initial_score": 75
    }
