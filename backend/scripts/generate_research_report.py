"""
P31: 投研报告生成器
从 leak.me 热点项目列表 → Surf API 深度分析 → 精美中文投研报告
"""
import os
import sys
import time
import json
import httpx
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SURF_API_KEY = os.getenv("SURF_API_KEY")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"

if not SURF_API_KEY:
    print("ERROR: SURF_API_KEY not found")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ========== leak.me 24h 热点 Web3 项目（已整理） ==========
LEAKME_PROJECTS = [
    {
        "name": "Reveel",
        "twitter": "@r3vl_xyz",
        "category": "AI 支付 Infra",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "Agentic 支付功能 + Base 链 USDC + Binance booster 公告",
    },
    {
        "name": "Saturn Credit",
        "twitter": "@saturn_credit",
        "category": "BTC 收益 DeFi",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "11%+ BTC yield + Certora 审计 + Pudgy Penguins 顾问",
    },
    {
        "name": "TechDollar",
        "twitter": "@techdollarhq",
        "category": "DeFi 私人信贷",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "Web3 信用基础设施 + 私人信贷 yield",
    },
    {
        "name": "Takeover",
        "twitter": "@takeoverfun",
        "category": "GameFi / DEX",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "Harberger Taxes onchain + PVP 玩法 + Grid 部署",
    },
    {
        "name": "Taiko",
        "twitter": "@taiko_xyz",
        "category": "Layer 2",
        "kol_24h": 20,
        "kol_type": "混合",
        "buzz": "主网扩展 + 弹性缩放执行层",
    },
    {
        "name": "Kyber Network",
        "twitter": "@KyberNetwork",
        "category": "DeFi 聚合器",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "多链流动性更新 + 14% APR yield 推广",
    },
    {
        "name": "Clude",
        "twitter": "@cludebot",
        "category": "AI / Blockchain",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "On-chain 记忆证明 + 4846 记忆审计",
    },
    {
        "name": "Otonix",
        "twitter": "@otonix_tech",
        "category": "Web4 代理 Infra",
        "kol_24h": 20,
        "kol_type": "Degen 主导",
        "buzz": "Base 链 token launch + 自主代理自愈",
    },
]


def call_surf(model, query, abilities, reasoning="medium", timeout=300):
    """调用 Surf API"""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一位顶级加密货币投研分析师，服务于专业投资机构。\n"
                    "请用中文输出，使用结构化的 Markdown 格式。\n"
                    "要求：\n"
                    "- 所有数据必须有来源支撑，不确定的标注「待验证」\n"
                    "- 使用表格呈现关键数据对比\n"
                    "- 风险和机会需量化评分（1-10分）\n"
                    "- 结论简洁明确，给出操作建议"
                )
            },
            {"role": "user", "content": query}
        ],
        "stream": False,
        "reasoning_effort": reasoning,
        "ability": abilities,
        "citation": ["source"],
    }
    headers = {
        "Authorization": f"Bearer {SURF_API_KEY}",
        "Content-Type": "application/json",
    }
    start = time.time()
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(SURF_BASE_URL, headers=headers, json=payload)
        elapsed = time.time() - start
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": 200,
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "elapsed": elapsed,
            }
        return {"status": resp.status_code, "error": resp.text[:500], "elapsed": elapsed}
    except Exception as e:
        return {"status": "error", "error": str(e), "elapsed": time.time() - start}


