"""
P28: Knowledge Retriever Service — Google Sheets 版
============================
从 Google Sheets `知识库_Web3` Tab 检索与主题相关的 Web3 知识
"""

import re
from typing import Optional
from ..core.config import get_logger

logger = get_logger("knowledge_retriever")


def retrieve_web3_knowledge(
    topic: str, 
    max_results: int = 5,
    min_quality_score: float = 0
) -> str:
    """
    从 Google Sheets 知识库 Tab 检索与主题相关的 Web3 知识
    
    Args:
        topic: 用户输入的主题/关键词
        max_results: 最大返回结果数
        min_quality_score: 最低质量评分阈值
        
    Returns:
        格式化的 Web3 知识上下文字符串
    """
    try:
        from ..services.google_sheets_source import google_sheets_source as gs
        
        if not gs.is_available():
            logger.warning("Google Sheets 不可用，跳过知识检索")
            return ""
        
        # 加载知识库 Tab
        records = gs._load_sheet_data("知识库_Web3")
        
        if not records:
            logger.info("[Knowledge Retriever] 知识库_Web3 无记录")
            return ""
        
        # 提取关键词
        keywords = extract_keywords(topic)
        logger.info(f"[Knowledge Retriever] 检索关键词: {keywords}")
        
        # 过滤和排序
        matched_records = []
        for record in records:
            # Google Sheets 字段直接用中文列名
            content = str(record.get("正文原文", record.get("正文内容", record.get("content", ""))))
            record_topic = str(record.get("赛道分类", record.get("主题", "")))
            title = str(record.get("标题", ""))
            entities = str(record.get("项目/人名/代币", record.get("核心实体", "")))
            record_keywords = str(record.get("关键词", ""))
            
            quality_score = record.get("质量评分", 0)
            if isinstance(quality_score, str):
                try:
                    quality_score = float(quality_score)
                except (ValueError, TypeError):
                    quality_score = 0
            
            if quality_score < min_quality_score:
                continue
            
            # 分层匹配（权重: 实体10 > 关键词5 > 标题2 > 全文1）
            entity_score = calculate_match_score(keywords, entities) * 10
            keyword_score = calculate_match_score(keywords, record_keywords) * 5
            title_score = calculate_match_score(keywords, f"{title} {record_topic}") * 2
            content_score = calculate_match_score(keywords, content)
            total_score = entity_score + keyword_score + title_score + content_score
            
            if total_score > 0:
                matched_records.append({
                    "title": title,
                    "topic": record_topic,
                    "content": content[:1500],
                    "quality_score": quality_score,
                    "match_score": total_score,
                    "entities": entities,
                    "keywords": record_keywords
                })
        
        matched_records.sort(key=lambda x: (x["match_score"], x["quality_score"]), reverse=True)
        top_records = matched_records[:max_results]
        
        if not top_records:
            logger.info(f"[Knowledge Retriever] 未找到与 '{topic}' 相关的知识")
            return ""
        
        # 格式化输出
        output_parts = [f"===== Web3 知识背景 ({len(top_records)} 条相关记录) ====="]
        for i, record in enumerate(top_records, 1):
            output_parts.append(f"""
--- [Web3背景 {i}] {record['title']} ---
主题: {record['topic']}
质量评分: {record['quality_score']:.1f}
内容摘要:
{record['content'][:800]}...
""")
        output_parts.append("=" * 50)
        
        result = "\n".join(output_parts)
        logger.info(f"[Knowledge Retriever] 检索到 {len(top_records)} 条相关知识")
        return result
        
    except Exception as e:
        logger.error(f"[Knowledge Retriever] 检索失败: {e}")
        return ""


def extract_keywords(topic: str) -> list[str]:
    """从主题中提取关键词"""
    stopwords = {"的", "了", "是", "在", "和", "与", "或", "对", "为", "将", "会", "能", "可以", "如何", "什么", "怎么", "分析", "介绍"}
    words = re.split(r'[\s,，。！？、：；""''【】\[\]()（）]+', topic)
    keywords = [w.strip() for w in words if w.strip() and len(w.strip()) >= 2 and w.strip() not in stopwords]
    return keywords


def calculate_match_score(keywords: list[str], text: str) -> int:
    """计算关键词匹配分数"""
    text_lower = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in text_lower)
