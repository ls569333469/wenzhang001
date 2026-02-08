"""
P23v2 动态方法选择 测试
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import json
from datetime import datetime
from app.agents.writer import writer_agent

TEST_MATERIALS = [
    {
        "type": "人物观点",
        "text": "流行歌手 Justin Bieber 于 2022 年 1 月以 500 ETH（约 130 万美元）购入 Bored Ape Yacht Club NFT（Bored Ape #3001），目前该 NFT 市值已跌至约 1.3 万美元，浮亏接近 99%。"
    },
    {
        "type": "行情数据",
        "text": "BTC 跌破 65,000 美元，截至 2 月 6 日 13:00 (UTC+8)，BTC 报约 64,239.2 美元，24 小时跌幅 9.50%；ETH 跌破 1,900 美元，报约 1,890.17 美元，24 小时下跌 9.80%。24小时内全球清算额达到约17亿美元，其中约15亿美元为多头头寸。"
    },
]

def run_test():
    print(f"\n{'='*60}")
    print(f"  🚀 P23v2 动态方法选择 测试")
    print(f"  时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")

    all_results = []

    for i, item in enumerate(TEST_MATERIALS, 1):
        print(f"\n{'━'*60}")
        print(f"  📄 素材 {i}: [{item['type']}]")
        print(f"  {item['text'][:80]}...")
        print(f"{'━'*60}")

        state = {
            "raw_input": item["text"],
            "mode": "short_article",
            "style": "mimeng",
            "retention_level": 3,
            "strategy_json": "{}",
            "api_config": {"provider": "volcengine"},
            "web3_knowledge": ""
        }

        start = datetime.now()
        result = writer_agent(state)
        elapsed = (datetime.now() - start).total_seconds()

        variants = result.get("variants", [])

        for v in variants:
            methods_str = ", ".join(v.get("methods", []))
            instruction = v.get("instruction", v.get("desc", ""))
            print(f"\n  {'─'*50}")
            print(f"  📌 {v['label']}")
            print(f"  方法: {methods_str}")
            print(f"  指令: {instruction}")
            print(f"  字数: {v['char_count']}")
            print(f"  {'─'*50}")
            print(f"  {v['content']}")

        all_results.append({
            "id": i,
            "type": item["type"],
            "input": item["text"][:100],
            "elapsed_sec": round(elapsed, 1),
            "variants": variants,
        })

        print(f"\n  ⏱️ 耗时: {elapsed:.1f}秒")

    # 保存
    out_path = os.path.join(os.path.dirname(__file__), "test_results_p23v2.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "version": "p23v2",
            "results": all_results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存: {out_path}")

if __name__ == "__main__":
    run_test()
