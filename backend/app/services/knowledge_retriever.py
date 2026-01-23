"""
Knowledge Retriever Service
============================
从 Knowledge_Repo (Lark Bitable) 检索与主题相关的 Web3 知识
"""

import os
import re
from typing import Optional
from ..core.lark_client import LarkClient
from ..core.config import get_logger

logger = get_logger("knowledge_retriever")

# Knowledge_Repo 表 ID
KNOWLEDGE_TABLE_ID = os.getenv("LARK_KNOWLEDGE_TABLE_ID", "")


def retrieve_web3_knowledge(
    topic: str, 
    max_results: int = 5,
    min_quality_score: float = 5.0
) -> str:
    """
    从 Knowledge_Repo 检索与主题相关的 Web3 知识
    
    Args:
        topic: 用户输入的主题/关键词
        max_results: 最大返回结果数
        min_quality_score: 最低质量评分阈值
        
    Returns:
        格式化的 Web3 知识上下文字符串
    """
    if not KNOWLEDGE_TABLE_ID:
        logger.warning("LARK_KNOWLEDGE_TABLE_ID 未配置，跳过知识检索")
        return ""
    
    try:
        client = LarkClient()
        app_token = os.getenv("LARK_APP_TOKEN", "")
        
        if not app_token:
            logger.warning("LARK_APP_TOKEN 未配置，跳过知识检索")
            return ""
        
        # 提取关键词用于检索
        keywords = extract_keywords(topic)
        logger.info(f"[Knowledge Retriever] 检索关键词: {keywords}")
        
        # 获取所有记录
        records = client.list_records(app_token, KNOWLEDGE_TABLE_ID)
        
        if not records:
            logger.info("[Knowledge Retriever] Knowledge_Repo 无记录")
            return ""
        
        # 过滤和排序
        matched_records = []
        for record in records:
            fields = record.get("fields", {})
            
            # 获取字段值
            content = get_text_value(fields.get("正文内容", ""))
            record_topic = get_text_value(fields.get("主题", ""))
            title = get_text_value(fields.get("标题", ""))
            quality_score = fields.get("质量评分", 0)
            
            # 确保质量评分是数字
            if isinstance(quality_score, str):
                try:
                    quality_score = float(quality_score)
                except:
                    quality_score = 0
            
            # 质量阈值过滤
            if quality_score < min_quality_score:
                continue
            
            # 关键词匹配
            match_score = calculate_match_score(
                keywords, 
                f"{title} {record_topic} {content}"
            )
            
            if match_score > 0:
                matched_records.append({
                    "title": title,
                    "topic": record_topic,
                    "content": content[:1500],  # 限制长度
                    "quality_score": quality_score,
                    "match_score": match_score
                })
        
        # 按匹配度和质量评分排序
        matched_records.sort(
            key=lambda x: (x["match_score"], x["quality_score"]), 
            reverse=True
        )
        
        # 取前 N 条
        top_records = matched_records[:max_results]
        
        if not top_records:
            logger.info(f"[Knowledge Retriever] 未找到与 '{topic}' 相关的知识")
            return ""
        
        # 格式化输出
        output_parts = [
            f"===== Web3 知识背景 ({len(top_records)} 条相关记录) ====="
        ]
        
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
    """
    从主题中提取关键词
    """
    # 移除常见停用词
    stopwords = {"的", "了", "是", "在", "和", "与", "或", "对", "为", "将", "会", "能", "可以", "如何", "什么", "怎么", "分析", "介绍"}
    
    # 简单分词（按空格、标点分割）
    words = re.split(r'[\s,，。！？、：；""''【】\[\]()（）]+', topic)
    
    # 过滤停用词和短词
    keywords = [w.strip() for w in words if w.strip() and len(w.strip()) >= 2 and w.strip() not in stopwords]
    
    return keywords


def calculate_match_score(keywords: list[str], text: str) -> int:
    """
    计算关键词匹配分数
    """
    text_lower = text.lower()
    score = 0
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            score += 1
    
    return score


def get_text_value(field_value) -> str:
    """
    从 Lark 字段值中提取文本
    """
    if isinstance(field_value, str):
        return field_value
    elif isinstance(field_value, list):
        # 富文本格式
        texts = []
        for item in field_value:
            if isinstance(item, dict):
                texts.append(item.get("text", ""))
            elif isinstance(item, str):
                texts.append(item)
        return "".join(texts)
    elif isinstance(field_value, dict):
        return field_value.get("text", str(field_value))
    else:
        return str(field_value) if field_value else ""
