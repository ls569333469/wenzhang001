"""测试 5 个话题的 Knowledge_Repo 检索效果"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.services.knowledge_retriever import retrieve_web3_knowledge

topics = [
    "Vitalik：我们需要更多、更好的 DAO，而非仅由代币投票控制的金库",
    "美 SEC 撤销对 Gemini Earn 的诉讼",
    "数据：若 ETH 跌破 2,805 美元，主流 CEX 累计多单清算强度将达 8.37 亿美元",
    "AI 初创公司 Inferact 完成 1.5 亿美元种子轮融资，a16z 与 Lightspeed 领投",
    "最近 Perp DEX 赛道的币价表现确实不太理想，HYPE 从高点跌到了 21 刀，LIT 维持到了 1.7 刀，还有 ParaDEX 出了事故，整个板块看起来有点萎靡。"
]

for i, topic in enumerate(topics, 1):
    print(f"\n{'='*60}")
    print(f"【话题 {i}】{topic[:50]}...")
    print(f"{'='*60}")
    
    result = retrieve_web3_knowledge(topic)
    
    if result:
        # 只显示前 500 字符
        print(result[:800] if len(result) > 800 else result)
    else:
        print("[X] 未检索到相关内容")
    
    print()
