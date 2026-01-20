from datetime import datetime
import json
import random
from pathlib import Path
from ..core.llm import generate_text
from ..core.prompts import render_prompt

# 模式到目录的映射
MODE_TO_DIR = {
    "mimeng": "mimeng",
    "diary": "xiaohongshu",
    "insider": "insider",
    "banfo": "banfo",
    "xinshixiang": "xinshixiang",
    "shijuezhi": "shijuezhi",
    "lianbushou": "lianbushou",
    "lingongzi": "lingongzi",
    "fengqiongzi": "fengqiongzi",
    "chengshian": "chengshian"
}

def load_style_samples(mode: str, max_samples: int = 3, max_chars_per_sample: int = 2000) -> str:
    """
    从对应风格目录加载随机样本文档。
    """
    current_dir = Path(__file__).parent.parent.parent  # backend/
    data_dir = current_dir / "data" / MODE_TO_DIR.get(mode, "mimeng")
    
    if not data_dir.exists():
        return f"[风格库目录不存在: {data_dir}]"
    
    # 扫描目录下所有 .txt 和 .md 文件（排除 README）
    style_files = [f for f in (list(data_dir.glob("*.txt")) + list(data_dir.glob("*.md"))) 
                   if f.name.lower() != "readme.md"]
    
    if not style_files:
        return f"[风格库为空，请在 {data_dir} 目录下添加 .txt 或 .md 文件]"
    
    selected_files = random.sample(style_files, min(max_samples, len(style_files)))
    
    samples = []
    for i, file_path in enumerate(selected_files, 1):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) > max_chars_per_sample:
                    content = content[:max_chars_per_sample] + "...[截断]"
                samples.append(f"--- 样本 {i}: {file_path.name} ---\n{content}")
        except Exception as e:
            samples.append(f"--- 样本 {i}: {file_path.name} (读取失败: {e}) ---")
    
    return "\n\n".join(samples)


def build_strategist_context(state: dict) -> dict:
    """
    Step 1.1: Build Context
    """
    mode = state["mode"]
    narrative_type = state.get("narrative_type", "project_review")
    
    rag_context = load_style_samples(mode)
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
    
    mode_descriptions = {
        "mimeng": "咪蒙体 - 制造焦虑、阶级冲突、情绪爆点",
        "diary": "小红书赚钱博主体 - 个人经历、干货分享、humble brag",
        "insider": "金融内幕消息体 - Alpha信号、专业术语、FOMO情绪",
        "banfo": "半佛仙人体 - 反常识观点、案例轰炸、硬核科普",
        "xinshixiang": "新世相体 - 情感叙事、UGC故事、共鸣升华",
        "shijuezhi": "视觉志体 - 图文并茂、短句金句、美学呈现",
        "lianbushou": "链捕手体 - Web3深度报道、专业分析",
        "lingongzi": "临公子体 - 投资干货、实用建议",
        "fengqiongzi": "风茕子体 - 人性剖析、职场洞察",
        "chengshian": "程十安体 - 生活干货、通俗易懂"
    }

    context = {
        "current_time_str": current_time_str,
        "narrative_type": narrative_type,
        "mode": mode,
        "mode_description": mode_descriptions.get(mode, mode),
        "narrative_desc": narrative_desc,
        "rag_context": rag_context
    }
    return context

def build_strategist_prompt(context: dict, state: dict) -> tuple[str, str]:
    """
    Step 1.2: Build Prompts
    Returns (system_prompt, user_prompt)
    """
    system_prompt = render_prompt("strategist", context)

    raw_input = state["raw_input"]
    references = state.get("references", [])
    
    combined_input = f"===== CORE INSTRUCTION / SOURCE =====\n{raw_input}\n\n"
    
    if references:
        combined_input += f"===== EXTRA REFERENCES ({len(references)} ITEMS) =====\n"
        for i, ref in enumerate(references, 1):
            combined_input += f"--- [Ref {i}] ---\n{ref}\n\n"
            
    combined_input += "================================================="

    user_prompt = f"""{combined_input}

Please analyze the above materials (Core Instruction + References) and generate a content strategy in JSON format.
If references are provided, identify common themes or contrast them with the core instruction."""

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
            temperature=0.2,
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
    Legacy Wrapper: Maintains backward compatibility for graph execution.
    """
    context = build_strategist_context(state)
    system_prompt, user_prompt = build_strategist_prompt(context, state)
    api_config = state.get("api_config", {})
    return execute_strategist_analysis(user_prompt, system_prompt, api_config)
