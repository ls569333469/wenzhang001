"""
推文 Writer 全量测试 — 8 个策略官报告 → 8 条推文
"""
import sys, time, glob
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
from app.core.llm import generate_text

# 读取所有策略官终版报告
REPORT_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round4"

reports = []
for f in sorted(REPORT_DIR.glob("strat_FINAL_*.md")):
    # 跳过带 URL 的旧版 Giza（用第二版）
    if "191408" in f.name:
        continue
    text = f.read_text(encoding="utf-8")
    # 只取 Surf 返回内容部分
    if "## 📥 Surf 完整返回" in text:
        content = text.split("## 📥 Surf 完整返回")[-1].strip()
    elif "---" in text:
        parts = text.split("---", 2)
        content = parts[-1].strip() if len(parts) > 2 else text
    else:
        content = text
    # 提取项目名
    name = f.stem.replace("strat_FINAL_", "").split("_20")[0]
    reports.append({"name": name, "content": content})
    print(f"  📄 {name}: {len(content)} 字符")

print(f"\n📦 共加载 {len(reports)} 份报告")

# 拼接所有报告
combined = "\n\n---\n\n".join(
    f"## {r['name']}\n\n{r['content']}" for r in reports
)
project_names = [r["name"] for r in reports]

# 推文 prompt（跟 daily_report_service.py 一致）
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
    "• 事件2（日期）\n"
    "```\n\n"
    "## 要求\n"
    f"- 催化剂只取 {date_30d_ago} 之后的事件，旧事件不要\n"
    "- 标题只写项目名称和 @X账号，不写代币符号和赛道\n"
    "- 不写可信度评分\n"
    "- 不写建议动作、投资建议\n"
    "- 不附带 URL 和来源链接\n"
    "- 金额用简写：$670万、$1.08亿、$0.035，不要写 6700000 USD 这种长数字\n"
    "- 粉丝数用简写：10.2万粉，不要写 102145\n"
    "- 没有数据的行直接跳过\n"
)

user_prompt = (
    f"今日投研的 {len(reports)} 个项目：{', '.join(project_names)}\n\n"
    f"投研报告内容：\n{combined}"
)

OUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "tweet"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n🐦 推文 Writer 全量测试 ({len(reports)} 项目)")
print(f"📅 30天过滤线: {date_30d_ago}")
print(f"📝 输入长度: {len(user_prompt)} 字符")
print(f"⏳ 调用豆包...")

start = time.time()
result = generate_text(
    prompt=user_prompt,
    provider="volcengine",
    temperature=0.7,
    system_prompt=system_prompt,
    max_tokens=6000,
)
elapsed = time.time() - start

print(f"✅ 完成 ({elapsed:.1f}s) | 输出: {len(result)} 字符")

# 质量分析
import re
tweet_count = result.count("🔍")
noise_keywords = ["建议", "操作", "策略", "可信度", "http", "https", "NFA"]
noise_hits = {kw: result.count(kw) for kw in noise_keywords if kw in result}
old_dates = re.findall(r"202[3-5]-(?:0[1-9]|1[0-2])-\d{2}", result)

print(f"\n📊 质量分析:")
print(f"   🔍 推文数: {tweet_count}")
print(f"   噪音: {noise_hits if noise_hits else '无'}")
print(f"   旧日期(30天前): {old_dates if old_dates else '无'}")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
filepath = OUT_DIR / f"tweet_full_{ts}.md"
report_md = (
    f"# 🐦 推文 Writer 全量测试 | {len(reports)} 项目\n\n"
    f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    f"> 耗时: {elapsed:.1f}s  \n"
    f"> 输出: {len(result)} 字符  \n"
    f"> 推文数: {tweet_count}  \n"
    f"> 噪音: {noise_hits if noise_hits else '无'}  \n"
    f"> 旧事件: {old_dates if old_dates else '无'}  \n\n"
    f"---\n\n"
    f"## 📥 LLM 返回\n\n{result}\n\n"
)
filepath.write_text(report_md, encoding="utf-8")
print(f"📁 已保存: {filepath}")
