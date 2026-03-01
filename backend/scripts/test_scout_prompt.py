"""
侦察官 Prompt 迭代测试工具

用法:
    python scripts/test_scout_prompt.py                    # 跑当前轮所有候选
    python scripts/test_scout_prompt.py --id A             # 只跑 A
    python scripts/test_scout_prompt.py --custom "prompt"  # 跑自定义 prompt
    python scripts/test_scout_prompt.py --compare          # 对比当前轮所有已有结果
    python scripts/test_scout_prompt.py --history          # 查看所有轮次历史

工作流:
    1. 在 ROUNDS 字典里添加新一轮的候选 prompt
    2. 修改 CURRENT_ROUND 指向当前轮次
    3. 运行脚本，查看结果
    4. 决定最佳 prompt 后进入下一轮迭代

结果保存: reports/research/prompt_test/round{N}/scout_{ID}_{时间}.md
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载 .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.surf_service import SurfService

# ============================================================
#  📌 当前测试轮次（每轮测试完，手动递增）
# ============================================================
CURRENT_ROUND = 2

# ============================================================
#  📝 所有轮次的候选 Prompt
#
#  每轮根据上一轮结果写新版本。
#  格式: ROUNDS[轮次号] = { "ID": {"label": "描述", "prompt": "..."}, ... }
# ============================================================

ROUNDS = {
    # ---- 第 1 轮: 基准测试 ----
    1: {
        "A": {
            "label": "极简版",
            "prompt": "检索 @leakmealpha 近 7 天的推文，整理出 Web3 和 AI 项目表格",
        },
        "B": {
            "label": "表格约束版",
            "prompt": (
                "检索 @leakmealpha 近 7 天推文 + 访问 leak.me 网站 trending。\n"
                "leak.me 是 Crypto KOL Tracker。\n"
                "只输出一张表格，不要其他内容：\n"
                "| 项目名称 | Twitter | 类别 | KOL 关注数 | 热度原因 |\n"
                "排除个人 KOL、交易所、媒体、纯 meme 币。最多 8 个。"
            ),
        },
        "C": {
            "label": "当前线上版",
            "prompt": (
                "请访问和分析 leak.me（https://leak.me/）网站的当前 trending 数据。"
                "请整理出所有被 KOL 关注的 Web3 和 AI 项目，"
                "用表格列出：项目名称、Twitter 账号、类别、24h KOL 新关注数、热度原因。"
                "排除个人 KOL 账号、交易所和媒体。"
            ),
        },
        "D": {
            "label": "手动测试版（含时间+禁深度分析）",
            "prompt": (
                "请访问和分析@leakmealpha和http://leak.me的trending 数据，"
                "从数据中识别出的核心项目，"
                "用表格列出：项目名称、Twitter 账号、类别、24h KOL 新关注数、热度原因、时间，"
                "精准提及时间，排除个人 KOL 账号、交易所和媒体，不做其他深度分析"
            ),
        },
    },

    # ---- 第 2 轮: 基于 B（零噪音冠军）迭代 ----
    # 目标: 保持 B 的干净度，增加字段让侦察官完成预分类
    2: {
        "E": {
            "label": "B+代币+阶段",
            "prompt": (
                "检索 @leakmealpha 近 7 天推文 + 访问 leak.me 网站 trending。\n"
                "leak.me 是 Crypto KOL Tracker。\n"
                "只输出一张表格，不要其他内容：\n"
                "| 项目名称 | Twitter | 类别 | KOL 关注数 | 是否有代币 | 项目阶段 | 热度原因 |\n"
                "项目阶段填：预发布/已上线/TGE前/空投中 之一。\n"
                "排除个人 KOL、交易所、媒体、纯 meme 币。最多 8 个。"
            ),
        },
        "F": {
            "label": "B+催化剂替代热度",
            "prompt": (
                "检索 @leakmealpha 近 7 天推文 + 访问 leak.me 网站 trending。\n"
                "leak.me 是 Crypto KOL Tracker。\n"
                "只输出一张表格，不要其他内容：\n"
                "| 项目名称 | Twitter | 类别 | KOL 关注数 | 项目阶段 | 近期催化剂 |\n"
                "项目阶段填：预发布/已上线/TGE前/空投中 之一。\n"
                "近期催化剂只写一句话，如：融资/空投/TGE/主网上线/合作。\n"
                "排除个人 KOL、交易所、媒体、纯 meme 币。最多 8 个。"
            ),
        },
        "G": {
            "label": "B+完整预分类（代币+阶段+催化剂）",
            "prompt": (
                "检索 @leakmealpha 近 7 天推文 + 访问 leak.me 网站 trending。\n"
                "leak.me 是 Crypto KOL Tracker，追踪加密 KOL 的新关注行为。\n"
                "只输出一张表格，不要写任何分析或说明：\n"
                "| 项目名称 | Twitter | 赛道 | KOL 关注数 | 代币 | 阶段 | 近期催化剂 |\n"
                "字段说明：\n"
                "- 赛道: DeFi/L2/AI/GameFi/RWA/Infra 等\n"
                "- 代币: 代币符号（如 $NEAR）或 无\n"
                "- 阶段: 预发布/测试网/已上线/TGE前\n"
                "- 近期催化剂: 一句话（融资/空投/TGE/上线/合作）\n"
                "排除个人 KOL、交易所、媒体、纯 meme 币。最多 8 个。"
            ),
        },
    },
}

# ============================================================
#  输出目录
# ============================================================
BASE_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test"


def get_round_dir(round_num: int) -> Path:
    d = BASE_DIR / f"round{round_num}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_test(prompt_id: str, prompt_text: str, label: str, round_num: int) -> dict:
    """执行单次测试"""
    print(f"\n{'='*60}")
    print(f"🧪 Round {round_num} | [{prompt_id}] {label}")
    print(f"{'='*60}")
    print(f"📝 Prompt:\n{prompt_text}\n")
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

    # ---- 内容结构分析 ----
    lines = content.strip().split("\n")
    table_lines = [l for l in lines if l.strip().startswith("|")]
    noise_lines = [l for l in lines if l.strip()
                   and not l.strip().startswith("|")
                   and not l.strip().startswith("---")
                   and not l.strip().startswith("#")]
    heading_lines = [l for l in lines if l.strip().startswith("#")]

    total_chars = len(content)
    table_chars = sum(len(l) for l in table_lines)
    noise_ratio = 1 - (table_chars / total_chars) if total_chars > 0 else 1

    print(f"\n📊 结构分析:")
    print(f"   总行数: {len(lines)}")
    print(f"   表格行: {len(table_lines)}")
    print(f"   标题行: {len(heading_lines)}")
    print(f"   正文/噪音行: {len(noise_lines)}")
    print(f"   噪音比: {noise_ratio:.0%}")
    print(f"   干净度: {'✅ 高' if noise_ratio < 0.2 else '⚠️ 中' if noise_ratio < 0.5 else '❌ 低'}")

    # ---- 保存结果 ----
    out_dir = get_round_dir(round_num)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = out_dir / f"scout_{prompt_id}_{ts}.md"

    report = (
        f"# 🧪 Round {round_num} | [{prompt_id}] {label}\n\n"
        f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
        f"> 耗时: {elapsed:.0f}s  \n"
        f"> 内容长度: {total_chars} 字符  \n"
        f"> 表格行: {len(table_lines)} | 噪音行: {len(noise_lines)} | 噪音比: {noise_ratio:.0%}  \n\n"
        f"---\n\n"
        f"## 📝 Prompt\n\n```\n{prompt_text}\n```\n\n"
        f"---\n\n"
        f"## 📥 Surf 完整返回\n\n{content}\n\n"
        f"---\n\n"
        f"## ✅ 有用部分（表格）\n\n"
    )
    if table_lines:
        report += "\n".join(table_lines) + "\n\n"
    else:
        report += "_（无表格内容）_\n\n"

    report += f"## ❌ 噪音部分（应剔除）\n\n"
    if noise_lines:
        for l in noise_lines:
            report += f"- {l.strip()}\n"
    else:
        report += "_（无噪音，非常干净 ✅）_\n"

    filepath.write_text(report, encoding="utf-8")
    print(f"📁 已保存: {filepath}")

    return {
        "id": prompt_id,
        "label": label,
        "status": status,
        "elapsed": elapsed,
        "table_lines": len(table_lines),
        "noise_lines": len(noise_lines),
        "noise_ratio": noise_ratio,
        "filepath": str(filepath),
    }


def show_compare(round_num: int):
    """对比某轮已有的测试结果"""
    d = BASE_DIR / f"round{round_num}"
    if not d.exists():
        print(f"❌ Round {round_num} 目录不存在")
        return

    files = sorted(d.glob("scout_*.md"))
    if not files:
        print(f"❌ Round {round_num} 没有测试结果")
        return

    print(f"\n📊 Round {round_num} 测试结果对比")
    print(f"{'='*60}")
    print(f"{'文件':<35} {'表格行':>6} {'噪音行':>6} {'噪音比':>6}")
    print("-" * 55)
    for f in files:
        text = f.read_text(encoding="utf-8")
        # 简易解析
        tl = text.count("表格行: ") and text.split("表格行: ")[1].split(" ")[0] if "表格行: " in text else "?"
        nl = text.split("噪音行: ")[1].split(" ")[0] if "噪音行: " in text else "?"
        nr = text.split("噪音比: ")[1].split(" ")[0] if "噪音比: " in text else "?"
        print(f"{f.name:<35} {tl:>6} {nl:>6} {nr:>6}")

    print(f"\n📂 结果目录: {d}")


def show_history():
    """查看所有轮次"""
    if not BASE_DIR.exists():
        print("❌ 还没有任何测试结果")
        return

    for d in sorted(BASE_DIR.iterdir()):
        if d.is_dir() and d.name.startswith("round"):
            files = list(d.glob("scout_*.md"))
            print(f"📁 {d.name}: {len(files)} 份测试结果")
            for f in sorted(files):
                print(f"   - {f.name}")


def main():
    parser = argparse.ArgumentParser(description="侦察官 Prompt 迭代测试工具")
    parser.add_argument("--id", type=str, help="只跑指定 ID")
    parser.add_argument("--custom", type=str, help="自定义 prompt")
    parser.add_argument("--round", type=int, default=CURRENT_ROUND, help="指定轮次")
    parser.add_argument("--compare", action="store_true", help="对比当前轮结果")
    parser.add_argument("--history", action="store_true", help="查看所有轮次历史")
    args = parser.parse_args()

    if args.history:
        show_history()
        return

    if args.compare:
        show_compare(args.round)
        return

    round_num = args.round
    prompts = ROUNDS.get(round_num, {})

    if not prompts and not args.custom:
        print(f"❌ Round {round_num} 没有定义候选 prompt")
        print(f"   请在脚本的 ROUNDS[{round_num}] 中添加候选")
        return

    results = []

    if args.custom:
        r = run_test("X", args.custom, "自定义", round_num)
        results.append(r)
    elif args.id:
        pid = args.id.upper()
        if pid not in prompts:
            print(f"❌ Round {round_num} 中未找到 ID: {pid}，可用: {list(prompts.keys())}")
            return
        p = prompts[pid]
        r = run_test(pid, p["prompt"], p["label"], round_num)
        results.append(r)
    else:
        for pid, p in prompts.items():
            r = run_test(pid, p["prompt"], p["label"], round_num)
            results.append(r)

    # ---- 汇总 ----
    if len(results) > 1:
        print(f"\n\n{'='*60}")
        print(f"📊 Round {round_num} 对比汇总")
        print(f"{'='*60}")
        print(f"{'ID':<4} {'标签':<14} {'耗时':>6} {'表格行':>6} {'噪音行':>6} {'噪音比':>7} {'评级'}")
        print("-" * 55)
        for r in results:
            nr = r.get("noise_ratio", 1)
            grade = "✅ 干净" if nr < 0.2 else "⚠️ 一般" if nr < 0.5 else "❌ 杂乱"
            print(f"{r.get('id','?'):<4} {r.get('label',''):<14} {r.get('elapsed',0):>5.0f}s {r.get('table_lines',0):>6} {r.get('noise_lines',0):>6} {nr:>6.0%} {grade}")

    print(f"\n📂 结果目录: {get_round_dir(round_num)}")
    print(f"\n💡 下一步:")
    print(f"   1. 打开上面的 .md 文件查看详细结果")
    print(f"   2. 决定哪些信息保留、哪些剔除")
    print(f"   3. 在脚本 ROUNDS[{round_num + 1}] 中写新候选")
    print(f"   4. 把 CURRENT_ROUND 改为 {round_num + 1}")
    print(f"   5. 重新运行脚本")


if __name__ == "__main__":
    main()
