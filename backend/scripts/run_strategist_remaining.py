"""
策略官终版 - 剩余 5 个项目
"""
import sys, time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
from app.services.surf_service import SurfService

PROJECTS = [
    {
        "name": "Parallel",
        "twitter": "@theparallel_io",
        "category": "GameFi",
        "token": "$PRL",
        "stage": "已上线",
        "catalyst": "2025生态扩展合作",
    },
    {
        "name": "Aleph Zero",
        "twitter": "@Aleph__Zero",
        "category": "Infra",
        "token": "$AZERO",
        "stage": "已上线",
        "catalyst": "2026网络升级发布",
    },
    {
        "name": "Chiliz",
        "twitter": "@chiliz",
        "category": "RWA",
        "token": "$CHZ",
        "stage": "已上线",
        "catalyst": "2026-02 2030 SportFi宣言发布",
    },
    {
        "name": "Kyber Network",
        "twitter": "@KyberNetwork",
        "category": "DeFi",
        "token": "$KNC",
        "stage": "已上线",
        "catalyst": "2025 TVL稳定增长",
    },
    {
        "name": "Dicey",
        "twitter": "@diceyhq",
        "category": "GameFi",
        "token": "无",
        "stage": "已上线",
        "catalyst": "2026 Magic Eden合作上线",
    },
]

PROMPT_TEMPLATE = (
    "深度调研项目 {name} ({twitter})。\n"
    "侦察线索: 赛道 {category}，代币 {token}，阶段 {stage}，催化剂 {catalyst}。\n\n"
    "输出完整投研报告，包含以下板块，只写事实和数据：\n\n"
    "## 📊 项目定位\n"
    "是什么、做什么、核心产品、目标市场。\n\n"
    "## 💰 融资\n"
    "用表格列出每轮融资：\n"
    "| 时间 | 轮次 | 金额 | 领投方 |\n"
    "融资总额。\n\n"
    "## 👥 团队\n"
    "核心成员（姓名/角色/背景），可信度 1-10。\n\n"
    "## 🪙 代币经济学\n"
    "代币符号、是否已发行、总供应量、分配比例、解锁计划。\n\n"
    "## 📈 市场数据\n"
    "当前价格、市值、FDV、TVL、Twitter 粉丝数。\n\n"
    "## 🔥 近期催化剂\n"
    "最近已发生 + 即将发生的关键事件（TGE/空投/主网/上所/产品发布/合作），注明日期。\n\n"
    "## 🏁 竞品对比\n"
    "同赛道 2-3 个竞品，简要对比定位和差异。\n\n"
    "不要附带来源链接和 URL。没有数据的板块直接跳过。"
)

OUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

results = []
for i, p in enumerate(PROJECTS, 1):
    prompt = PROMPT_TEMPLATE.format(**p)
    print(f"\n{'='*60}")
    print(f"🧪 [{i}/5] 策略官 | {p['name']} ({p['twitter']})")
    print(f"{'='*60}")
    print("⏳ 调用 Surf API...")

    surf = SurfService()
    start = time.time()
    result = surf.call(
        model="surf-1.5",
        user_prompt=prompt,
        abilities=["search"],
        reasoning="high",
        timeout=600,
    )
    elapsed = time.time() - start
    status = result.get("status", 0)
    content = result.get("content", "")

    print(f"✅ 完成 ({elapsed:.0f}s) | 状态: {status} | 内容: {len(content)} 字符")

    if status == 200:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = OUT_DIR / f"strat_FINAL_{p['name']}_{ts}.md"
        report = (
            f"# 📋 投研报告 | {p['name']}\n\n"
            f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
            f"> 耗时: {elapsed:.0f}s  \n"
            f"> 内容长度: {len(content)} 字符  \n\n"
            f"---\n\n"
            f"{content}\n\n"
        )
        filepath.write_text(report, encoding="utf-8")
        print(f"📁 已保存: {filepath}")
        results.append({"name": p["name"], "elapsed": elapsed, "chars": len(content), "ok": True})
    else:
        print(f"❌ 错误: {result.get('error', '')[:200]}")
        results.append({"name": p["name"], "elapsed": elapsed, "chars": 0, "ok": False})

print(f"\n\n{'='*60}")
print("📊 汇总")
print(f"{'='*60}")
for r in results:
    status = "✅" if r["ok"] else "❌"
    print(f"  {status} {r['name']:<16} {r['elapsed']:>5.0f}s  {r['chars']:>5} 字符")
print(f"\n📂 结果目录: {OUT_DIR}")
