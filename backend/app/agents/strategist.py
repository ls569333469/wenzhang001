from datetime import datetime
import json
from ..core.llm import generate_text
from ..core.prompts import render_prompt
from ..core.config import get_feature_flag, get_logger
from ..core.forbidden_patterns import load_forbidden_patterns  # P21
from ..services.knowledge_retriever import retrieve_web3_knowledge

logger = get_logger("strategist")


def _format_sample(index: int, sample: dict) -> str:
    """
    P28: 丰富样本格式 — 传入 content + 情绪 + 逻辑公式
    A/B 测试验证: 审核分从 75 提升到 90
    """
    parts = [f"--- 样本 {index+1} ---"]
    parts.append(sample.get("content", "")[:2000])
    
    # 情绪效价（如果非空）
    ev = sample.get("emotional_valence", "")
    if ev:
        parts.append(f"情绪: {ev}")
    
    # 逻辑公式（如果非空）
    lp = sample.get("logic_pattern", "")
    if lp:
        parts.append(f"逻辑公式: {lp}")
    
    return "\n".join(parts)


def build_strategist_context(state: dict) -> dict:
    """
    Step 1.1: Build Context
    """
    from ..services.sample_service import sample_service  # 使用统一的样本服务
    
    mode = state["mode"]
    style = state.get("style", mode)  # P10: style 参数
    narrative_type = state.get("narrative_type", "project_review")
    
    # P29 B方案: 所有模式统一使用 random 样本
    samples = sample_service.get_samples(style=style, count=3)
    if samples:
        rag_context = "\n\n".join([
            _format_sample(i, s) for i, s in enumerate(samples)
        ])
    else:
        rag_context = f"[未获取到 {style} 风格样本，请检查数据源配置]"
    
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Narrative Type Definitions (P18: 移除 market_news, opinion)
    narrative_descriptions = {
        "project_review": "Deep dive analysis, technical breakdown, pros/cons.",
        "tutorial": "Step-by-step guide, educational, clear instructions.",
    }
    narrative_desc = narrative_descriptions.get(narrative_type, "Standard Review")
    
    # P10: 仅保留有实际样本数据的风格
    mode_descriptions = {
        "mimeng": "咪蒙体 - 制造焦虑、阶级冲突、情绪爆点",
        "banfo": "半佛仙人体 - 反常识观点、案例轰炸、硬核科普"
    }
    
    # P30: 吹捧模式使用半佛积极样本（后续换刘润）
    STYLE_OVERRIDE = {"bullish_take": "banfo"}
    if mode in STYLE_OVERRIDE:
        style = STYLE_OVERRIDE[mode]
    
    # 安全检查：未知风格 fallback 到 mimeng
    VALID_STYLES = {"mimeng", "banfo"}
    if style not in VALID_STYLES:
        logger.warning(f"Unknown style '{style}', fallback to mimeng")
        style = "mimeng"

    # [Feature Flag] Knowledge_Repo 集成
    web3_knowledge = ""
    if get_feature_flag("use_knowledge_repo"):
        topic = state.get("raw_input", "")
        logger.info(f"[Strategist] Knowledge_Repo 已启用，检索主题: {topic[:50]}...")
        web3_knowledge = retrieve_web3_knowledge(topic)
        if web3_knowledge:
            logger.info(f"[Strategist] 检索到 Web3 知识背景")
        else:
            logger.info(f"[Strategist] 未检索到相关 Web3 知识")
    
    context = {
        "current_time_str": current_time_str,
        "narrative_type": narrative_type,
        "mode": mode,
        "mode_description": mode_descriptions.get(mode, mode),
        "narrative_desc": narrative_desc,
        "rag_context": rag_context,
        "web3_knowledge": web3_knowledge,  # 传递给 Writer
        "retention_level": state.get("retention_level", 3),  # P10: 内容保留度
        "forbidden_patterns": load_forbidden_patterns(),  # P21: 禁用词库
    }
    
    # P29: 注入公式菜单供策略师选择（short_article + bullish_take）
    if state.get("mode") in ("short_article", "bullish_take"):
        pattern_menu = sample_service.get_pattern_menu(style=style)
        context["pattern_menu"] = pattern_menu
        logger.info(f"[P29] Injected pattern_menu: {len(pattern_menu)} patterns for {style}")
    
    return context

