"""
Material Analyzer - AI 预筛选
P23 Phase 1b: 对爬取的素材进行 LLM 评估

功能:
  - 一句话摘要
  - 创作适合度评分 (1-10)
  - 事实类型分类
  - 关键词/实体提取
  - 推荐创作模式
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.llm import generate_text

ANALYZE_SYSTEM_PROMPT = """你是一个 Web3 内容编辑助手。对给定的素材进行快速评估，返回 JSON（不做任何展开分析）。"""

ANALYZE_PROMPT_TEMPLATE = """分析以下 Web3 内容，返回严格 JSON（无其他文字）：

标题: {title}
内容: {content}

返回格式：
{{
  "summary": "一句话核心摘要（30字内）",
  "quality_score": 创作适合度1-10,
  "score_reason": "一句话评分理由",
  "fact_type": "硬数据/深度分析/观点评论/快讯资讯",
  "keywords": ["关键词1", "关键词2"],
  "entities": ["项目/代币/人名"]
}}

评分标准：
- 8-10：有具体数据+争议性/情绪点
- 5-7：有信息量但角度普通
- 1-4：纯公告/无新意/过于细碎"""


def calc_timeliness(published_at: str) -> str:
    """时效性计算 — 零 LLM 开销"""
    try:
        if not published_at:
            return "unknown"
        pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        delta = datetime.now() - pub_time.replace(tzinfo=None)
        if delta < timedelta(hours=24):
            return "fresh"
        elif delta < timedelta(days=3):
            return "recent"
        else:
            return "stale"
    except Exception:
        return "unknown"


def suggest_modes(content_type: str, content: str) -> List[str]:
    """推荐创作模式 — 基于规则，不消耗 LLM"""
    text_len = len(content)
    if content_type == "快讯" or text_len < 80:
        return ["short_article"]
    elif text_len < 250:
        return ["mid_article", "short_article"]
    else:
        return ["mid_article", "long_article"]


def content_fingerprint(content: str) -> str:
    """MD5 内容指纹"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()[:16]


def analyze_material(material: Dict, api_config: dict = None) -> Dict:
    """
    对单条素材进行 AI 预筛选分析

    Args:
        material: 爬虫返回的素材 dict
        api_config: 可选 LLM API 配置

    Returns:
        enriched material dict with analysis fields
    """
    title = material.get("title", "")
    content = material.get("content", "")[:2000]  # Cap for token cost
    content_type = material.get("content_type", "")

    # AI analysis
    analysis = _call_llm_analysis(title, content, api_config)

    # Merge results
    result = {
        **material,
        "summary": analysis.get("summary", title[:30]),
        "quality_score": analysis.get("quality_score", 5),
        "score_reason": analysis.get("score_reason", ""),
        "fact_type": analysis.get("fact_type", "快讯资讯"),
        "keywords": analysis.get("keywords", []),
        "entities": analysis.get("entities", []),
        "suggested_modes": suggest_modes(content_type, content),
        "timeliness": calc_timeliness(material.get("published_at", "")),
        "fingerprint": content_fingerprint(content),
        "status": "未使用",
    }

    return result


def analyze_batch(materials: List[Dict], api_config: dict = None) -> List[Dict]:
    """批量分析素材"""
    results = []
    total = len(materials)

    for i, mat in enumerate(materials):
        print(f"[Analyzer] 分析 {i + 1}/{total}: {mat.get('title', '')[:40]}...")
        try:
            result = analyze_material(mat, api_config)
            results.append(result)
        except Exception as e:
            print(f"[Analyzer] 分析失败: {e}")
            # Fallback: add without AI analysis
            mat["summary"] = mat.get("title", "")[:30]
            mat["quality_score"] = 5
            mat["score_reason"] = "分析失败"
            mat["fact_type"] = "快讯资讯"
            mat["keywords"] = []
            mat["entities"] = []
            mat["suggested_modes"] = suggest_modes(
                mat.get("content_type", ""), mat.get("content", "")
            )
            mat["timeliness"] = calc_timeliness(mat.get("published_at", ""))
            mat["fingerprint"] = content_fingerprint(mat.get("content", ""))
            mat["status"] = "未使用"
            results.append(mat)

    print(f"[Analyzer] 完成: {len(results)}/{total} 条")
    return results


def _call_llm_analysis(title: str, content: str, api_config: dict = None) -> Dict:
    """调用 LLM 进行内容分析"""
    prompt = ANALYZE_PROMPT_TEMPLATE.format(title=title, content=content)

    kwargs = {
        "prompt": prompt,
        "system_prompt": ANALYZE_SYSTEM_PROMPT,
        "temperature": 0.3,
        "max_tokens": 512,
    }

    # Use provided api_config or defaults
    if api_config:
        kwargs["provider"] = api_config.get("provider", "volcengine")
        kwargs["model_id"] = api_config.get("model", None)
        kwargs["api_key"] = api_config.get("api_key", None)

    try:
        raw = generate_text(**kwargs)
        if not raw:
            return {}

        # Extract JSON from response
        text = raw.strip()
        # Handle markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        return json.loads(text)

    except json.JSONDecodeError as e:
        print(f"[Analyzer] JSON parse error: {e}")
        return {}
    except Exception as e:
        print(f"[Analyzer] LLM error: {e}")
        return {}
