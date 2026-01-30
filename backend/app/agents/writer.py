from datetime import datetime
import json
import json
from ..core.llm import generate_text
from ..core.prompts import render_prompt

# 各模式的风格模板 (P10: 仅保留有数据的风格)
MODE_TEMPLATES = {
    "mimeng": {
        "name": "咪蒙体",
        "style": """
        - 标题必须戳中痛点，制造焦虑或共鸣
        - 开头必须讲一个引人入胜的故事或案例
        - 使用大量短句，每句话单独成段
        - 多用感叹号和问号制造情绪张力
        - 金句要多，要有转发冲动
        - 结尾要有强烈的情绪升华或行动号召
        - 禁用词：delve, tapestry, landscape, crucial, testament
        """,
        "tone": "激进、焦虑、戳心、制造冲突"
    },
    "banfo": {
        "name": "半佛仙人体",
        "style": """
        - 抛出反常识观点吸引注意
        - 案例轰炸，用大量例子支撑论点
        - 口语化表达，多用"其实""说白了"
        - 段子穿插，保持幽默感
        - 逻辑链条清晰，让人恍然大悟
        - 商业本质拆解
        """,
        "tone": "犀利、幽默、理性、恍然大悟"
    }
}



def writer_agent(state: dict) -> dict:
    """
    Step 2: Writer
    Generates the first draft based on the Strategist's plan.
    Uses dynamic configuration from state.
    """
    print(">>> [Writer Debug] writer_agent started")
    raw_input = state["raw_input"]
    mode = state.get("mode", "deep_analysis")  # 创作模式 (控制结构)
    narrative_type = state.get("narrative_type", "project_review")
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    
    # P10: 获取 style 参数，用于风格选择
    style = state.get("style", "auto")
    
    # P10: 如果 style="auto"，尝试使用 Strategist 推荐的 style，否则默认 mimeng
    if style == "auto":
        recommended_style = state.get("recommended_style")
        if recommended_style and recommended_style in MODE_TEMPLATES:
            style = recommended_style
            print(f">>> [Writer Debug] Using recommended style: {style}")
        else:
            style = "mimeng"  # 默认 fallback
            print(f">>> [Writer Debug] No recommended style, using default: {style}")
    
    # P10: 获取 length 参数并计算字数约束
    length = state.get("length", "medium")
    from ..graph import calculate_length
    length_constraints = calculate_length(length)
    
    print(f">>> [Writer Debug] Final style: {style}, mode: {mode}, length: {length} ({length_constraints})")
    
    # 获取提供商配置
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    print(f">>> [Writer Debug] Config: provider={provider}, model={model_id}, key_exists={bool(api_key)}")
    
    # P10: 从 MODE_TEMPLATES 获取风格指南 (基于 style 而非 mode)
    template = MODE_TEMPLATES.get(style, MODE_TEMPLATES["mimeng"])
    
    # [P8] Lark Integration: 获取动态 Few-Shot 样本 (基于 style)
    # [P10.6] A/B Test: 支持 Google Sheets 和 Lark 双数据源
    from ..services.sample_service import sample_service
    # 尝试匹配 emotion, 如果 state 中没有, 暂时为 None
    emotion = state.get("emotion") 
    print(f">>> [Writer Debug] Fetching style samples for style={style}, emotion={emotion}")
    try:
        samples = sample_service.get_samples(style=style, emotion=emotion, count=3)
        print(f">>> [Writer Debug] Samples fetched: {len(samples)}")
        
        # P10: Fallback 如果获取不到样本
        if not samples and style != "mimeng":
            print(f">>> [Writer Debug] No samples for {style}, falling back to mimeng")
            samples = sample_service.get_samples(style="mimeng", emotion=emotion, count=3)
    except Exception as e:
        print(f">>> [Writer Debug] Error fetching samples: {e}")
        samples = []
    
    samples_text = ""
    if samples:
        samples_text = "\n\n=== 🌟 FEW-SHOT EXAMPLES (LEARN FROM THESE) ===\n"
        for i, s in enumerate(samples, 1):
            sample_content = s['content']
            # P12: Include logic_pattern for enhanced style learning
            logic_pattern = s.get('logic_pattern', '')
            snippet_type = s.get('snippet_type', '')
            # 截断过长样本以节省 token
            if len(sample_content) > 500:
                sample_content = sample_content[:500] + "..."
            samples_text += f"\n--- Example {i} ---\n"
            if logic_pattern:
                samples_text += f"[逻辑公式: {logic_pattern}]\n"
            if snippet_type:
                samples_text += f"[类型: {snippet_type}]\n"
            samples_text += f"{sample_content}\n"
    else:
        # Fallback hint
        samples_text = "\n(No specific samples found in Lark Library, follow Style Guidelines strictly)"

    rag_context = f"Style Name: {template['name']}\nStyle Guidelines: {template['style']}\nTone: {template['tone']}\n{samples_text}"
    
    # 解析策略计划中的信息锚点
    info_anchors = {"must_mention": [], "key_data": [], "can_extend": []}
    try:
        plan_data = json.loads(strategy_json)
        if "info_anchors" in plan_data:
            info_anchors = plan_data["info_anchors"]
    except:
        pass
    
    must_mention_str = "、".join(info_anchors.get("must_mention", [])) or "（未提取到关键实体）"
    key_data_str = "、".join(info_anchors.get("key_data", [])) or "（未发现关键数据）"
    
    # Narrative Type Definitions
    narrative_descriptions = {
        "project_review": "Deep dive analysis, technical breakdown, pros/cons.",
        "market_news": "Breaking news style, urgent, market impact focus.",
        "tutorial": "Step-by-step guide, educational, clear instructions.",
        "opinion": "Strong personal stance, argumentative, thought leadership.",
        "micro_novel": "Fictionalized narrative, storytelling, dramatic arc."
    }
    narrative_desc = narrative_descriptions.get(narrative_type, "Standard Review")

    context = {
        "mode": mode,
        "style": style,  # P10
        "template_name": template['name'],
        "narrative_type": narrative_type,
        "narrative_desc": narrative_desc,
        "must_mention_str": must_mention_str,
        "key_data_str": key_data_str,
        "rag_context": rag_context,
        "length_constraints": length_constraints,  # P10
        "retention_level": state.get("retention_level", 3)  # P10
    }
    print(">>> [Writer Debug] Rendering prompt")
    system_prompt = render_prompt("writer", context)

    # [P12] Inject Web3 Knowledge
    web3_knowledge = state.get("web3_knowledge", "")
    knowledge_section = ""
    if web3_knowledge:
        knowledge_section = f"\n\n{web3_knowledge}\n"

    user_prompt = f"""策略规划：
{strategy_json}

原始素材：
{raw_input}{knowledge_section}

请现在开始撰写文章。【重要：必须使用中文撰写！】"""

    print(">>> [Writer Debug] Calling generate_text...")
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.65,
            system_prompt=system_prompt
        )
        print(f">>> [Writer Debug] Success! Response length: {len(response_text)}")
        return {"draft_content": response_text}
    except Exception as e:
        print(f">>> [Writer Debug] FAILED: {str(e)}")
        return {"error": f"Error generating content: {str(e)}"}
