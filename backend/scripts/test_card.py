"""
配图生成快速测试 — 用真实项目数据生成 HTML 卡片
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.card_generator import generate_card_html

# 用今天策略官报告的数据
projects = [
    {
        "name": "Giza",
        "twitter": "@gizatechxyz",
        "category": "DeFi AI",
        "summary": "非托管 DeFi AI 代理基础设施，支持跨协议自动执行收益策略",
        "catalyst": "02-26 Giza World 产品发布",
    },
    {
        "name": "Taiko",
        "twitter": "@taikoxyz",
        "category": "Layer2",
        "summary": "开源无许可以太坊等价 ZK-Rollup L2，完全 EVM 兼容",
        "catalyst": "02月 ERC-8004 主网发布",
    },
    {
        "name": "Kaito AI",
        "twitter": "@KaitoAI",
        "category": "AI",
        "summary": "AI 驱动的社交情报与预测市场平台，量化 mindshare 数据",
        "catalyst": "02-10 与 Polymarket 合作推出 Attention Markets",
    },
    {
        "name": "Chiliz",
        "twitter": "@chiliz",
        "category": "SportFi",
        "summary": "体育粉丝经济 SportFi L1 公链，粉丝代币生态",
        "catalyst": "02-03 Vision 2030 直播",
    },
    {
        "name": "Kyber Network",
        "twitter": "@KyberNetwork",
        "category": "DeFi",
        "summary": "多链 DEX 流动性聚合协议，支持 25 条链",
        "catalyst": "02-09 上线 MegaETH",
    },
    {
        "name": "Parallel",
        "twitter": "@ParallelTCG",
        "category": "GameFi",
        "summary": "NFT 链上 TCG 卡牌游戏与元宇宙创作平台",
        "catalyst": "",
    },
]

html = generate_card_html(projects, "20260301")

out_path = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "card_test_20260301.html"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(html, encoding="utf-8")
print(f"✅ 配图 HTML 已生成: {out_path}")
print(f"   双击打开浏览器预览")
