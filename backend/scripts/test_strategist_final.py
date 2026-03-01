"""
策略官终版 Prompt 测试
"""
import sys, time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
from app.services.surf_service import SurfService

PROJECT = {
    "name": "Giza",
    "twitter": "@gizatechxyz",
    "category": "Infra",
    "token": "$GIZA",
    "stage": "TGE前",
    "catalyst": "2025代理经济启动",
}

PROMPT = (
    f"深度调研项目 {PROJECT['name']} ({PROJECT['twitter']})。\n"
    f"侦察线索: 赛道 {PROJECT['category']}，代币 {PROJECT.get('token', '未知')}，"
    f"阶段 {PROJECT.get('stage', '未知')}，催化剂 {PROJECT.get('catalyst', '')}。\n\n"
    f"输出完整投研报告，包含以下板块，只写事实和数据：\n\n"
    f"## 📊 项目定位\n"
    f"是什么、做什么、核心产品、目标市场。\n\n"
    f"## 💰 融资\n"
    f"用表格列出每轮融资：\n"
    f"| 时间 | 轮次 | 金额 | 领投方 |\n"
    f"融资总额。\n\n"
    f"## 👥 团队\n"
    f"核心成员（姓名/角色/背景），可信度 1-10。\n\n"
    f"## 🪙 代币经济学\n"
    f"代币符号、是否已发行、总供应量、分配比例、解锁计划。\n\n"
    f"## 📈 市场数据\n"
    f"当前价格、市值、FDV、TVL、Twitter 粉丝数。\n\n"
    f"## 🔥 近期催化剂\n"
    f"最近已发生 + 即将发生的关键事件（TGE/空投/主网/上所/产品发布/合作），注明日期。\n\n"
    f"## 🏁 竞品对比\n"
    f"同赛道 2-3 个竞品，简要对比定位和差异。\n\n"
    f"不要附带来源链接和 URL。没有数据的板块直接跳过。"
)

OUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"📝 Prompt:\n{PROMPT[:300]}...\n")
print("⏳ 调用 Surf API...")

surf = SurfService()
start = time.time()
result = surf.call(
    model="surf-1.5",
    user_prompt=PROMPT,
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
    filepath = OUT_DIR / f"strat_FINAL_{PROJECT['name']}_{ts}.md"
    report = (
        f"# 🧪 策略官终版测试 | {PROJECT['name']}\n\n"
        f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
        f"> 耗时: {elapsed:.0f}s  \n"
        f"> 内容长度: {len(content)} 字符  \n\n"
        f"---\n\n"
        f"## 📝 Prompt\n\n```\n{PROMPT}\n```\n\n"
        f"---\n\n"
        f"## 📥 Surf 完整返回\n\n{content}\n\n"
    )
    filepath.write_text(report, encoding="utf-8")
    print(f"📁 已保存: {filepath}")
else:
    print(f"❌ 错误: {result.get('error', '')[:200]}")
