"""
P22 批量测试脚本：短篇连珠炮风格
数据源：吴说区块链 48H 内容（2026-02-06 ~ 2026-02-07）
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

# === 30条吴说区块链素材 ===
TEST_MATERIALS = [
    "BTC 跌破 65,000 美元，截至 2 月 6 日 13:00 (UTC+8)，BTC 报约 64,239.2 美元，24 小时跌幅 9.50%；ETH 跌破 1,900 美元，报约 1,890.17 美元，24 小时下跌 9.80%。24小时内全球清算额达到约17亿美元，其中约15亿美元为多头头寸。",
    "BitMEX 联合创始人 Arthur Hayes 发文称，近期比特币下跌可能主要源于围绕 IBIT 结构性产品的交易商对冲行为。他指出，银行发行的相关结构性产品在市场波动时会触发交易商卖出比特币现货进行对冲。",
    "YZi Labs 声明，近期发现有账号在 X 平台冒充其投资人身份进行活动。YZi Labs 表示，官方投资人社交账号均已列于官网，提醒社区用户通过官方渠道核实信息，警惕冒充与诈骗行为，注意资产与信息安全。",
    "据 @EmberCN 监测，Aave 创始人 Stani.eth 在过去 13 小时内继续卖出 1700 枚 ETH（约 353 万美元），购入了 30,727 枚 AAVE。",
    "FTX 前高管 Ryan Salame 发推指控称，美国司法部曾在其认罪前承诺不调查其妻子，但随后仍对其妻子提起指控，并称相关行动发生在其入监服刑之后。",
    "据 WSJ，美国监管机构已批准 Erebor Bank 获得全国性银行牌照，成为特朗普第二任期内首家获批的新设银行。该行由 Palmer Luckey 发起。",
    "据 Arkham 分析师 Emmett Gallic 监测，比特币矿企 Hut 8 向 Coinbase 信贷抵押托管账户再转入 1560 枚 BTC，价值约 1 亿美元。",
    "据 Bitdeer 官方披露，截至 2026 年 2 月 6 日，持有 1,039.5 枚比特币（不包括客户存款）。在过去一周，Bitdeer 减少了 468.8 枚比特币。",
    "据《金融时报》报道，Crypto.com 创始人 Kris Marszalek 以约 7000 万美元收购域名 AI.com，成为目前公开披露的史上最高价域名交易。",
    "Arkham 表示，Tesla 目前仍持有约 1.15 万枚 BTC，其在 2022 年 LUNA 崩盘期间已出售大部分比特币，仅保留最初购入量约 20%。",
    "彭博 ETF 分析师 Eric Balchunas 发推表示，美东时间 2 月 5 日，iShares Bitcoin Trust（IBIT）在价格单日下跌 13% 的情况下成交额达约 100 亿美元，刷新上市以来成交量纪录。",
    "a16z 合伙人、a16z crypto 领导者 Chris Dixon 发文称，当前流行的说法将加密货币的非投机用例局限于稳定币和比特币，但他认为这只是起点。他坚持加密投资长期主义，相信区块链金融普及后会涌现其他类别的应用。",
    "据 Arkham 分析师监测，与 Multicoin Capital 相关地址在过去 24 小时内向 FalconX 和 Galaxy Digital 转移约 44 万枚 JITOSOL。",
    "巴西联邦区法院判处哥伦比亚籍棋手 Daniel Uribe Arteaga 因利用 Tether 的 USDT 实施诈骗及洗钱罪名成立，获刑 8 年。",
    "巴西圣保罗州法院裁定，要求 Circle 对涉诈资金进行冻结，在一起约 1.3 万美元的加密诈骗案件中下令冻结 USDC。该案被认定为巴西司法机构首次直接向稳定币发行方发出冻结命令。",
    "VanEck 数字资产研究主管 Matthew Sigel 表示，比特币近期下跌并非由单一黑天鹅事件触发，而是五大因素叠加所致：一是高杠杆快速出清，二是关税不确定性，三是ETF资金流向变化，四是矿企抛售压力，五是宏观情绪恶化。",
    "过去 30 天 Solana 价格下跌约 40%，拖累 SOL 财库型公司持仓大幅缩水。数据显示，19 家 SOL treasury 实体合计持有约 1850 万枚 SOL。",
    "Multicoin Capital 联合创始人 Tushar Jain 表示，Multicoin 已更新其长期投资论述，认为区块链已从早期基础设施建设阶段，进入以清算层和应用层为核心的新周期。",
    "流行歌手 Justin Bieber 于 2022 年 1 月以 500 ETH（约 130 万美元）购入 Bored Ape Yacht Club NFT（Bored Ape #3001），目前该 NFT 市值已跌至约 1.3 万美元，浮亏接近 99%。",
    "美国 Federal Reserve 拟推出精简版主账户（skinny master account），向部分机构开放有限的美联储支付系统接入权，引发加密银行与社区关注。",
    "彭博高级 ETF 分析师 Eric Balchunas 在 X 平台发文表示，21Shares 正在申请发行 Ondo ETF。他表示自己从没听说过这个 ETF 形式，认为这是一个新的尝试。",
    "Crypto.com 联合创始人兼 CEO Kris Marszalek 创立的 AI 平台 AI.com 宣布将面向零售用户推出自主 AI Agent。该 AI Agent 可执行链上操作和资产管理任务。",
    "据 @EmberCN 监测，易理华旗下 Trend Research 已累计将 63.04 万枚 ETH (12.94 亿美元) 转进币安，链上现仅剩 2.13 万枚 ETH (4394 万美元)。",
    "Cardano 创始人 Charles Hoskinson 表示，自己在加密资产上的账面亏损已达到约 30 亿美元，但并不打算出售任何持仓。",
    "MegaETH Foundation 宣布，将把其稳定币 USDM 产生的协议收入用于定期回购 MEGA 代币。官方表示，USDM 是 MegaETH 生态的核心资产。",
    "币安官方发推表示，2025 年，币安团队协助全球执法机构追回约 1.31 亿美元非法资产，并响应超过 7.1 万项官方执法请求。",
    "据 Onchain Lens 监测，2 月 7 日，稳定币发行商 Circle 在过去 9 小时内于 Solana 链上增发了 15 亿枚 USDC。",
    "CFTC 于 2 月 6 日重新发布 Staff Letter 25-40，并对支付型稳定币定义作出有限修订，明确国家信托银行可作为合规发行方。",
    "据加密记者 Eleanor Terrett，白宫稳定币收益相关讨论的下一轮会议已安排在下周二举行。消息人士称，本次仍为工作人员层级会议。",
    "北京社科院副院长范文仲发文指出，虚拟货币与证券代币监管新规并非全盘否定区块链等技术应用，而是对可能演变为系统性风险源头的活动加以明确约束，合规创新仍留空间。",
]


def run_batch_test():
    """批量测试短篇模式"""
    mode = "short_article"
    mode_config = get_mode_config(mode)
    length_constraints = mode_config.get("length", {"min": 50, "max": 300, "target": 200})
    
    results = []
    errors = []
    
    print(f"\n{'='*60}")
    print(f"  P22 短篇连珠炮批量测试")
    print(f"  素材数量: {len(TEST_MATERIALS)}")
    print(f"  字数目标: {length_constraints}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    for i, material in enumerate(TEST_MATERIALS, 1):
        print(f"\n--- 素材 {i}/{len(TEST_MATERIALS)} ---")
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
            min_len = length_constraints["min"]
            max_len = length_constraints["max"]
            
            results.append({
                "id": i,
                "input": material[:100],
                "output": content,
                "char_count": char_count,
                "in_range": min_len <= char_count <= max_len,
                "near_target": abs(char_count - target) <= target * 0.2,
            })
            
            print(f"输出 ({char_count}字): {content[:120]}...")
            print(f"字数: {'✅' if results[-1]['in_range'] else '❌'} 范围 | {'✅' if results[-1]['near_target'] else '❌'} 接近目标")
            
        except Exception as e:
            errors.append({"id": i, "input": material[:80], "error": str(e)})
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # === 汇总报告 ===
    print(f"\n\n{'='*60}")
    print(f"  📊 批量测试汇总报告")
    print(f"{'='*60}")
    print(f"总测试: {len(TEST_MATERIALS)}")
    print(f"成功: {len(results)}")
    print(f"失败: {len(errors)}")
    
    if results:
        counts = [r["char_count"] for r in results]
        in_range = sum(1 for r in results if r["in_range"])
        near_target = sum(1 for r in results if r["near_target"])
        
        print(f"\n📏 字数统计:")
        print(f"  平均: {sum(counts)/len(counts):.0f}字")
        print(f"  最短: {min(counts)}字")
        print(f"  最长: {max(counts)}字")
        print(f"  范围合格率: {in_range}/{len(results)} ({in_range/len(results)*100:.0f}%)")
        print(f"  接近目标率: {near_target}/{len(results)} ({near_target/len(results)*100:.0f}%)")
    
    if errors:
        print(f"\n❌ 错误列表:")
        for e in errors:
            print(f"  #{e['id']}: {e['error'][:100]}")
    
    # 保存结果
    output_path = os.path.join(os.path.dirname(__file__), "test_results_short_article.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "total": len(TEST_MATERIALS),
            "success": len(results),
            "errors": len(errors),
            "results": results,
            "error_details": errors,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存: {output_path}")
    
    # 打印全部内容
    print(f"\n\n{'='*60}")
    print(f"  📝 全部输出内容（供人工审查）")
    print(f"{'='*60}")
    for r in results:
        print(f"\n{'─'*40}")
        print(f"#{r['id']} ({r['char_count']}字)")
        print(f"{'─'*40}")
        print(r["output"])
    
    return results, errors


if __name__ == "__main__":
    run_batch_test()
