"""
短篇 Writer - P25 提示词拆分版
字数: 50-300字 (适合X/Twitter正常发文)
策略官分析素材 → 写手按方案直接写3个版本
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from app.services.sample_service import sample_service
import re
import json

HARD_CONSTRAINTS = "\n\n【字数：50-300字 | 语言：中文】"


def _extract_plans_from_strategy(strategy_json: str) -> list:
    """
    P25: 从策略官输出中提取版本方案
    策略官输出格式: {"material_analysis": {...}, "plans": [...]}
    不再有兜底方案 — 策略官必须输出有效plans
    """
    try:
        obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
        plans = obj.get("plans", [])
        if isinstance(plans, list) and len(plans) > 0:
            print(f"--- [P25] ✅ 从策略官输出提取到 {len(plans)} 个版本方案 ---")
            return plans[:3]
        raise ValueError(f"策略官输出plans为空或无效: {plans}")
    except json.JSONDecodeError as e:
        raise ValueError(f"策略官JSON解析失败: {e}")


def _post_process(text: str) -> str:
    """统一后处理"""
    if not text:
        return text
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'——', '，', text)
    text = re.sub(r'—', '，', text)
    text = text.replace('；', '。')
    text = re.sub(r'^#+\s*.*\n', '', text, flags=re.MULTILINE)
    text = text.strip()
    return text


def _generate_variant(
    raw_input: str,
    plan: dict,
    system_prompt_context: dict,
    length_constraints: dict,
    api_config: dict,
    custom_prompts: dict = None,
) -> str:
    """P26: 根据策略官方案生成单个版本"""
    label = plan.get("label", "")
    angle = plan.get("angle", "")
    hook = plan.get("hook", "")
    tone = plan.get("tone", "")
    emotion_arc = plan.get("emotion_arc", "")
    ending_style = plan.get("ending_style", "")

    # 构建动态 system prompt
    ctx = {**system_prompt_context}
    if custom_prompts and custom_prompts.get("writer"):
        from jinja2 import Environment
        env = Environment()
        system_prompt = env.from_string(custom_prompts["writer"]).render(**ctx)
        system_prompt += HARD_CONSTRAINTS
    else:
        system_prompt = render_modular_prompt("writer/short_article.jinja2", ctx)

    # P26: user prompt — 给方向 + 情感弧线 + 收尾方式
    user_prompt = f"""素材：
{raw_input}

你要写的版本：{label}
角度：{angle}
第一句的方向：{hook}
语气：{tone}
情感走向：{emotion_arc}
收尾方式：{ending_style}

⚠️ 严禁编造素材中没有的事实、场景、对话、数据。只能基于素材内容进行观点重构和表达重构。
⚠️ 记住节奏要求：必须有长短句交替，禁止全篇碎片短句。
直接写。{length_constraints['target']}字左右。第一句就亮出判断。"""

    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints.get("max", 500) * 1.5), 2048)

    # P25: 重试机制 — 遇到 Connection error 时最多重试2次
    import time
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response_text = generate_text(
                prompt=user_prompt,
                api_key=api_key,
                model_id=model_id,
                provider=provider,
                temperature=0.88,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
            )
            return _post_process(response_text)
        except Exception as e:
            if attempt < max_retries and "Connection" in str(e):
                wait_time = 3 * (attempt + 1)
                print(f"--- [P25] ⚠️ {label} 第{attempt+1}次重试（{wait_time}s后）: {e} ---")
                time.sleep(wait_time)
            else:
                raise


def short_article_writer(state: dict) -> dict:
    """
    短篇 Writer - P25 提示词拆分版
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    style = state.get("style", "mimeng")

    mode_config = get_mode_config("short_article")
    length_constraints = mode_config.get("length", {"min": 50, "max": 300, "target": 200})

    custom_length = state.get("custom_length", 0)
    if custom_length and custom_length > 0:
        margin = int(custom_length * 0.2)
        length_constraints = {
            "min": max(100, custom_length - margin),
            "max": custom_length + margin,
            "target": custom_length
        }

    samples = sample_service.get_samples(style=style, count=2)
    rag_context = ""
    if samples:
        rag_context = "\n\n".join([f"--- 样本 ---\n{s.get('content', '')[:300]}" for s in samples])

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
        "rag_context": rag_context,
        "context_card": context_card,
        "forbidden_patterns": load_forbidden_patterns(),
    }

    custom_prompts = state.get("custom_prompts", {})

    # P25: 从策略官输出中提取版本方案（不再自己调LLM分析）
    print("--- [P25] 从策略官输出提取版本方案 ---")
    plans = _extract_plans_from_strategy(strategy_json)
    for i, p in enumerate(plans):
        print(f"  版本{i+1}: {p['label']} | 语气: {p.get('tone','')} | 情感: {p.get('emotion_arc','')} | 收尾: {p.get('ending_style','')}")

    # P25: 写手按策略官方案生成3个版本
    variants = []
    for i, plan in enumerate(plans):
        try:
            print(f"--- [P26] 写手生成版本 {i+1}/3: {plan['label']} ({plan.get('tone','')}) | {plan.get('ending_style','')} ---")
            content = _generate_variant(
                raw_input=raw_input,
                plan=plan,
                system_prompt_context=shared_context,
                length_constraints=length_constraints,
                api_config=api_config,
                custom_prompts=custom_prompts,
            )
            variants.append({
                "key": f"variant_{i+1}",
                "label": plan["label"],
                "methods": plan.get("methods", []),
                "instruction": plan.get("instruction", ""),
                "content": content,
                "char_count": len(content) if content else 0,
            })
        except Exception as e:
            print(f"--- [P25] ❌ 版本 {i+1} 失败: {e} ---")
            variants.append({
                "key": f"variant_{i+1}",
                "label": plan["label"],
                "methods": plan.get("methods", []),
                "instruction": plan.get("instruction", ""),
                "content": f"[生成失败: {e}]",
                "char_count": 0,
            })

    first_content = next((v["content"] for v in variants if v["char_count"] > 0), "")

    return {
        "draft_content": first_content,
        "variants": variants,
    }
