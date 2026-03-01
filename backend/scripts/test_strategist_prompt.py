"""
策略官 Prompt 迭代测试工具

用法:
    python scripts/test_strategist_prompt.py              # 跑当前轮所有候选
    python scripts/test_strategist_prompt.py --id A       # 只跑 A
    python scripts/test_strategist_prompt.py --compare    # 对比当前轮结果
    python scripts/test_strategist_prompt.py --history    # 查看历史

测试输入: 使用 Scout G 版返回的真实项目数据
结果保存: reports/research/prompt_test/strategist/round{N}/
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.surf_service import SurfService

# ============================================================
#  📌 当前测试轮次
# ============================================================
CURRENT_ROUND = 2

# ============================================================
#  📦 测试用项目数据（来自 Scout G 版真实返回）
#  测试时只取 1-2 个项目，节省 API 调用
# ============================================================

TEST_PROJECTS = [
    {
        "name": "Giza",
        "twitter": "@gizatechxyz",
        "category": "Infra",
        "kol_24h": 2,
        "token": "$GIZA",
        "stage": "TGE前",
        "catalyst": "2025代理经济启动",
    },
    {
        "name": "Kaito AI",
        "twitter": "@kaitoai",
        "category": "AI",
        "kol_24h": 1,
        "token": "$KAITO",
        "stage": "已上线",
        "catalyst": "2025 TGE后增长加速",
    },
]

# 默认测试第一个项目
DEFAULT_PROJECT = TEST_PROJECTS[0]

# ============================================================
#  📝 候选 Prompt
# ============================================================

ROUNDS = {
    1: {
        "A": {
            "label": "当前线上版（8维度）",
            "build_prompt": lambda p: (
                f"请对以下 Web3 项目做全面深度投研分析：\n\n"
                f"项目名称: {p['name']}\n"
                f"Twitter: {p['twitter']}\n"
                f"类别: {p['category']}\n"
                f"热度原因: {p.get('catalyst', '')}\n\n"
                f"请从以下维度分析（每个维度都要有具体数据支撑）：\n"
                f"1. 项目概要（定位、核心产品、目标市场）\n"
                f"2. 融资与估值（融资历史、投资方、估值、FDV）\n"
                f"3. 团队（核心成员、背景、可信度评分 1-10）\n"
                f"4. 市场数据（价格、市值、TVL、社交数据）\n"
                f"5. 代币经济学（总量、分配、解锁计划）\n"
                f"6. 竞品对比（同赛道 2-3 个竞品）\n"
                f"7. 风险与机会（关键风险点、投资机会窗口）\n"
                f"8. 总结评级（1-10 分 + 一句话结论）"
            ),
        },
        "B": {
            "label": "事实卡片+事件时间线",
            "build_prompt": lambda p: (
                f"调研项目 {p['name']} ({p['twitter']})，赛道: {p['category']}。\n\n"
                f"输出两部分：\n\n"
                f"## 信息卡\n"
                f"| 字段 | 数据 |\n"
                f"|------|------|\n"
                f"| 定位 | 一句话概括 |\n"
                f"| 代币 | 符号 + 是否已发行 |\n"
                f"| 阶段 | 预发布/测试网/已上线/TGE前 |\n"
                f"| 融资 | 总额 + 最近一轮（金额/领投方/时间） |\n"
                f"| 团队 | 创始人姓名+背景 |\n"
                f"| 可信度 | 1-10 分 |\n"
                f"| 风险 | 1-2 个关键风险 |\n\n"
                f"## 近期事件\n"
                f"最近 30 天内的关键事件，每行格式：日期 — 事件。\n"
                f"没有数据的字段直接跳过整行。"
            ),
        },
        "C": {
            "label": "结构化4段式",
            "build_prompt": lambda p: (
                f"深度调研项目 {p['name']} ({p['twitter']})。\n"
                f"侦察线索: 赛道 {p['category']}，代币 {p.get('token', '未知')}，"
                f"阶段 {p.get('stage', '未知')}，催化剂 {p.get('catalyst', '')}。\n\n"
                f"输出以下 4 个板块，每段 2-3 句话，只写事实和数据：\n\n"
                f"## 📊 一句话定位\n"
                f"是什么、做什么、核心产品。\n\n"
                f"## 💰 融资与团队\n"
                f"融资总额、最新一轮、领投方、核心团队成员背景、可信度 1-10。\n\n"
                f"## 🔥 近期催化剂\n"
                f"最近 30 天关键事件，注明日期。\n\n"
                f"## ⚠️ 关键风险\n"
                f"2-3 个具体风险点。\n\n"
                f"没有数据的板块直接跳过。"
            ),
        },
    },

    # ---- 第 2 轮: 聚焦关键时间节点（Alpha 日报核心价值）----
    2: {
        "D": {
            "label": "信息卡+关键事件时间线",
            "build_prompt": lambda p: (
                f"调研项目 {p['name']} ({p['twitter']})，赛道: {p['category']}。\n\n"
                f"输出两部分：\n\n"
                f"## 信息卡\n"
                f"| 字段 | 数据 |\n"
                f"|------|------|\n"
                f"| 定位 | 一句话概括 |\n"
                f"| 代币 | 符号 + 是否已发行 |\n"
                f"| 阶段 | 预发布/测试网/已上线/TGE前 |\n"
                f"| 融资 | 总额 + 最近一轮（金额/领投方/时间） |\n"
                f"| 团队 | 创始人姓名+背景 |\n"
                f"| 可信度 | 1-10 分 |\n\n"
                f"## 关键事件时间线\n"
                f"列出所有可查到的里程碑事件，包括已发生和即将发生的：\n"
                f"格式：日期 — 事件（如 TGE/测试网/主网/预售/空投/上所/融资/产品发布）\n"
                f"按时间正序排列。\n"
                f"没有数据的字段直接跳过。"
            ),
        },
        "E": {
            "label": "纯时间线（最精简）",
            "build_prompt": lambda p: (
                f"调研项目 {p['name']} ({p['twitter']})。\n\n"
                f"只输出该项目的关键事件时间线，格式：\n"
                f"日期 — 事件类型 — 具体内容\n\n"
                f"事件类型包括：融资/TGE/测试网/主网/预售/空投/上所/产品发布/合作。\n"
                f"包含已发生和计划中的事件，按时间正序排列。"
            ),
        },
        "F": {
            "label": "信息卡+里程碑表格",
            "build_prompt": lambda p: (
                f"调研项目 {p['name']} ({p['twitter']})，赛道: {p['category']}。\n\n"
                f"输出两部分：\n\n"
                f"## 信息卡\n"
                f"| 字段 | 数据 |\n"
                f"|------|------|\n"
                f"| 定位 | 一句话概括 |\n"
                f"| 代币 | 符号 + 是否已发行 |\n"
                f"| 融资总额 | 金额 |\n"
                f"| 团队 | 创始人 + 背景 |\n"
                f"| 可信度 | 1-10 分 |\n\n"
                f"## 里程碑\n"
                f"| 日期 | 事件类型 | 内容 |\n"
                f"|------|----------|------|\n"
                f"列出融资/TGE/测试网/主网/预售/空投/上所/产品发布等关键节点。\n"
                f"包含已发生和计划中的事件。\n"
                f"没有数据的字段直接跳过。"
            ),
        },
    },
}

# ============================================================
#  输出目录
# ============================================================
BASE_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist"


def get_round_dir(round_num: int) -> Path:
    d = BASE_DIR / f"round{round_num}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_test(prompt_id: str, prompt_text: str, label: str, round_num: int, project: dict) -> dict:
    """执行单次测试"""
    print(f"\n{'='*60}")
    print(f"🧪 Round {round_num} | [{prompt_id}] {label}")
    print(f"📦 项目: {project['name']} ({project['twitter']})")
    print(f"{'='*60}")
    print(f"📝 Prompt:\n{prompt_text[:300]}...\n")
    print("⏳ 调用 Surf API...")

    surf = SurfService()
    start = time.time()
    result = surf.call(
        model="surf-1.5",
        user_prompt=prompt_text,
        abilities=["search"],
        reasoning="high",
        timeout=600,
    )
    elapsed = time.time() - start

    status = result.get("status", 0)
    content = result.get("content", "")
    error = result.get("error", "")

    print(f"✅ 完成 ({elapsed:.0f}s) | 状态: {status} | 内容长度: {len(content)} 字符")

    if status != 200:
        print(f"❌ 错误: {error[:200]}")
        return {"status": status, "error": error, "elapsed": elapsed}

    # ---- 内容分析 ----
    lines = content.strip().split("\n")
    table_lines = [l for l in lines if l.strip().startswith("|")]
    heading_lines = [l for l in lines if l.strip().startswith("#")]
    noise_keywords = ["建议", "操作", "策略", "方法论", "数据来源", "搜索过程", "值得关注", "不可忽视"]
    noise_hits = sum(1 for kw in noise_keywords if kw in content)

    print(f"\n📊 内容分析:")
    print(f"   总行数: {len(lines)}")
    print(f"   表格行: {len(table_lines)}")
    print(f"   标题行: {len(heading_lines)}")
    print(f"   噪音关键词命中: {noise_hits}")
    print(f"   内容质量: {'✅ 干净' if noise_hits == 0 else '⚠️ 有噪音' if noise_hits < 3 else '❌ 噪音多'}")

    # ---- 保存 ----
    out_dir = get_round_dir(round_num)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = out_dir / f"strat_{prompt_id}_{project['name']}_{ts}.md"

    report = (
        f"# 🧪 策略官 Round {round_num} | [{prompt_id}] {label}\n\n"
        f"> 项目: {project['name']} ({project['twitter']})  \n"
        f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
        f"> 耗时: {elapsed:.0f}s  \n"
        f"> 内容长度: {len(content)} 字符  \n"
        f"> 噪音关键词: {noise_hits}  \n\n"
        f"---\n\n"
        f"## 📝 Prompt\n\n```\n{prompt_text}\n```\n\n"
        f"---\n\n"
        f"## 📥 Surf 完整返回\n\n{content}\n\n"
    )

    filepath.write_text(report, encoding="utf-8")
    print(f"📁 已保存: {filepath}")

    return {
        "id": prompt_id,
        "label": label,
        "project": project["name"],
        "status": status,
        "elapsed": elapsed,
        "content_len": len(content),
        "noise_hits": noise_hits,
        "filepath": str(filepath),
    }


def show_compare(round_num: int):
    d = BASE_DIR / f"round{round_num}"
    if not d.exists():
        print(f"❌ Round {round_num} 目录不存在")
        return
    files = sorted(d.glob("strat_*.md"))
    if not files:
        print(f"❌ Round {round_num} 没有测试结果")
        return
    print(f"\n📊 策略官 Round {round_num} 结果对比")
    print(f"{'='*60}")
    for f in sorted(files):
        print(f"  📄 {f.name}")


def show_history():
    if not BASE_DIR.exists():
        print("❌ 还没有任何测试结果")
        return
    for d in sorted(BASE_DIR.iterdir()):
        if d.is_dir() and d.name.startswith("round"):
            files = list(d.glob("strat_*.md"))
            print(f"📁 {d.name}: {len(files)} 份测试结果")


def main():
    parser = argparse.ArgumentParser(description="策略官 Prompt 迭代测试工具")
    parser.add_argument("--id", type=str, help="只跑指定 ID")
    parser.add_argument("--project", type=int, default=0, help="测试项目索引 (0=Giza, 1=Kaito)")
    parser.add_argument("--round", type=int, default=CURRENT_ROUND, help="轮次")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()

    if args.history:
        show_history()
        return
    if args.compare:
        show_compare(args.round)
        return

    project = TEST_PROJECTS[min(args.project, len(TEST_PROJECTS) - 1)]
    round_num = args.round
    prompts = ROUNDS.get(round_num, {})

    if not prompts:
        print(f"❌ Round {round_num} 没有定义候选 prompt")
        return

    results = []

    if args.id:
        pid = args.id.upper()
        if pid not in prompts:
            print(f"❌ 未找到 ID: {pid}，可用: {list(prompts.keys())}")
            return
        p = prompts[pid]
        prompt_text = p["build_prompt"](project)
        r = run_test(pid, prompt_text, p["label"], round_num, project)
        results.append(r)
    else:
        for pid, p in prompts.items():
            prompt_text = p["build_prompt"](project)
            r = run_test(pid, prompt_text, p["label"], round_num, project)
            results.append(r)

    # ---- 汇总 ----
    if len(results) > 1:
        print(f"\n\n{'='*60}")
        print(f"📊 策略官 Round {round_num} 对比汇总 (项目: {project['name']})")
        print(f"{'='*60}")
        print(f"{'ID':<4} {'标签':<20} {'耗时':>6} {'字数':>6} {'噪音':>4} {'评级'}")
        print("-" * 55)
        for r in results:
            nh = r.get("noise_hits", 0)
            grade = "✅" if nh == 0 else "⚠️" if nh < 3 else "❌"
            print(f"{r['id']:<4} {r['label']:<20} {r['elapsed']:>5.0f}s {r['content_len']:>6} {nh:>4} {grade}")

    print(f"\n📂 结果目录: {get_round_dir(round_num)}")


if __name__ == "__main__":
    main()
