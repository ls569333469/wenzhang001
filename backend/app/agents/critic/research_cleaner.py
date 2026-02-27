"""
P31: 投研数据清洗 Critic
在投研模式中，Critic 不做评分打分，而是做数据清洗和分级
"""
import re
import json
from ...core.llm import generate_text
from ...core.prompts import render_modular_prompt
from ...core.mode_configs import get_mode_config


def research_cleaner(draft, mode="project_research", api_config=None,
                     length=None, style=None, custom_prompts=None,
                     strategy_json=""):
    """
    投研模式 Critic — 数据清洗 + 分级

    职责：
    1. 清理 Surf API 输出中的噪音（内部标记、URL、占位符）
    2. 自动判断项目阶段（concept/funded/pre_tge/launched/mature）
    3. 验证数据完整性

    返回格式与 standard_critic 一致：
    {"score": int, "verdict": str, "suggestions": list}
    """
    api_config = api_config or {}

    # 构建清洗 prompt
    try:
        system_prompt = render_modular_prompt("critic/project_research.jinja2", {
            "strategy_json": strategy_json,
        })
    except Exception:
        system_prompt = (
            "你是数据清洗专家。请清理以下投研分析文本：\n"
            "1. 删除所有 URL 链接和内部标记\n"
            "2. 删除'待验证''暂无数据'等占位符\n"
            "3. 判断项目阶段\n"
            "4. 输出清洗后的干净文本"
        )

    user_prompt = f"""请清洗以下投研分析数据，去除噪音和无效信息：

---
{draft}
---

要求：
1. 删除所有 URL、链接引用、内部数据库标记（如 db_internal_xxx）
2. 删除"待验证""暂无数据""未找到"等无内容的占位段落
3. 删除分析方法论描述（如"我通过搜索发现..."）
4. 保留所有有实质内容的数据和结论
5. 直接输出清洗后的完整文本，不要添加任何说明"""

    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None

    try:
        cleaned_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.2,  # 低温度，精确清洗
            system_prompt=system_prompt,
            max_tokens=3000,
        )
    except Exception as e:
        print(f"--- [P31] Cleaner Error: {e}, using regex fallback ---")
        cleaned_text = _regex_fallback_clean(draft)

    return {
        "score": 100,  # 清洗模式始终通过（不打分）
        "verdict": "PASS",
        "suggestions": ["数据清洗完成"],
        "cleaned_draft": cleaned_text,
    }


def _regex_fallback_clean(text: str) -> str:
    """纯正则 fallback 清洗（AI 失败时使用）"""
    # 删除 URL
    text = re.sub(r'https?://\S+', '', text)
    # 删除内部标记
    text = re.sub(r'db_internal_\w+', '', text)
    text = re.sub(r'\[来源[：:]\s*.*?\]', '', text)
    # 删除占位文本
    text = re.sub(r'(?:^|\n).*?(?:待验证|暂无数据|未找到|数据缺失).*?(?:\n|$)', '\n', text)
    # 删除连续空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
