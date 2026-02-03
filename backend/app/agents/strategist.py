from datetime import datetime
import json
from ..core.llm import generate_text
from ..core.prompts import render_prompt
from ..core.config import get_feature_flag, get_logger
from ..services.knowledge_retriever import retrieve_web3_knowledge

logger = get_logger("strategist")



def build_strategist_context(state: dict) -> dict:
    """
    Step 1.1: Build Context
    """
    from ..services.sample_service import sample_service  # 使用统一的样本服务
    
    mode = state["mode"]
    style = state.get("style", mode)  # P10: style 参数
    narrative_type = state.get("narrative_type", "project_review")
    
    # 使用 sample_service 获取样本 (支持 Lark/Google Sheets A/B 测试)
    samples = sample_service.get_samples(style=style, count=3)
    if samples:
        rag_context = "\n\n".join([
            f"--- 样本 {i+1} ---\n{s.get('content', '')[:2000]}" 
            for i, s in enumerate(samples)
        ])
    else:
        rag_context = f"[未获取到 {style} 风格样本，请检查数据源配置]"
    
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Narrative Type Definitions
    narrative_descriptions = {
        "project_review": "Deep dive analysis, technical breakdown, pros/cons.",
        "market_news": "Breaking news style, urgent, market impact focus.",
        "tutorial": "Step-by-step guide, educational, clear instructions.",
        "opinion": "Strong personal stance, argumentative, thought leadership.",
        "micro_novel": "Fictionalized narrative, storytelling, dramatic arc."
    }
    narrative_desc = narrative_descriptions.get(narrative_type, "Standard Review")
    
    # P10: 仅保留有实际样本数据的风格
    mode_descriptions = {
        "mimeng": "咪蒙体 - 制造焦虑、阶级冲突、情绪爆点",
        "banfo": "半佛仙人体 - 反常识观点、案例轰炸、硬核科普"
    }
    
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
        "retention_level": state.get("retention_level", 3)  # P10: 内容保留度
    }
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
    
    return {
        "plan": plan_text,
        "web3_knowledge": context.get("web3_knowledge", "")
    }
