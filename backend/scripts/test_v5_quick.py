"""
P22 V5 快速测试脚本：8条代表性素材（每类2条）
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
from datetime import datetime
from app.agents.writer import writer_agent
from app.core.mode_configs import get_mode_config

# === 8条代表性素材（每类2条）===
TEST_MATERIALS = [
    # 🏷️ 人物观点型 (最好写)
    {"type": "人物观点", "text": "BitMEX 联合创始人 Arthur Hayes 发文称，近期比特币下跌可能主要源于围绕 IBIT 结构性产品的交易商对冲行为。他指出，银行发行的相关结构性产品在市场波动时会触发交易商卖出比特币现货进行对冲。"},
    {"type": "人物观点", "text": "Cardano 创始人 Charles Hoskinson 表示，自己在加密资产上的账面亏损已达到约 30 亿美元，但并不打算出售任何持仓。"},

    # 🏷️ 监管/法律型 (次好写)
    {"type": "监管法律", "text": "FTX 前高管 Ryan Salame 发推指控称，美国司法部曾在其认罪前承诺不调查其妻子，但随后仍对其妻子提起指控，并称相关行动发生在其入监服刑之后。"},
    {"type": "监管法律", "text": "北京社科院副院长范文仲发文指出，虚拟货币与证券代币监管新规并非全盘否定区块链等技术应用，而是对可能演变为系统性风险源头的活动加以明确约束，合规创新仍留空间。"},

    # 🏷️ 行情/数据型
    {"type": "行情数据", "text": "BTC 跌破 65,000 美元，截至 2 月 6 日 13:00 (UTC+8)，BTC 报约 64,239.2 美元，24 小时跌幅 9.50%；ETH 跌破 1,900 美元，报约 1,890.17 美元，24 小时下跌 9.80%。24小时内全球清算额达到约17亿美元，其中约15亿美元为多头头寸。"},
    {"type": "行情数据", "text": "流行歌手 Justin Bieber 于 2022 年 1 月以 500 ETH（约 130 万美元）购入 Bored Ape Yacht Club NFT（Bored Ape #3001），目前该 NFT 市值已跌至约 1.3 万美元，浮亏接近 99%。"},

    # 🏷️ 链上监测 & 项目动态型 (最难写)
    {"type": "链上监测", "text": "据 @EmberCN 监测，易理华旗下 Trend Research 已累计将 63.04 万枚 ETH (12.94 亿美元) 转进币安，链上现仅剩 2.13 万枚 ETH (4394 万美元)。"},
    {"type": "项目动态", "text": "据 Onchain Lens 监测，2 月 7 日，稳定币发行商 Circle 在过去 9 小时内于 Solana 链上增发了 15 亿枚 USDC。"},
]


def run_v5_test():
    """V5 快速测试"""
    mode = "short_article"
    mode_config = get_mode_config(mode)
    length_constraints = mode_config.get("length", {"min": 50, "max": 300, "target": 200})
    
    results = []
    
    print(f"\n{'='*60}")
    print(f"  🚀 P22 V5 口语化短评 快速测试")
    print(f"  素材数量: {len(TEST_MATERIALS)}")
    print(f"  字数目标: {length_constraints}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(TEST_MATERIALS, 1):
        material = item["text"]
        mat_type = item["type"]
        print(f"\n--- [{mat_type}] 素材 {i}/{len(TEST_MATERIALS)} ---")
        print(f"输入: {material[:80]}...")
        
        state = {
            "raw_input": material,
            "mode": mode,
            "style": "mimeng",
            "retention_level": 3,
            "strategy_json": "{}",
            "api_config": {"provider": "volcengine"},
            "web3_knowledge": ""
        }
        
        try:
            result = writer_agent(state)
            
            content = ""
            if isinstance(result, dict):
                content = result.get("draft_content", "") or ""
            else:
                content = str(result)
            
            char_count = len(content)
            target = length_constraints["target"]
            
            results.append({
                "id": i,
                "type": mat_type,
                "input": material[:100],
                "output": content,
                "char_count": char_count,
                "in_range": length_constraints["min"] <= char_count <= length_constraints["max"],
                "near_target": abs(char_count - target) <= target * 0.3,
            })
            
            # 直接打印完整输出
            print(f"\n📝 输出 ({char_count}字):")
            print(f"{'─'*40}")
            print(content)
            print(f"{'─'*40}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "id": i, "type": mat_type, "input": material[:100],
                "output": f"ERROR: {e}", "char_count": 0,
                "in_range": False, "near_target": False,
            })
    
    # === 汇总 ===
    print(f"\n\n{'='*60}")
    print(f"  📊 V5 测试汇总")
    print(f"{'='*60}")
    
    for r in results:
        status = "✅" if r["in_range"] else "❌"
        print(f"  #{r['id']} [{r['type']}] {r['char_count']}字 {status}")
    
    success = [r for r in results if r["char_count"] > 0]
    if success:
        counts = [r["char_count"] for r in success]
        print(f"\n  平均: {sum(counts)/len(counts):.0f}字")
        print(f"  范围: {min(counts)}-{max(counts)}字")
    
    # 保存结果
    output_path = os.path.join(os.path.dirname(__file__), "test_results_v5.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "version": "v5",
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 结果已保存: {output_path}")


if __name__ == "__main__":
    run_v5_test()
