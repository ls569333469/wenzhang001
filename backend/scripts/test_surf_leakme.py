"""
P31: 用 Surf API 分析 @leakmealpha 和 leak.me 24h trending 数据
目标：整理出 Web3 项目列表
"""
import os
import sys
import time
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

OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "surf_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def call_surf(model, query, abilities, reasoning="medium", timeout=180):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一位专业的加密货币研究分析师。请用中文回答。"
                    "提供结构化的数据，使用表格格式呈现。"
                    "重点关注 Web3/Crypto 相关的项目，排除个人账号和非加密实体。"
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
                "reasoning": data["choices"][0]["message"].get("reasoning", ""),
                "usage": data.get("usage", {}),
                "elapsed": elapsed,
            }
        return {"status": resp.status_code, "error": resp.text[:500], "elapsed": elapsed}
    except Exception as e:
        return {"status": "error", "error": str(e), "elapsed": time.time() - start}


# ===== 任务1: 分析 @leakmealpha X账号 =====
print("=" * 60)
print("任务1: 分析 @leakmealpha X账号")
print("=" * 60)

r1 = call_surf(
    model="surf-1.5",
    query=(
        "请分析 X（Twitter）账号 @leakmealpha，包括：\n"
        "1. 账号基本信息（简介、粉丝数、发帖频率）\n"
        "2. 该账号的定位和功能（它是做什么的？）\n"
        "3. 它附属的网站 leak.me 是什么服务？\n"
        "4. 最近发布的内容中提到了哪些 Web3/Crypto 项目？\n"
        "5. 该账号追踪的 KOL 关注行为中，最近 24 小时有哪些项目获得了最多 KOL 新关注？\n\n"
        "请重点罗列出所有提及的 Web3 项目名称和 Twitter 账号。"
    ),
    abilities=["search"],
    reasoning="high",
    timeout=300,
)

print(f"  Status: {r1['status']} ({r1.get('elapsed', 0):.1f}s)")
if r1.get("content"):
    print(f"  Content: {len(r1['content'])} chars")


# ===== 任务2: 获取 leak.me 当前 24h trending =====
print("\n" + "=" * 60)
print("任务2: 获取 leak.me 24h trending Web3 项目")
print("=" * 60)

r2 = call_surf(
    model="surf-1.5",
    query=(
        "请访问和分析 leak.me（https://leak.me/）网站的当前 24 小时 trending 数据。\n"
        "leak.me 是一个 Crypto KOL Tracker，追踪加密货币 KOL（意见领袖）的新关注行为。\n\n"
        "请帮我：\n"
        "1. 获取 leak.me 当前 24h trending 列表中的所有账号\n"
        "2. 对每个账号标注：是 Web3 项目 / 个人账号 / 非加密实体\n"
        "3. 筛选出纯 Web3/Crypto 项目，整理成表格，包含：\n"
        "   - 项目名称\n"
        "   - Twitter 账号\n"
        "   - 项目类别（DeFi/L1/L2/GameFi/AI/Infra 等）\n"
        "   - 24h 新增 KOL 关注数\n"
        "   - KOL 类型分布（Degen/VC/Corporate）\n"
        "   - 简要说明该项目为什么近期受到关注\n\n"
        "请将结果分为两个表格：\n"
        "表1: Web3 项目列表（主要输出）\n"
        "表2: 排除的非项目账号列表（个人/非加密）"
    ),
    abilities=["search"],
    reasoning="high",
    timeout=300,
)

print(f"  Status: {r2['status']} ({r2.get('elapsed', 0):.1f}s)")
if r2.get("content"):
    print(f"  Content: {len(r2['content'])} chars")


# ===== 保存完整结果 =====
outfile = OUTPUT_DIR / "leakme_analysis.md"
with open(outfile, "w", encoding="utf-8") as f:
    f.write(f"# leak.me 热点数据分析报告\n\n")
    f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**数据来源**: Surf API → @leakmealpha + leak.me\n\n")
    f.write("---\n\n")

    f.write("## 一、@leakmealpha 账号分析\n\n")
    f.write(f"**模型**: surf-1.5 | **耗时**: {r1.get('elapsed', 0):.1f}s | **Tokens**: {r1.get('usage', {}).get('total_tokens', '?')}\n\n")
    f.write(r1.get("content", r1.get("error", "无内容")) + "\n\n")
    f.write("---\n\n")

    f.write("## 二、leak.me 24h Trending Web3 项目\n\n")
    f.write(f"**模型**: surf-1.5 | **耗时**: {r2.get('elapsed', 0):.1f}s | **Tokens**: {r2.get('usage', {}).get('total_tokens', '?')}\n\n")
    f.write(r2.get("content", r2.get("error", "无内容")) + "\n\n")

print(f"\n报告已保存: {outfile}")
print("Done!")