def build_strategist_prompt(context: dict, state: dict) -> tuple[str, str]:
    """
    Step 1.2: Build Prompts
    Returns (system_prompt, user_prompt)
    """
    import random
    from jinja2 import Environment

    raw_input = state["raw_input"]
    references = state.get("references", [])
    
    combined_input = f"===== CORE INSTRUCTION / SOURCE =====\n{raw_input}\n\n"
    
    # P23: Append material context if provided (from 素材中心 "去创作")
    material_context = state.get("material_context", "")
    if material_context:
        combined_input += f"===== REFERENCE MATERIAL (素材原文) =====\n{material_context[:3000]}\n\n"

    if references:
        combined_input += f"===== EXTRA REFERENCES ({len(references)} ITEMS) =====\n"
        for i, ref in enumerate(references, 1):
            combined_input += f"--- [Ref {i}] ---\n{ref}\n\n"
            
    combined_input += "================================================="
    
    # Diversity injection
    random_seed = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    # P15: Custom Prompt Support
    custom_prompts = state.get("custom_prompts", {})
    if custom_prompts.get("strategist"):
        # Use custom prompt as template, inject combined_input as raw_input
        env = Environment()
        # Render custom prompt with context AND raw_input (which now contains all info)
        system_prompt = env.from_string(custom_prompts["strategist"]).render(
            **context,
            raw_input=combined_input
        )
        # Minimize user prompt as info is already in system prompt
        user_prompt = f"[Session: {random_seed}]\nPlease analyze based on the instructions above."
    else:
        # P25: 短篇使用专用策略官模板
        mode = state.get("mode", "mid_article")
        if mode == "short_article":
            # 短篇专用模板：素材分析 + 六法框架 + 12种写法
            context["raw_input"] = combined_input
            system_prompt = render_prompt("strategist/short_article", context)
            user_prompt = f"[Session: {random_seed}]\n请分析以上素材，输出3个版本方案的JSON。"
        elif mode == "bullish_take":
            # P30: 吹捧专用模板：5种切入视角 + story/detail
            context["raw_input"] = combined_input
            system_prompt = render_prompt("strategist/bullish_take", context)
            user_prompt = f"[Session: {random_seed}]\n请分析以上素材，选择最合适的切入视角，输出3个方案的JSON。"
        else:
            # Default Logic
            system_prompt = render_prompt("strategist", context)
            user_prompt = f"""{combined_input}

[Session: {random_seed}]
Please analyze the above materials (Core Instruction + References) and generate a content strategy in JSON format.
If references are provided, identify common themes or contrast them with the core instruction.

CRITICAL DIVERSITY REQUIREMENTS:
1. Generate 3-5 COMPLETELY UNIQUE title candidates with DIFFERENT angles
2. Each title MUST use a DIFFERENT formula combination (数字法则, 悬念法则, etc.)
3. Avoid ANY repetition from previous generations
4. Use the ACTUAL numbers and entities from the source material
5. Create titles that a reader would see as 4 DISTINCT approaches to the same topic"""


    return system_prompt, user_prompt

def execute_strategist_analysis(user_prompt: str, system_prompt: str, api_config: dict) -> str:
    """
    Step 1.3: Execute LLM Analysis
    """
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.85,  # Higher temp for more diverse title generation
            system_prompt=system_prompt
        )
        
        # 清理 JSON 格式
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        return text
    except Exception as e:
        return json.dumps({
            "error": str(e), 
            "info_anchors": {"must_mention": [], "key_data": [], "can_extend": []},
            "fallback_plan": "Generate generic content based on mode."
        })

def strategist_agent(state: dict) -> dict:
    """
    Step 1: Strategist Agent
    Generates a content strategy plan based on the input and context.
    Returns: {"plan": str, "web3_knowledge": str}
    """
    context = build_strategist_context(state)
    system_prompt, user_prompt = build_strategist_prompt(context, state)
    api_config = state.get("api_config", {})
    
    plan_text = execute_strategist_analysis(user_prompt, system_prompt, api_config)
    
    # P20: 诊断日志 - 检查 context_card 是否生成
    try:
        plan_obj = json.loads(plan_text)
        if "context_card" in plan_obj:
            logger.info(f"[P20] ✅ context_card 已生成: {plan_obj['context_card']}")
        else:
            logger.warning("[P20] ⚠️ Strategist 未返回 context_card 字段")
    except:
        logger.warning("[P20] ⚠️ 无法解析 Strategist JSON 响应")
    
    return {
        "plan": plan_text,
        "web3_knowledge": context.get("web3_knowledge", "")
    }
