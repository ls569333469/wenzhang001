"""Phase 2: 10 个话题检索质量测试"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv()

from app.services.knowledge_retriever import retrieve_web3_knowledge

# 10 个分类话题
test_topics = [
    ("DeFi-DEX", "Uniswap V4 新功能发布，流动性挖矿收益分析"),
    ("DeFi-借贷", "Aave 借贷协议利率变化，清算机制更新"),
    ("NFT", "Azuki NFT 地板价暴跌，蓝筹 NFT 市场走势"),
    ("BTC", "比特币减半后矿工收益下降，算力迁移趋势"),
    ("AI+Crypto", "GPT-4 与区块链结合，AI Agent 赛道爆发"),
    ("安全", "DeFi 协议遭黑客攻击，损失数千万美元"),
    ("监管", "SEC 起诉 Coinbase，加密监管政策收紧"),
    ("宏观", "美联储加息对加密市场影响，比特币与美股相关性"),
    ("DAO", "Arbitrum DAO 投票争议，社区治理分裂"),
    ("投资", "a16z 领投 AI 初创公司，加密 VC 动态"),
]

print("="*70)
print("Phase 2: 检索质量测试 (10 个话题)")
print("="*70)

results = []

for category, topic in test_topics:
    print(f"\n[{category}] {topic[:40]}...")
    result = retrieve_web3_knowledge(topic)
    
    if result:
        # 提取匹配数量
        import re
        match = re.search(r'(\d+) 条相关记录', result)
        count = int(match.group(1)) if match else 0
        
        # 提取第一条标题
        title_match = re.search(r'\[Web3背景 1\] (.+?) ---', result)
        first_title = title_match.group(1)[:30] if title_match else "N/A"
        
        results.append({
            "category": category,
            "topic": topic[:30],
            "match_count": count,
            "first_match": first_title,
            "relevant": "?"  # 需要人工判断
        })
        print(f"   -> 匹配 {count} 条 | 首条: {first_title}")
    else:
        results.append({
            "category": category,
            "topic": topic[:30],
            "match_count": 0,
            "first_match": "无匹配",
            "relevant": "N/A"
        })
        print(f"   -> [X] 无匹配")

# 输出汇总表
print("\n" + "="*70)
print("检索结果汇总")
print("="*70)
print(f"{'分类':<12} {'话题':<25} {'匹配数':<6} {'首条标题':<30}")
print("-"*70)
for r in results:
    print(f"{r['category']:<12} {r['topic']:<25} {r['match_count']:<6} {r['first_match']:<30}")

# 统计
total = len(results)
matched = sum(1 for r in results if r['match_count'] > 0)
print(f"\n匹配率: {matched}/{total} = {matched/total*100:.1f}%")
