"""
P31: Layer 1 按日期多次搜索测试
- 解除 JSON 输出限制，让 Surf 自由输出表格
- 按日期搜索 @leakmealpha 推文（逐天）
- 合并结果保存为一个文件
"""
import os
import sys
import time
import httpx
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

SURF_API_KEY = os.getenv("SURF_API_KEY")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"

SYSTEM_PROMPT = """你是一位专业的加密货币研究分析师。请用中文回答。
提供结构化的数据，使用表格格式呈现。
重点关注 Web3/Crypto/AI 相关的项目，排除个人账号和非加密实体。"""

OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def call_surf(query: str, timeout: int = 300) -> dict:
    payload = {
        "model": "surf-1.5",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        "stream": False,
        "reasoning_effort": "high",
        "ability": ["search"],
    }
    headers = {
        "Authorization": f"Bearer {SURF_API_KEY}",
        "Content-Type": "application/json",
    }
    start = time.time()
    try:
        with httpx.Client(timeout=timeout, verify=False) as client:
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


# ===== 搜索日期列表 =====
# 按天搜索最近 5 天（可扩展）
DAYS_BACK = 5
dates = []
for i in range(DAYS_BACK):
    d = datetime.now() - timedelta(days=i)
    dates.append(d.strftime("%Y-%m-%d"))

print("=" * 60)
print(f"📡 Layer 1 按日期多次搜索: @leakmealpha + leak.me")
print(f"   搜索范围: {dates[-1]} ~ {dates[0]} ({DAYS_BACK} 天)")
print("=" * 60)

all_results = []

for date_str in dates:
    query = f"""请搜索 X（Twitter）账号 @leakmealpha 在 {date_str} 这一天发布的推文内容。

@leakmealpha 是 leak.me（Crypto KOL Tracker）的官方账号，每天会发布多条推文，内容包括：
- "X KOLs followed in the past Y hours" 类型的榜单
- "trending on CT" 项目推送
- 新 token launch 监控

请从该日期的推文中提取所有被提及的 Web3 和 AI 项目，整理成表格：

| 项目名称 | Twitter 账号 | 类别 | KOL 新关注数 | 热度原因 | 参与机会 |

要求：
- 保留 Web3 项目和 AI 项目，排除个人 KOL、交易所、媒体
- 如果该日期没有找到推文，请说明
- 不要编造数据"""

    print(f"\n  📅 搜索 {date_str}...")
    result = call_surf(query)

    if result["status"] == 200:
        print(f"     ✅ {result['elapsed']:.0f}s, "
              f"{result['usage'].get('total_tokens', '?')} tokens, "
              f"{len(result['content'])} 字符")
        all_results.append({
            "date": date_str,
            "content": result["content"],
            "tokens": result["usage"].get("total_tokens", 0),
            "elapsed": result["elapsed"],
        })
    else:
        print(f"     ❌ 失败: {result.get('error', 'Unknown')}")
        all_results.append({
            "date": date_str,
            "error": result.get("error", "Unknown"),
        })

# ===== 同时搜索 leak.me 网站当前数据 =====
print(f"\n  🌐 搜索 leak.me 网站当前 trending...")
website_query = """请访问和分析 leak.me（https://leak.me/）网站的当前 trending 数据。
leak.me 是一个 Crypto KOL Tracker，追踪加密货币 KOL 的新关注行为。

请帮我获取网站上的所有 trending 项目，整理成表格：

| 项目名称 | Twitter 账号 | 类别 | KOL 新关注数 | KOL 类型 | 热度原因 | 参与机会 |

要求：
- 保留 Web3 项目和 AI 项目，排除个人 KOL、交易所
- 区分 Web3 项目 / AI 项目 / 个人 / 其他"""

website_result = call_surf(website_query)
if website_result["status"] == 200:
    print(f"     ✅ {website_result['elapsed']:.0f}s, "
          f"{website_result['usage'].get('total_tokens', '?')} tokens")

# ===== 合并保存 =====
today = datetime.now().strftime("%Y%m%d")
outfile = OUTPUT_DIR / f"layer1_multiday_{today}.md"

with open(outfile, "w", encoding="utf-8") as f:
    f.write(f"# Layer 1 多日数据采集报告\n\n")
    f.write(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"> **搜索范围**: {dates[-1]} ~ {dates[0]} ({DAYS_BACK} 天)\n")
    f.write(f"> **数据来源**: @leakmealpha 推文 + leak.me 网站\n\n")
    f.write("---\n\n")

    # leak.me 网站数据
    f.write("## 一、leak.me 网站当前 Trending\n\n")
    if website_result["status"] == 200:
        f.write(f"**耗时**: {website_result['elapsed']:.0f}s | "
                f"**Tokens**: {website_result['usage'].get('total_tokens', '?')}\n\n")
        f.write(website_result["content"] + "\n\n")
    else:
        f.write(f"❌ 获取失败: {website_result.get('error', '')}\n\n")
    f.write("---\n\n")

    # 逐天推文数据
    for r in all_results:
        f.write(f"## {r['date']} @leakmealpha 推文\n\n")
        if "error" in r:
            f.write(f"❌ 搜索失败: {r['error']}\n\n")
        else:
            f.write(f"**耗时**: {r['elapsed']:.0f}s | "
                    f"**Tokens**: {r['tokens']}\n\n")
            f.write(r["content"] + "\n\n")
        f.write("---\n\n")

total_tokens = sum(r.get("tokens", 0) for r in all_results)
total_tokens += website_result.get("usage", {}).get("total_tokens", 0)
total_time = sum(r.get("elapsed", 0) for r in all_results)
total_time += website_result.get("elapsed", 0)

print(f"\n{'='*60}")
print(f"📊 统计: {len(all_results)} 天 + 网站, {total_time:.0f}s, {total_tokens:,} tokens")
print(f"💾 已保存: {outfile}")
print("✅ Done!")
