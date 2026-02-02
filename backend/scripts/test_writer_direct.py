"""
直接测试 Writer Agent，查看长篇生成的原始响应
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_writer_directly():
    print("="*70)
    print("  直接测试 Writer Agent (长篇)")
    print("="*70)
    
    from app.agents.writer import writer_agent
    from app.graph import enforce_mode_length, calculate_length
    
    # 模拟 state
    mode = "deep_analysis"
    requested_length = "short"
    enforced_length = enforce_mode_length(mode, requested_length)
    
    print(f"\n📋 模拟参数:")
    print(f"   mode: {mode}")
    print(f"   requested length: {requested_length}")
    print(f"   enforced length: {enforced_length}")
    print(f"   length_constraints: {calculate_length(enforced_length)}")
    
    state = {
        "raw_input": "前 Coinbase CTO：实物黄金并非对冲美元危机的最佳品种，比特币更具抗审查优势。前 Coinbase CTO Balaji 发推表示，当今几乎每种资产类别都可能被政府没收。虽然贵金属被认为是对冲美元危机的传统选择，但实物黄金并非最佳品种，因为其存在运输困难、存储安全隐患和流动性问题。银行黄金或 ETF 黄金则具有交易对手风险，可能会被关闭、冻结或重新评估。此外，如果出于任何原因出现美元危机，黄金交易功能可能被迫紧急暂停。相比之下，比特币具有抗审查优势，是一种无需第三方许可即可交易的自托管数字商品。尽管 Coinbase 等交易所可以收取您的 BTC，但自托管可以消除此风险。",
        "mode": mode,
        "style": "banfo",
        "length": enforced_length,  # 使用强制后的 length
        "retention_level": 3,
        "narrative_type": "project_review",
        "strategy_json": '{"pain_point": "黄金并非最佳避险品", "hook_angle": "比特币抗审查优势", "outline": ["黄金局限性", "比特币优势", "结论"]}',
        "api_config": {"provider": "volcengine"},
        "web3_knowledge": ""
    }
    
    print(f"\n🧠 调用 writer_agent...")
    print("-"*50)
    
    try:
        result = writer_agent(state)
        
        print(f"\n📊 返回结果类型: {type(result)}")
        print(f"📊 返回结果 keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
        
        if isinstance(result, dict):
            if "draft_content" in result:
                content = result["draft_content"]
                print(f"\n✅ draft_content 长度: {len(content)} 字")
                if content:
                    print(f"\n预览:\n{content[:500]}...")
                else:
                    print(f"⚠️ draft_content 为空!")
            
            if "error" in result:
                print(f"\n❌ 错误信息: {result['error']}")
        else:
            print(f"\n⚠️ 返回值不是 dict: {result}")
            
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_writer_directly()
