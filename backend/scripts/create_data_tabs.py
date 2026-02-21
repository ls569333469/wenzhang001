"""
P27-P2: 创建 Google Sheets 数据 Tab 并填入种子数据
运行方式: python -m scripts.create_data_tabs
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source


def create_tab(spreadsheet, tab_name: str, headers: list, rows: list):
    """创建 Tab（如已存在则跳过），写入表头和数据"""
    try:
        ws = spreadsheet.worksheet(tab_name)
        print(f"  ✅ Tab '{tab_name}' 已存在，跳过创建")
    except Exception:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=len(rows) + 10, cols=len(headers))
        print(f"  🆕 Tab '{tab_name}' 已创建")
    
    # 写入表头 + 数据
    all_data = [headers] + rows
    ws.update(range_name=f"A1:{chr(64 + len(headers))}{len(all_data)}", values=all_data)
    print(f"  📝 写入 {len(rows)} 条种子数据")


def main():
    print("=" * 60)
    print("  P27-P2: 创建 Google Sheets 数据 Tab")
    print("=" * 60)
    
    # 初始化连接
    if not google_sheets_source._init_client():
        print("❌ Google Sheets 连接失败，请检查 credentials")
        return
    
    spreadsheet = google_sheets_source._spreadsheet
    print(f"✅ 已连接到 Google Sheets\n")
    
    # ===== 1. 吹捧素材 =====
    print("[1/4] 吹捧素材 Tab")
    create_tab(spreadsheet, "吹捧素材",
        headers=["日期", "作者", "内容", "分类", "来源"],
        rows=[
            ["2026-02-21", "@cz_binance", "Binance has processed over $100B in trading volume this month. Thank you for your support! 🙏", "cz", "X/Twitter"],
            ["2026-02-21", "@cz_binance", "Building in bear market, shipping in bull market. The cycle continues. Stay focused, stay building. 💪", "cz", "X/Twitter"],
            ["2026-02-20", "@haborofficial", "Web3 education is the key to mass adoption. We are building bridges, not walls. 🌉", "heyi", "X/Twitter"],
            ["2026-02-20", "@haborofficial", "刚参加完 Consensus 大会回来。行业的能量前所未有，大量传统金融机构正在积极布局。", "heyi", "X/Twitter"],
            ["2026-02-19", "@binance", "New listing announcement: $KAITO token is now available on Binance Spot. Trade now! 🚀", "official", "X/Twitter"],
            ["2026-02-19", "@binance", "Binance Earn now supports staking for 15+ new tokens. Earn rewards while you HODL.", "official", "X/Twitter"],
            ["2026-02-18", "@cz_binance", "Just met some amazing builders at ETHDenver. The innovation happening in DeFi is mind-blowing. Future is bright! ☀️", "cz", "X/Twitter"],
        ]
    )
    
    # ===== 2. 嘴撸项目 =====
    print("\n[2/4] 嘴撸项目 Tab")
    create_tab(spreadsheet, "嘴撸项目",
        headers=["项目ID", "项目名称", "最后写作时间"],
        rows=[
            ["bera", "Berachain", "3天前"],
            ["monad", "Monad", "5天前"],
            ["sui", "Sui", "1周前"],
            ["sei", "Sei", "2周前"],
            ["celestia", "Celestia", ""],
        ]
    )
    
    # ===== 3. 嘴撸_Berachain =====
    print("\n[3/4] 嘴撸_Berachain Tab")
    create_tab(spreadsheet, "嘴撸_Berachain",
        headers=["类型", "标题", "描述", "来源", "时间"],
        rows=[
            ["角度", "生态扩展", "DeFi 协议迁移趋势，Infrared 领跑", "", ""],
            ["角度", "PoL 机制", "流动性证明的创新——BGT 飞轮效应", "", ""],
            ["角度", "社区治理", "BGT 持有者权益与投票参与率", "", ""],
            ["角度", "TVL 增长", "链上数据分析——主网上线后的爆发", "", ""],
            ["情报", "Berachain 主网上线第一周 TVL 突破 $2B", "远超市场预期，成为今年增速最快的 L1", "DeFiLlama", "3h"],
            ["情报", "Infrared Finance 成为 Bera 最大 DeFi 协议", "TVL 占比超过 35%", "DeBank", "6h"],
            ["情报", "BGT 质押率达到 45%，远超预期", "社区参与度极高", "Dune", "12h"],
        ]
    )
    
    # ===== 4. 投研项目 =====
    print("\n[4/4] 投研项目 Tab")
    create_tab(spreadsheet, "投研项目",
        headers=["项目名", "赛道", "融资轮次", "融资金额", "投资方", "公链", "一句话摘要"],
        rows=[
            ["Ethena", "稳定币/DeFi", "Series B", "$100M", "Dragonfly, Franklin Templeton, PayPal Ventures", "Ethereum", "合成美元协议，通过 delta 中性对冲策略提供高收益稳定币 USDe"],
            ["Berachain", "Layer 1", "Series A", "$100M", "Polychain Capital, OKX Ventures, Framework", "Berachain", "基于 Proof of Liquidity 共识机制的 EVM 兼容 Layer 1"],
            ["Monad", "Layer 1", "Series A", "$225M", "Paradigm, Dragonfly, Electric Capital", "Monad", "超高性能 EVM 兼容链，目标 10000 TPS，并行执行引擎"],
            ["Story Protocol", "IP/创意经济", "Series B", "$80M", "a16z crypto, Polychain Capital", "Story Network", "可编程 IP 协议，让知识产权在链上可追溯、可组合、可交易"],
            ["Initia", "Layer 1/模块化", "Series A", "$7.5M", "Binance Labs, Delphi Digital, Hack VC", "Cosmos", "模块化 Layer 1，interwoven rollup 架构统一流动性和安全性"],
        ]
    )
    
    print("\n" + "=" * 60)
    print("  ✅ 全部 4 个 Tab 创建完成！")
    print("  📊 种子数据: 吹捧(7) + 嘴撸项目(5) + Bera情报(7) + 投研(5)")
    print("=" * 60)


if __name__ == "__main__":
    main()
