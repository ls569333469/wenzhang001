"""
配图生成测试 — 带催化剂日期过滤
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.card_generator import generate_card_html, pick_best_catalyst

# 模拟今天 2026-03-02
TODAY = datetime(2026, 3, 2)

# 用真实策略官报告的催化剂列表
projects_raw = [
    {
        "name": "Giza",
        "twitter": "@gizatechxyz",
        "category": "DeFi AI",
        "summary": "非托管 DeFi AI 代理基础设施，支持跨协议自动执行收益策略",
        "catalysts": [
            "2026-02-26 Giza World 上线",
            "2026-02-27 Giza World Snapshots 功能发布",
            "2026-03-26 ARMA/Pulse 退役迁移",
        ],
    },
    {
        "name": "Taiko",
        "twitter": "@taikoxyz",
        "category": "Layer2",
        "summary": "开源无许可以太坊等价 ZK-Rollup L2，完全 EVM 兼容",
        "catalysts": [
            "2026-02 ERC-8004 主网发布",
        ],
    },
    {
        "name": "Kaito AI",
        "twitter": "@KaitoAI",
        "category": "AI",
        "summary": "AI 驱动的社交情报与预测市场平台，量化 mindshare 数据",
        "catalysts": [
            "2026-02-10 与 Polymarket 合作推出 Attention Markets",
            "2026-02-20 解锁 3.63%",
            "2026-03-22 解锁 1.76%",
            "3月 Attention Markets 扩展至多领域",
        ],
    },
    {
        "name": "Chiliz",
        "twitter": "@chiliz",
        "category": "SportFi",
        "summary": "体育粉丝经济 SportFi L1 公链，粉丝代币生态",
        "catalysts": [
            "2026-02-03 Vision 2030 直播发布",
            "2026-02-04 Fan Token Play 上线",
            "2026-02-21 波兰加密社区会议",
            "2026年 美国市场重新进入",
        ],
    },
    {
        "name": "Kyber Network",
        "twitter": "@KyberNetwork",
        "category": "DeFi",
        "summary": "多链 DEX 流动性聚合协议，支持 25 条链",
        "catalysts": [
            "2026-02-09 KyberSwap 上线 MegaETH",
            "2026-02-25 FairFlow 第30周期启动",
            "2026-02-28 推广最佳路由执行",
        ],
    },
    {
        "name": "Parallel",
        "twitter": "@ParallelTCG",
        "category": "GameFi",
        "summary": "NFT 链上 TCG 卡牌游戏与元宇宙创作平台",
        "catalysts": [],
    },
]

# 过滤催化剂
projects = []
print("📅 催化剂过滤结果 (基准日期 2026-03-02):\n")
for p in projects_raw:
    best = pick_best_catalyst(p["catalysts"], today=TODAY)
    print(f"  {p['name']:16s} → {best or '(无近期事件)'}")
    projects.append({
        **{k: v for k, v in p.items() if k != "catalysts"},
        "catalyst": best,
    })

print()

html = generate_card_html(projects, "20260302")

out_path = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "card_test_20260302.html"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(html, encoding="utf-8")
print(f"✅ 配图 HTML 已生成: {out_path}")
