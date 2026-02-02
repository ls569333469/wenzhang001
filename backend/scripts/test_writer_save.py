"""
直接测试 Writer Agent，保存结果到文件
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_writer_directly():
    from app.agents.writer import writer_agent
    from app.graph import enforce_mode_length, calculate_length
    
    mode = "deep_analysis"
    requested_length = "short"
    enforced_length = enforce_mode_length(mode, requested_length)
    
    state = {
        "raw_input": "前 Coinbase CTO：实物黄金并非对冲美元危机的最佳品种，比特币更具抗审查优势。前 Coinbase CTO Balaji 发推表示，当今几乎每种资产类别都可能被政府没收。虽然贵金属被认为是对冲美元危机的传统选择，但实物黄金并非最佳品种，因为其存在运输困难、存储安全隐患和流动性问题。银行黄金或 ETF 黄金则具有交易对手风险，可能会被关闭、冻结或重新评估。此外，如果出于任何原因出现美元危机，黄金交易功能可能被迫紧急暂停。相比之下，比特币具有抗审查优势，是一种无需第三方许可即可交易的自托管数字商品。尽管 Coinbase 等交易所可以收取您的 BTC，但自托管可以消除此风险。",
        "mode": mode,
        "style": "banfo",
        "length": enforced_length,
        "retention_level": 3,
        "narrative_type": "project_review",
        "strategy_json": '{"pain_point": "黄金并非最佳避险品", "hook_angle": "比特币抗审查优势", "outline": ["黄金局限性", "比特币优势", "结论"]}',
        "api_config": {"provider": "volcengine"},
        "web3_knowledge": ""
    }
    
    result = writer_agent(state)
    
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Result type: {type(result)}\n")
        f.write(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}\n\n")
        
        if isinstance(result, dict):
            if "draft_content" in result:
                content = result["draft_content"]
                f.write(f"Content length: {len(content)} chars\n\n")
                f.write("=== CONTENT ===\n")
                f.write(content)
            if "error" in result:
                f.write(f"\nError: {result['error']}\n")
    
    print("Result saved to test_output.txt")

if __name__ == "__main__":
    test_writer_directly()
