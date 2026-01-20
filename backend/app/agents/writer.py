from datetime import datetime
import json
import json
from ..core.llm import generate_text
from ..core.prompts import render_prompt

# 各模式的风格模板
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
    "diary": {
        "name": "小红书赚钱博主体",
        "style": """
        - 标题用数字+结果：如"3个月从0到100万"
        - 开头要humble brag，看似谦虚实则炫耀
        - 内容要有干货感，列点清晰
        - 穿插个人经历增加可信度
        - 多用emoji装饰🔥💰✨
        - 结尾暗示还有更多干货，引导关注
        - 营造"普通人也能做到"的感觉
        """,
        "tone": "亲切、励志、干货、接地气"
    },
    "insider": {
        "name": "金融内幕消息体",
        "style": """
        - 开头要有独家信息感或内部消息暗示
        - 使用专业术语增加可信度
        - 分析要有逻辑链条，从数据到结论
        - 适当使用Web3/加密货币黑话
        - 保持神秘感，不要说得太满
        - 结尾给出明确但模糊的操作建议
        - 制造 FOMO 情绪
        """,
        "tone": "专业、神秘、内部人士视角、Alpha信号"
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
    },
    "xinshixiang": {
        "name": "新世相体",
        "style": """
        - 场景描写细腻，有画面感
        - 故事叙述温暖，有文学感
        - 情感递进，共鸣升华
        - 多用对话体，增强代入感
        - 留白处理，引人深思
        """,
        "tone": "温柔、感性、共鸣、治愈"
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
    mode = state["mode"]
    narrative_type = state.get("narrative_type", "project_review")
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    
    # 获取提供商配置
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    print(f">>> [Writer Debug] Config: provider={provider}, model={model_id}, key_exists={bool(api_key)}")
    
    # 从 MODE_TEMPLATES 获取风格指南
    template = MODE_TEMPLATES.get(mode, MODE_TEMPLATES["mimeng"])
    
    # [P8] Lark Integration: 获取动态 Few-Shot 样本
    from ..services.sync_service import sync_service
    # 尝试匹配 emotion, 如果 state 中没有, 暂时为 None
    emotion = state.get("emotion") 
    print(f">>> [Writer Debug] Fetching style samples for mode={mode}, emotion={emotion}")
    try:
        samples = sync_service.get_samples(style=mode, emotion=emotion, count=3)
        print(f">>> [Writer Debug] Samples fetched: {len(samples)}")
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
        "template_name": template['name'],
        "narrative_type": narrative_type,
        "narrative_desc": narrative_desc,
        "must_mention_str": must_mention_str,
        "key_data_str": key_data_str,
        "rag_context": rag_context
    }
    print(">>> [Writer Debug] Rendering prompt")
    system_prompt = render_prompt("writer", context)

    user_prompt = f"""Strategist's Plan:
{strategy_json}

Source Material:
{raw_input}

Please write the article now."""

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
