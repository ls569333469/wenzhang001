"""
吹捧 Writer - P30 对齐 P29 短篇架构
3 版本生成：策略官 3 个方案 → 写手分别执行
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from app.services.google_sheets_source import google_sheets_source
import re
import json
import time


def _extract_plans(strategy_json: str) -> list:
    """从策略官输出提取版本方案"""
    try:
        obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
        plans = obj.get("plans", [])
        if isinstance(plans, list) and len(plans) > 0:
            print(f"--- [P30] ✅ 从策略官提取到 {len(plans)} 个吹捧方案 ---")
            return plans[:3]
        raise ValueError(f"策略官输出plans为空: {plans}")
    except json.JSONDecodeError as e:
        raise ValueError(f"策略官JSON解析失败: {e}")


def _get_rag_samples() -> str:
    """获取风格样本 — 暂用半佛积极情绪样本，后续切换CZ转发推文样本"""
    try:
        samples = google_sheets_source.get_samples(
            style="banfo", emotion="积极", count=2
        )
        if not samples:
            return ""
        parts = []
        for i, s in enumerate(samples, 1):
            content = s.get("content", "")
            if content:
                parts.append(f"--- 样本({s.get('snippet_type','')}) ---\n{content[:300]}")
        return "\n\n".join(parts)
    except Exception as e:
        print(f"[bullish_take] RAG sample fetch failed: {e}")
        return ""


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


def _generate_variant(
    raw_input: str,
    plan: dict,
    system_prompt_context: dict,
    length_constraints: dict,
    api_config: dict,
) -> str:
    """根据策略官方案生成单个版本"""
    label = plan.get("label", "")
    perspective = plan.get("perspective", "")
    story = plan.get("story", "")
    hook = plan.get("hook", "")
    detail = plan.get("detail", "")
    tone = plan.get("tone", "")
    logic_pattern = plan.get("logic_pattern", "")


    system_prompt = render_modular_prompt("writer/bullish_take.jinja2", system_prompt_context)

    user_prompt = f"""素材：
{raw_input}

你要写的版本：{label}
切入视角：{perspective}
这篇内容讲的故事：{story}
第一句的方向：{hook}
用这个事实/数据支撑：{detail}
语气：{tone}
写作公式：{logic_pattern}

⚠️ 严禁编造素材中没有的事实、数据、引言。
⚠️ 记住节奏要求：必须有长短句交替，禁止全篇碎片短句。
⚠️ 币安是配角，博主/读者/用户才是主角。
直接写。严格控制在{length_constraints['target']}字左右（{length_constraints['min']}-{length_constraints['max']}字）。按策略官hook方向即时反应写第一句。"""

    provider = api_config.get("provider", "grok")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints['target'] * 2), 2048)
    print(f"    [P30] max_tokens={max_tokens} (target={length_constraints['target']}字×2)")

    # 重试机制
    max_retries = 2
    for attempt in range(max_retries + 1):
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
            return _post_process(response_text)
        except Exception as e:
            if attempt < max_retries and "Connection" in str(e):
                wait_time = 3 * (attempt + 1)
                print(f"--- [P30] ⚠️ {label} 第{attempt+1}次重试（{wait_time}s后）: {e} ---")
                time.sleep(wait_time)
            else:
                raise


def bullish_take_writer(state: dict) -> dict:
    """
    吹捧模式 Writer - P30 3版本生成
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    web3_knowledge = state.get("web3_knowledge", "")

    mode_config = get_mode_config("bullish_take")
    length_constraints = mode_config.get("length", {"min": 100, "max": 300, "target": 200})

    custom_length = state.get("custom_length", 0)
    if custom_length and custom_length > 0:
        margin = int(custom_length * 0.2)
        length_constraints = {
            "min": max(50, custom_length - margin),
            "max": custom_length + margin,
            "target": custom_length
        }

    # P30: RAG 样本（暂用半佛积极，后续换CZ转发推文样本）
    rag_context = _get_rag_samples()

    shared_context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "length": length_constraints,
        "raw_input": raw_input,
        "strategy_json": strategy_json,
        "web3_knowledge": web3_knowledge,
        "rag_context": rag_context,
        "forbidden_patterns": load_forbidden_patterns(),
    }

    # 从策略官输出提取3个版本方案
    print("--- [P30] 从策略官输出提取吹捧版本方案 ---")
    plans = _extract_plans(strategy_json)
    for i, p in enumerate(plans):
        print(f"  版本{i+1}: {p.get('label','')} | 视角: {p.get('perspective','')} | 公式: {p.get('logic_pattern','')}")

    # 按方案循环生成3个版本
    variants = []
    for i, plan in enumerate(plans):
        try:
            print(f"--- [P30] 写手生成版本 {i+1}/3: {plan.get('label','')} ({plan.get('tone','')}) ---")
            content = _generate_variant(
                raw_input=raw_input,
                plan=plan,
                system_prompt_context=shared_context,
                length_constraints=length_constraints,
                api_config=api_config,
            )
            variants.append({
                "key": f"variant_{i+1}",
                "label": plan.get("label", f"版本{i+1}"),
                "methods": [],
                "instruction": plan.get("story", ""),
                "content": content,
                "char_count": len(content) if content else 0,
            })
        except Exception as e:
            print(f"--- [P30] ❌ 版本 {i+1} 失败: {e} ---")
            variants.append({
                "key": f"variant_{i+1}",
                "label": plan.get("label", f"版本{i+1}"),
                "methods": [],
                "instruction": plan.get("angle", ""),
                "content": f"[生成失败: {e}]",
                "char_count": 0,
            })

    first_content = next((v["content"] for v in variants if v["char_count"] > 0), "")

    return {
        "draft_content": first_content,
        "variants": variants,
    }
