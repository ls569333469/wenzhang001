"""
短篇 Writer - P23v2 六法重构 + 动态方法选择 + 多版本输出
字数: 200-500字 (适合X/Twitter正常发文)
先分析素材特征，再定制3种最佳重构方法，最后生成3个版本
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from app.services.sample_service import sample_service
import re
import json

HARD_CONSTRAINTS = "\n\n【字数：200-500字 | 语言：中文】"

# 六法框架定义
SIX_METHODS = {
    "结构重构": "改变叙事顺序（结果先行/倒叙/从细节切入），重新分配主次关系",
    "视角转换": "换叙述主体（受影响方/散户/行业/历史对比），换时空维度",
    "内容重构": "具体→抽象（提炼规律）或抽象→具体（画面感），补充推断",
    "逻辑重组": "正向→反向论证，线性→发散思维，因果关系重排",
    "形式转换": "陈述→设问/反问，直述→比喻，说理→画面感/对话体",
    "语言优化": "书面→口语化，严谨→轻松，长句→短句，加语气词",
}


def _analyze_material(raw_input: str, api_config: dict) -> list:
    """
    P23v2: 轻量分析步骤 - 分析素材特征，推荐3种最佳方法组合
    返回: [{"label": "版本名", "methods": ["方法1", "方法2"], "instruction": "具体指令"}, ...]
    """
    analysis_prompt = f"""你是一个内容策略分析师。现在有一条加密货币素材需要改写成3个不同版本的原创短评。

素材：
{raw_input}

六种可用的重构方法：
1. 结构重构：{SIX_METHODS["结构重构"]}
2. 视角转换：{SIX_METHODS["视角转换"]}
3. 内容重构：{SIX_METHODS["内容重构"]}
4. 逻辑重组：{SIX_METHODS["逻辑重组"]}
5. 形式转换：{SIX_METHODS["形式转换"]}
6. 语言优化：{SIX_METHODS["语言优化"]}

请分析这条素材的特征，然后为它定制3个版本的重构方案。每个版本选2-3种方法组合。
3个版本之间的风格和角度要有明显差异。

用JSON格式输出，不要输出其他内容：
[
  {{"label": "版本名(3-5字)", "methods": ["方法1", "方法2"], "instruction": "一句话说明这个版本具体怎么写"}},
  {{"label": "版本名", "methods": ["方法1", "方法2"], "instruction": "一句话说明"}},
  {{"label": "版本名", "methods": ["方法1", "方法2", "方法3"], "instruction": "一句话说明"}}
]"""

    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None

    try:
        result = generate_text(
            prompt=analysis_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.3,  # 低温度保证稳定JSON输出
            system_prompt="你是内容策略分析师，只输出JSON，不要额外解释。",
            max_tokens=500,
        )
        # 解析JSON
        result = result.strip()
        # 处理可能的markdown代码块
        if result.startswith("```"):
            result = re.sub(r'^```\w*\n?', '', result)
            result = re.sub(r'\n?```$', '', result)
            result = result.strip()
        plans = json.loads(result)
        if isinstance(plans, list) and len(plans) >= 3:
            return plans[:3]
    except Exception as e:
        print(f"--- [P23v2] 分析失败({e})，使用默认方案 ---")

    # 兜底：返回默认方案
    return [
        {"label": "换个角度聊", "methods": ["视角转换", "结构重构"], "instruction": "原文站机构/专家角度，你站散户/普通人角度，吐槽或感慨"},
        {"label": "说透本质", "methods": ["内容重构", "逻辑重组"], "instruction": "别罗列事实，把这事最讽刺/最荒谬的点挖出来，让人恍然大悟"},
        {"label": "群里聊天", "methods": ["语言优化", "形式转换"], "instruction": "就像在群里看到消息第一反应蹦出来说的话，短句连射"},
    ]


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
    """根据分析结果生成单个版本"""
    methods = plan.get("methods", [])
    instruction = plan.get("instruction", "")
    label = plan.get("label", "")

    # 构建方法说明
    method_details = []
    for m in methods:
        if m in SIX_METHODS:
            method_details.append(f"- **{m}**：{SIX_METHODS[m]}")

    methods_text = "\n".join(method_details) if method_details else "- 自由发挥"

    # 构建动态 system prompt（不用模板，直接拼接）
    ctx = {**system_prompt_context, "variant_method": "dynamic"}
    if custom_prompts and custom_prompts.get("writer"):
        from jinja2 import Environment
        env = Environment()
        system_prompt = env.from_string(custom_prompts["writer"]).render(**ctx)
        system_prompt += HARD_CONSTRAINTS
    else:
        system_prompt = render_modular_prompt("writer/short_article.jinja2", ctx)

    # user prompt — 极简指令，不做学术分析
    user_prompt = f"""素材：
{raw_input}

你要写的版本：{label}
风格指令：{instruction}

直接写。{length_constraints['target']}字左右。第一句就带感情，别铺垫。"""

    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints.get("max", 500) * 1.5), 2048)

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


def short_article_writer(state: dict) -> dict:
    """
    短篇 Writer - P23v2 动态方法选择 + 多版本输出
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    style = state.get("style", "mimeng")

    mode_config = get_mode_config("short_article")
    length_constraints = mode_config.get("length", {"min": 200, "max": 500, "target": 350})

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

    # P23v2 Step 1: 分析素材，动态推荐3种方法
    print("--- [P23v2] Step 1: 分析素材特征 ---")
    plans = _analyze_material(raw_input, api_config)
    for i, p in enumerate(plans):
        print(f"  版本{i+1}: {p['label']} | 方法: {', '.join(p.get('methods',[]))} | {p.get('instruction','')}")

    # P23v2 Step 2: 按推荐方法生成3个版本
    variants = []
    for i, plan in enumerate(plans):
        try:
            print(f"--- [P23v2] Step 2: 生成版本 {i+1}/3: {plan['label']} ---")
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
            print(f"--- [P23v2] ❌ 版本 {i+1} 失败: {e} ---")
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
