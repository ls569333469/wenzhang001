"""
P23v2 扩展测试：4条新素材（监管、链上、项目、观点各1条）
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
        "type": "监管法律",
        "text": "FTX 前高管 Ryan Salame 发推指控称，美国司法部曾在其认罪前承诺不调查其妻子，但随后仍对其妻子提起指控，并称相关行动发生在其入监服刑之后。"
    },
    {
        "type": "链上监测",
        "text": "据 @EmberCN 监测，易理华旗下 Trend Research 已累计将 63.04 万枚 ETH (12.94 亿美元) 转进币安，链上现仅剩 2.13 万枚 ETH (4394 万美元)。"
    },
    {
        "type": "项目动态",
        "text": "据 Onchain Lens 监测，2 月 7 日，稳定币发行商 Circle 在过去 9 小时内于 Solana 链上增发了 15 亿枚 USDC。"
    },
    {
        "type": "人物观点",
        "text": "Cardano 创始人 Charles Hoskinson 表示，自己在加密资产上的账面亏损已达到约 30 亿美元，但并不打算出售任何持仓。"
    },
]

def run_test():
    print(f"\n{'='*60}")
    print(f"  🚀 P23v2 扩展测试（4条新素材）")
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
            print(f"\n  {'─'*50}")
            print(f"  📌 {v['label']}（{methods_str}）")
            print(f"  字数: {v['char_count']}")
            print(f"  {'─'*50}")
            print(f"  {v['content']}")

        all_results.append({
            "id": i,
            "type": item["type"],
            "input": item["text"],
            "elapsed_sec": round(elapsed, 1),
            "variants": variants,
        })

        print(f"\n  ⏱️ 耗时: {elapsed:.1f}秒")

    # 保存
    out_path = os.path.join(os.path.dirname(__file__), "test_results_p23v2_ext.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "version": "p23v2_extended",
            "results": all_results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存: {out_path}")

if __name__ == "__main__":
    run_test()
