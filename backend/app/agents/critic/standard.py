"""
标准 Critic - P24 全模式独立管线
适用于: short_article, mid_article, long_article, tutorial
每个模式使用独立 jinja2 模板（critic/{mode}.jinja2）
"""
from datetime import datetime
import json
import logging
from app.core.llm import generate_text
from app.core.prompts import render_prompt
from app.core.mode_configs import get_mode_config, SCORING_DIMENSIONS, PENALTY_RULES
from app.core.forbidden_patterns import load_forbidden_patterns  # P21

logger = logging.getLogger(__name__)


def standard_critic(draft: str, mode: str, api_config: dict = None,
                    length: str = "thread", style: str = "auto", 
                    custom_prompts: dict = None,
                    strategy_json: str = None,
                    variant_index: int = 0) -> dict:
    """
    标准 Critic - 5维度评分系统
    约束已烘焙到模板中
    variant_index: P30 吹捧模式按版本索引取对应plan（0/1/2）
    """
    if api_config is None:
        api_config = {}
    if custom_prompts is None:
        custom_prompts = {}
    
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    # P16: 使用 mode_configs 字数配置
    mode_config = get_mode_config(mode)
    length_constraints = mode_config.get("length", {"min": 400, "max": 800, "target": 500})
    word_count = len(draft)
    
    # P24: 注入模式专用评分配置
    scoring = mode_config.get("scoring", {})
    
    # P29/P30: 从策略官 JSON 提取对应版本的字段
    logic_pattern = ""
    tone = ""
    perspective = ""
    story = ""
    detail = ""
    if strategy_json:
        try:
            strategy_obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
            plans = strategy_obj.get("plans", [])
            if plans and isinstance(plans, list):
                # P30-fix: 按 variant_index 取对应版本的 plan，而非始终 plans[0]
                idx = min(variant_index, len(plans) - 1) if variant_index >= 0 else 0
                plan = plans[idx]
                logic_pattern = plan.get("logic_pattern", "")
                tone = plan.get("tone", "")
                perspective = plan.get("perspective", "")
                story = plan.get("story", "")
                detail = plan.get("detail", "")
                logger.info(f"[P30] Critic 对照版本{idx+1}: perspective={perspective}, tone={tone}")
        except (json.JSONDecodeError, TypeError):
            pass
    
    context = {
        "current_time_str": datetime.now().isoformat(),
        "mode": mode,
        "mode_name": mode_config.get("name", mode),
        "length": length,
        "length_constraints": length_constraints,
        "style": style,
        "word_count": word_count,
        "draft": draft,
        "forbidden_patterns": load_forbidden_patterns(),  # P21: 禁用词库
        # P24: 模式专用评分参数
        "dimensions": scoring.get("dimensions", SCORING_DIMENSIONS),
        "penalty_rules": scoring.get("penalty_rules", PENALTY_RULES),
        "penalty_cap": scoring.get("penalty_cap", 30),
        "pass_threshold": scoring.get("pass_threshold", 85),
        "refine_threshold": scoring.get("refine_threshold", 70),
        # P29/P30: 策略官上下文
        "logic_pattern": logic_pattern,
        "tone": tone,
        "perspective": perspective,
        "story": story,
        "detail": detail,
    }

    
    # P15: Custom Prompt Support
    if custom_prompts.get("critic"):
        from jinja2 import Environment
        env = Environment()
        system_prompt = env.from_string(custom_prompts["critic"]).render(
            **context,
            raw_input=draft
        )
    else:
        # P24: 加载模式专用模板 (critic/short_article.jinja2 等)
        system_prompt = render_prompt(f"critic/{mode}", context)

    user_prompt = """请严格按照系统提示中的评审流程和输出格式进行评分，输出纯JSON。"""
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.1,
            system_prompt=system_prompt
        )
        
        # Parse JSON result
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(text)
        
        # P26-fix: 短篇 Critic 模板只返回 verdict/reason/suggestions，不含 score
        # 从 verdict 推导 score 以确保 router_logic 正常工作
        raw_score = result.get("final_score", result.get("score", 0))
        verdict = result.get("verdict", "")
        if raw_score == 0 and verdict:
            verdict_score_map = {"PASS": 90, "REFINE": 75, "REWRITE": 50}
            raw_score = verdict_score_map.get(verdict.upper(), 75)
        
        return {
            "score": raw_score,
            "verdict": verdict or _calculate_verdict(raw_score, mode),
            "dimensions": result.get("dimensions", {}),
            "penalties": result.get("penalties", []),
            "suggestions": result.get("suggestions", []),
            "cot_analysis": result.get("cot_analysis", ""),
            "initial_score": result.get("initial_score", 0)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Critic JSON parse error: {e}")
        return _fallback_result(f"JSON解析失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"Critic Error: {e}")
        return _fallback_result(f"评审错误: {str(e)}")


def _calculate_verdict(score: int, mode: str = "mid_article") -> str:
    """根据分数和模式计算 verdict"""
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
    """返回兜底结果"""
    return {
        "score": 75,
        "verdict": "REFINE",
        "dimensions": {},
        "penalties": [],
        "suggestions": [error_msg],
        "cot_analysis": "",
        "initial_score": 75
    }
