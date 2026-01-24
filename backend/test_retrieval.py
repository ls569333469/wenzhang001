"""检查检索到的具体 Web3 知识内容"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.services.knowledge_retriever import retrieve_web3_knowledge

# 模拟用户输入的话题
topic = "数据：终极空头接连做空 BTC 已达一年，前三笔亏损后此次盈利达 6500 万美元"

print(f"=== 检索话题 ===")
print(f"{topic}\n")

result = retrieve_web3_knowledge(topic)

print(f"=== 检索结果 ===")
print(result if result else "未检索到相关内容")
