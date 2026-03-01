"""
推文 Writer 测试 — 验证新版逐项目推文格式

输入: 3 个项目的策略官投研报告（Giza, Taiko, Kaito AI）
输出: 每个项目一条独立推文
验证: 标题格式、30天事件过滤、无可信度/建议/URL
"""
import sys, time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
from app.core.llm import generate_text

# 用策略官真实报告作为输入
STRATEGIST_REPORTS = """
## Giza (@gizatechxyz)

## 📊 项目定位
Giza 是构建自主、非托管 DeFi 代理的基础设施。核心产品：Giza World（可视化代理导航界面）、Giza Optimizer（多协议收益优化引擎）。目标市场：DeFi 用户、机构投资者。

## 💰 融资
| 时间 | 轮次 | 金额 | 领投方 |
|------|------|------|--------|
| 2023-07-11 | PRE SEED | 3000000 | CoinFund |
| 2025-01-29 | ICO | 1500000 | |
| 2025-05-15 | Undisclosed | 2200000 | |
融资总额：6700000 美元。

## 👥 团队
Renç Korzay（CEO，区块链基础设施背景）；Fran Algaba（CTO，技术架构经验）；Cem F. Dagdelen（CPO）。

## 🪙 代币经济学
代币符号：GIZA。已发行。总供应量：1000000000。Team & Advisors 18.25%、Community 22.21%。TGE 总解锁 6%。

## 📈 市场数据
价格：0.0345 美元。市值：9589350 美元。FDV：34500000 美元。TVL：20690000 美元。Twitter：102145。

## 🔥 近期催化剂
ICO（2025-01-29）；TGE（2025-05-20）；Giza World 产品发布（2026-02-26，统一代理界面）。ARMA/Pulse 退役迁移（2026-03-26）。

## 🏁 竞品对比
ZyFAI（多链收益优化）；Virtuals Protocol（通用 AI 代理平台）。

---

## Taiko (@taiko_xyz)

## 📊 项目定位
开源、无许可的以太坊等价ZK-Rollup Layer-2，支持未修改的ETH合约。

## 💰 融资
| 时间 | 轮次 | 金额 | 领投方 |
|------|------|------|--------|
| 2024-03-02 | SERIES A | 15000000 | Hashed, Lightspeed |
| 2023-06-08 | Undisclosed | 22000000 | HongShan |
融资总额：37045000 美元。

## 👥 团队
Daniel Wang（Co-Founder, CEO, Loopring创始人）；Brecht Devos（CTO）。

## 🪙 代币经济学
代币符号：TAIKO。已发行。总量：1000000000。流通：169248698。

## 📈 市场数据
价格：0.126 美元。市值：24274800 美元。FDV：126026000 美元。TVL：8125670 美元。

## 🔥 近期催化剂
Shasta升级（2025-03-26）；100% ZK覆盖（2025-12）；HTX上市（2026-01，涨47%）；ERC-8004主网（2026-02）。

## 🏁 竞品对比
Optimism (OP)；Arbitrum (ARB)；zkSync (ZK)。

---

## Kaito AI (@kaitoai)

## 📊 项目定位
AI 驱动的 InfoFi 网络，聚合社交媒体数据做 mindshare 和 sentiment 分析。

## 💰 融资
| 时间 | 轮次 | 金额 | 领投方 |
|------|------|------|--------|
| 2023 | Seed | 5300000 | Dragonfly, Sequoia China |
| 2023 | Seed | 5500000 | Spartan Group |
融资总额：10800000 美元。

## 👥 团队
Yu Hu（CEO，前 Citadel 和 Deutsche Bank 分析师）。

## 🪙 代币经济学
代币符号：KAITO。已发行（2025 TGE）。总量：1000000000。Airdrop 12%。

## 📈 市场数据
价格：0.338 美元。市值：81586149 美元。FDV：337831000 美元。Twitter：421616。

## 🔥 近期催化剂
TGE（2025-02-20）；与 Polymarket 合作（2026-02-10）；3月 Attention Markets 扩展。

## 🏁 竞品对比
LunarCrush；Santiment；Noise。
"""

# 构建推文 prompt（跟 daily_report_service.py 一致）
today = datetime.now()
date_30d_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")

system_prompt = (
    "你是 Web3 Alpha 猎手，负责写 X(Twitter) 推文。\n\n"
    "## 任务\n"
    "根据投研报告，为每个项目生成一条独立推文。\n\n"
    "## 推文格式（每个项目一条）\n"
    "```\n"
    "🔍 项目名称 @X账号\n\n"
    "一段话介绍项目定位和核心产品（2-3句）\n\n"
    "💰 融资金额 + 领投方\n"
    "👥 创始人姓名 + 背景\n"
    "🪙 代币符号 + 总量 + 关键分配\n"
    "📈 价格 | 市值 | FDV | TVL | Twitter粉丝\n\n"
    "🔥 近期催化剂：\n"
    "• 事件1（日期）\n"
    "• 事件2（日期）\n\n"
    "@X账号 | NFA\n"
    "```\n\n"
    "## 要求\n"
    f"- 催化剂只取 {date_30d_ago} 之后的事件，旧事件不要\n"
    "- 标题只写项目名称和 @X账号，不写代币符号和赛道\n"
    "- 不写可信度评分\n"
    "- 不写建议动作、投资建议\n"
    "- 不附带 URL 和来源链接\n"
    "- 没有数据的行直接跳过\n"
)

user_prompt = (
    f"今日投研的 3 个项目：Giza, Taiko, Kaito AI\n\n"
    f"投研简报内容：\n{STRATEGIST_REPORTS}"
)

OUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "tweet"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"🐦 推文 Writer 测试")
print(f"📅 30天过滤线: {date_30d_ago}")
print(f"⏳ 调用本地 LLM (豆包)...")

start = time.time()
result = generate_text(
    prompt=user_prompt,
    provider="volcengine",
    temperature=0.7,
    system_prompt=system_prompt,
    max_tokens=6000,
)
elapsed = time.time() - start

print(f"✅ 完成 ({elapsed:.1f}s) | 内容: {len(result)} 字符")

# 分析质量
noise_keywords = ["建议", "操作", "策略", "可信度", "http", "https"]
noise_hits = sum(1 for kw in noise_keywords if kw in result)
has_old_events = any(y in result for y in ["2023-", "2024-", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05"])

print(f"\n📊 质量分析:")
print(f"   噪音关键词命中: {noise_hits}")
print(f"   包含旧事件(30天前): {'❌ 是' if has_old_events else '✅ 否'}")
print(f"   🔍 标记数: {result.count('🔍')}")
print(f"   @账号数: {result.count('@')}")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
filepath = OUT_DIR / f"tweet_test_{ts}.md"
report = (
    f"# 🐦 推文 Writer 测试\n\n"
    f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    f"> 耗时: {elapsed:.1f}s  \n"
    f"> 内容长度: {len(result)} 字符  \n"
    f"> 噪音: {noise_hits} | 旧事件: {'有' if has_old_events else '无'}  \n\n"
    f"---\n\n"
    f"## 📝 System Prompt\n\n```\n{system_prompt}\n```\n\n"
    f"---\n\n"
    f"## 📥 LLM 返回\n\n{result}\n\n"
)
filepath.write_text(report, encoding="utf-8")
print(f"📁 已保存: {filepath}")