def generate_project_report(project: dict) -> dict:
    """为单个项目生成深度投研报告"""
    name = project["name"]
    twitter = project["twitter"]
    category = project["category"]
    buzz = project["buzz"]

    query = f"""请对 {name}（{twitter}）进行深度投研分析。

背景信息：
- 项目类别：{category}
- 近期热度原因：{buzz}
- 24h 内获得 {project['kol_24h']} 个 Crypto KOL 新关注（来源：leak.me）

请按以下结构输出报告：

## 📊 项目概要
一段话概括项目定位、核心产品和目标市场。

## 💰 融资与估值
- 融资轮次、金额、投资方（用表格）
- 当前估值或 FDV（如有）

## 👥 团队
- 核心成员背景（用表格：姓名/角色/背景）
- 团队可信度评分（1-10）

## 📈 市场数据
- 代币价格、市值、24h 交易量（如已上线）
- TVL（如适用）
- 社交数据：X 粉丝数、Smart Followers

## 🔥 近期催化剂
- 为什么最近受到 KOL 关注？具体事件或公告。

## ⚠️ 风险评估
用表格列出 3-5 个主要风险，每个含：
- 风险描述
- 影响程度（高/中/低）
- 发生概率（高/中/低）

## 🎯 投资结论
- 一句话判断：看涨/中立/看跌 + 置信度百分比
- 适合的投资策略（持有/交易/观望）
- 关键跟踪指标（3-5个）"""

    print(f"\n  🔍 分析中: {name} ({twitter})...")
    result = call_surf(
        model="surf-1.5",
        query=query,
        abilities=["search", "market_analysis"],
        reasoning="high",
        timeout=300,
    )
    print(f"     ✅ 完成: {result.get('elapsed', 0):.0f}s, "
          f"{len(result.get('content', '')):.0f} 字符, "
          f"{result.get('usage', {}).get('total_tokens', '?')} tokens")
    return result


def build_final_report(projects: list, results: list):
    """组装最终精美报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"# 🌊 每日投研快报")
    lines.append(f"")
    lines.append(f"> **生成时间**: {now}  ")
    lines.append(f"> **数据来源**: leak.me KOL Tracker + Surf AI 深度分析  ")
    lines.append(f"> **分析模型**: surf-1.5 (reasoning: high)")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # === 热点总览 ===
    lines.append(f"## 📋 今日热点项目总览")
    lines.append(f"")
    lines.append(f"| # | 项目 | 类别 | 24h KOL | 热度原因 |")
    lines.append(f"|---|------|------|---------|----------|")
    for i, p in enumerate(projects, 1):
        lines.append(f"| {i} | **{p['name']}** ({p['twitter']}) | {p['category']} | +{p['kol_24h']} | {p['buzz'][:40]}... |")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # === 各项目详细报告 ===
    for i, (proj, res) in enumerate(zip(projects, results), 1):
        lines.append(f"## {i}. {proj['name']}")
        lines.append(f"")
        lines.append(f"> 📍 {proj['category']} | 🐦 [{proj['twitter']}](https://x.com/{proj['twitter'].lstrip('@')}) | 🔥 24h KOL +{proj['kol_24h']}")
        lines.append(f"")

        if res.get("content"):
            lines.append(res["content"])
        elif res.get("error"):
            lines.append(f"⚠️ 分析失败: {res['error'][:200]}")
        else:
            lines.append(f"⚠️ 无数据返回")

        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    # === 尾部 ===
    lines.append(f"## 📝 报告说明")
    lines.append(f"")
    lines.append(f"- **数据时效**: 基于 {now} 快照，市场数据可能已变动")
    lines.append(f"- **热点来源**: leak.me 追踪 Crypto KOL 的 X 关注行为，24h 新关注数反映机构/大V兴趣方向")
    lines.append(f"- **分析局限**: Surf AI 对新兴小项目的数据覆盖可能不完整，标注「待验证」的数据需人工确认")
    lines.append(f"- **免责声明**: 本报告仅供研究参考，不构成投资建议")
    lines.append(f"")

    return "\n".join(lines)


# ========== 主流程 ==========
if __name__ == "__main__":
    # 选取前 3 个项目做深度分析（控制 API 用量和时间）
    selected = LEAKME_PROJECTS[:3]

    print("=" * 60)
    print(f"📊 投研报告生成器 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   项目数: {len(selected)}")
    print("=" * 60)

    results = []
    for proj in selected:
        res = generate_project_report(proj)
        results.append(res)
        # API 冷却
        if proj != selected[-1]:
            print("     ⏳ 冷却 5s...")
            time.sleep(5)

    # 生成最终报告
    print("\n📄 组装最终报告...")
    report = build_final_report(selected, results)

    # 保存
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"daily_research_{date_str}.md"
    outpath = OUTPUT_DIR / filename
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ 报告已保存: {outpath}")

    # 统计
    total_time = sum(r.get("elapsed", 0) for r in results)
    total_tokens = sum(r.get("usage", {}).get("total_tokens", 0) for r in results)
    total_chars = sum(len(r.get("content", "")) for r in results)
    print(f"📊 统计: {total_time:.0f}s 总耗时, {total_tokens} tokens, {total_chars} 字符")
    print("Done!")
