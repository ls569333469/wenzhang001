"""
P31: 测试 Surf API 的社交热点数据获取能力
"""
import os
import sys
import json
import time
import httpx
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SURF_API_KEY = os.getenv("SURF_API_KEY")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"

if not SURF_API_KEY:
    print("ERROR: SURF_API_KEY not found in .env")
    sys.exit(1)


def call_surf(model, query, abilities, reasoning="medium", timeout=120):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a crypto research analyst. Return structured data in JSON or table format when possible."},
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


# ===== TEST 1: 获取当前热点项目 =====
print("=" * 60)
print("TEST 1: 获取当日社交热点项目 (surf-1.5-instant)")
print("=" * 60)

r1 = call_surf(
    model="surf-1.5-instant",
    query=(
        "What are the top 10 trending crypto projects right now based on social media buzz, "
        "KOL attention, and Mindshare? "
        "For each project provide: name, ticker, category, "
        "mindshare score or ranking, recent KOL mentions, "
        "and a one-line summary of why it's trending. "
        "Format as a table."
    ),
    abilities=["search"],
    reasoning="medium",
)
print(f"  Status: {r1['status']} ({r1.get('elapsed', 0):.1f}s)")
if r1.get("content"):
    print(f"  Content ({len(r1['content'])} chars):")
    print(r1["content"][:2000])
    print("..." if len(r1["content"]) > 2000 else "")


# ===== TEST 2: 获取 Surf Hub Trending =====
print("\n" + "=" * 60)
print("TEST 2: Surf Hub 热门项目排名 (surf-1.5-instant)")
print("=" * 60)

r2 = call_surf(
    model="surf-1.5-instant",
    query=(
        "List the top 10 crypto projects by social trending/mindshare score "
        "from Surf's database right now. "
        "Include: project name, sector, mindshare rank, "
        "X followers count, smart followers count, "
        "and 7-day sentiment (bullish/bearish ratio). "
        "Format as a structured table."
    ),
    abilities=["search", "market_analysis"],
    reasoning="medium",
)
print(f"  Status: {r2['status']} ({r2.get('elapsed', 0):.1f}s)")
if r2.get("content"):
    print(f"  Content ({len(r2['content'])} chars):")
    print(r2["content"][:2000])
    print("..." if len(r2["content"]) > 2000 else "")


# ===== TEST 3: 特定行业社交排名 =====
print("\n" + "=" * 60)
print("TEST 3: DeFi 赛道社交热度排名 (surf-1.5-instant)")
print("=" * 60)

r3 = call_surf(
    model="surf-1.5-instant",
    query=(
        "What are the top 10 DeFi projects by social mindshare in the last 7 days? "
        "Include: project name, mindshare rank, X followers, "
        "smart followers, recent key news, and price change 7d. "
        "Format as a table."
    ),
    abilities=["search", "market_analysis"],
    reasoning="medium",
)
print(f"  Status: {r3['status']} ({r3.get('elapsed', 0):.1f}s)")
if r3.get("content"):
    print(f"  Content ({len(r3['content'])} chars):")
    print(r3["content"][:2000])
    print("..." if len(r3["content"]) > 2000 else "")


# ===== 保存完整结果 =====
OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "surf_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_DIR / "surf_social_trending_test.md", "w", encoding="utf-8") as f:
    f.write("# Surf API 社交热点数据测试\n\n")
    f.write(f"**时间**: 2026-02-25\n\n")
    for name, r in [("热点项目", r1), ("Hub 排名", r2), ("DeFi 行业排名", r3)]:
        f.write(f"## {name}\n\n")
        f.write(f"**耗时**: {r.get('elapsed', 0):.1f}s | **Tokens**: {r.get('usage', {}).get('total_tokens', '?')}\n\n")
        f.write(r.get("content", r.get("error", "No content")) + "\n\n---\n\n")

print(f"\n结果已保存到: {OUTPUT_DIR / 'surf_social_trending_test.md'}")
print("Done!")
