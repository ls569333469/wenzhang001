"""
策略官 Round 3: 批量投研测试

把 Scout G 的完整 8 项目表格一次性传给 Surf，测试批量深度
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.surf_service import SurfService

# Scout G 的真实返回
SCOUT_G_TABLE = """| 项目名称 | Twitter | 赛道 | KOL 关注数 | 代币 | 阶段 | 近期催化剂 |
|----------|---------|------|------------|------|------|--------------| 
| Taiko | @taiko_xyz | L2 | 1 | $TKO | 测试网 | 2025 Q1 DAO测试网部署 |
| Parallel | @theparallel_io | GameFi | 1 | $PRL | 已上线 | 2025生态扩展合作 |
| Aleph Zero | @Aleph__Zero | Infra | 2 | $AZERO | 已上线 | 2026网络升级发布 |
| Chiliz | @chiliz | RWA | 2 | $CHZ | 已上线 | 2026-02 2030 SportFi宣言发布 |
| Kaito AI | @kaitoai | AI | 1 | $KAITO | 已上线 | 2025 TGE后增长加速 |
| Kyber Network | @KyberNetwork | DeFi | 1 | $KNC | 已上线 | 2025 TVL稳定增长 |
| Dicey | @diceyhq | GameFi | 2 | 无 | 已上线 | 2026 Magic Eden合作上线 |
| Giza | @gizatechxyz | Infra | 2 | $GIZA | TGE前 | 2025代理经济启动 |"""

PROMPTS = {
    "G": {
        "label": "批量增强表格",
        "prompt": (
            "以下是从 leak.me KOL Tracker 发现的 8 个近期热门项目：\n\n"
            f"{SCOUT_G_TABLE}\n\n"
            "请对每个项目做深度调研，输出增强版表格：\n"
            "| 项目 | 赛道 | 代币(验证) | 阶段(验证) | 融资总额 | 核心团队 | 关键时间节点 |\n\n"
            "字段说明：\n"
            "- 代币(验证): 验证代币符号是否正确，纠正错误的\n"
            "- 阶段(验证): 验证当前真实阶段\n"
            "- 融资总额: 已融资金额 + 领投方\n"
            "- 核心团队: 创始人姓名+一句话背景\n"
            "- 关键时间节点: 最近和即将到来的重要事件（TGE/空投/主网/上所/融资/产品发布），注明日期\n\n"
            "保持表格格式，每个项目一行。"
        ),
    },
    "H": {
        "label": "批量信息卡+时间线",
        "prompt": (
            "以下是从 leak.me KOL Tracker 发现的 8 个近期热门项目：\n\n"
            f"{SCOUT_G_TABLE}\n\n"
            "对每个项目深度调研，每个项目输出：\n\n"
            "### 项目名称\n"
            "定位：一句话。融资：金额+领投方。团队：创始人+背景。\n"
            "时间线：关键事件（TGE/空投/测试网/主网/上所/产品发布），注明日期。\n\n"
            "每个项目控制在 3-5 行，查不到的信息跳过。"
        ),
    },
}

OUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "prompt_test" / "strategist" / "round3"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run(pid, label, prompt):
    print(f"\n{'='*60}")
    print(f"🧪 Round 3 | [{pid}] {label}")
    print(f"{'='*60}")
    print(f"📝 Prompt 前 200 字:\n{prompt[:200]}...\n")
    print("⏳ 调用 Surf API（批量模式，可能较慢）...")

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

    if status != 200:
        print(f"❌ 错误: {result.get('error', '')[:200]}")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUT_DIR / f"strat_{pid}_{ts}.md"

    report = (
        f"# 🧪 策略官 Round 3 | [{pid}] {label}\n\n"
        f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
        f"> 耗时: {elapsed:.0f}s  \n"
        f"> 内容长度: {len(content)} 字符  \n\n"
        f"---\n\n"
        f"## 📝 Prompt\n\n```\n{prompt}\n```\n\n"
        f"---\n\n"
        f"## 📥 Surf 完整返回\n\n{content}\n\n"
    )

    filepath.write_text(report, encoding="utf-8")
    print(f"📁 已保存: {filepath}")


if __name__ == "__main__":
    for pid, p in PROMPTS.items():
        run(pid, p["label"], p["prompt"])
    print(f"\n📂 结果目录: {OUT_DIR}")
