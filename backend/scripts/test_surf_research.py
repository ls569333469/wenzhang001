"""
P31: Surf API 完整投研测试
模拟真实投研流程：用 Surf API 获取项目全维度数据
"""
import os
import sys
import json
import time
import httpx
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SURF_API_KEY = os.getenv("SURF_API_KEY")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"

if not SURF_API_KEY:
    print("ERROR: SURF_API_KEY not found in .env")
    sys.exit(1)

# 输出文件
OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "surf_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def call_surf(model: str, query: str, abilities: list, reasoning: str = "medium", timeout: int = 300):
    """调用 Surf API 并返回结果"""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional crypto research analyst. "
                    "Provide detailed, data-driven analysis with specific numbers, "
                    "metrics, and sources. Use structured formatting with headers and tables. "
                    "Always include: price, market cap, TVL, funding history, team background, "
                    "social sentiment, and key risks. Output in English."
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
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            reasoning_text = data["choices"][0]["message"].get("reasoning", "")
            return {
                "status": 200,
                "content": content,
                "reasoning": reasoning_text,
                "usage": usage,
                "elapsed": elapsed,
                "model": data.get("model", model),
            }
        else:
            return {
                "status": resp.status_code,
                "error": resp.text[:500],
                "elapsed": elapsed,
            }
    except httpx.TimeoutException:
        return {"status": "timeout", "elapsed": time.time() - start}
    except Exception as e:
        return {"status": "error", "error": str(e), "elapsed": time.time() - start}


def save_result(name: str, result: dict):
    """保存结果到文件"""
    filepath = OUTPUT_DIR / f"{name}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Surf API Test: {name}\n\n")
        f.write(f"**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Model**: {result.get('model', 'N/A')}\n\n")
        f.write(f"**Elapsed**: {result.get('elapsed', 0):.1f}s\n\n")
        if result.get("usage"):
            u = result["usage"]
            f.write(f"**Tokens**: prompt={u.get('prompt_tokens', '?')}, "
                    f"completion={u.get('completion_tokens', '?')}, "
                    f"total={u.get('total_tokens', '?')}\n\n")
        f.write("---\n\n")
        if result.get("content"):
            f.write(result["content"])
        elif result.get("error"):
            f.write(f"**ERROR**: {result['error']}")
        else:
            f.write("No content returned.")
    print(f"  -> Saved: {filepath}")


# ===== TEST 1: 项目基本面分析 (MegaETH) =====
print("=" * 60)
print("TEST 1: MegaETH Full Analysis (surf-1.5-instant)")
print("=" * 60)

result1 = call_surf(
    model="surf-1.5-instant",
    query=(
        "Provide a comprehensive analysis of MegaETH including:\n"
        "1. Project overview and technology (real-time L2, EVM-compatible)\n"
        "2. Current price, market cap, FDV\n"
        "3. Complete funding history (all rounds, amounts, lead investors)\n"
        "4. Team background\n"
        "5. Social sentiment (X followers, Mindshare score, bullish/bearish ratio)\n"
        "6. Recent news and developments\n"
        "7. Key risks and catalysts\n"
        "8. One-line investment conclusion"
    ),
    abilities=["search", "evm_onchain", "market_analysis"],
    reasoning="medium",
    timeout=120,
)

print(f"  Status: {result1['status']} ({result1.get('elapsed', 0):.1f}s)")
if result1.get("content"):
    print(f"  Content length: {len(result1['content'])} chars")
    print(f"  Usage: {result1.get('usage', {})}")
save_result("megaeth_analysis", result1)


# ===== TEST 2: Pre-TGE 项目评估 (Surf 官方有的) =====
print("\n" + "=" * 60)
print("TEST 2: Pre-TGE Project Assessment - Sentient (surf-1.5)")
print("=" * 60)

result2 = call_surf(
    model="surf-1.5",
    query=(
        "Provide a Pre-TGE investment assessment of SENTIENT project:\n"
        "1. Project basics: sector, product, milestones\n"
        "2. Funding rounds: amounts, lead investors, valuation terms\n"
        "3. Team: core members, backgrounds\n"
        "4. Token plan: utility, allocation, vesting\n"
        "5. Comparables (5 similar projects): FDV/TVL/revenue multiples\n"
        "6. FDV scenarios: Bear/Base/Bull with methodology\n"
        "7. Exchange listing probability (Binance/Coinbase/OKX)\n"
        "8. Social momentum: mention volume, sentiment, KOL coverage\n"
        "9. Key risks\n"
        "10. Conclusion: Participate/Watch/Avoid + confidence level"
    ),
    abilities=["search", "market_analysis"],
    reasoning="high",
    timeout=300,
)

print(f"  Status: {result2['status']} ({result2.get('elapsed', 0):.1f}s)")
if result2.get("content"):
    print(f"  Content length: {len(result2['content'])} chars")
    print(f"  Usage: {result2.get('usage', {})}")
save_result("sentient_pretge", result2)


# ===== TEST 3: 链上数据查询 (Hyperliquid) =====
print("\n" + "=" * 60)
print("TEST 3: On-chain Data Query - Hyperliquid (surf-1.5-instant)")
print("=" * 60)

result3 = call_surf(
    model="surf-1.5-instant",
    query=(
        "Give me Hyperliquid's key on-chain and market metrics:\n"
        "1. Current price, 24h/7d/30d change\n"
        "2. Daily trading volume (spot + perps)\n"
        "3. TVL and protocol revenue\n"
        "4. Open interest and funding rates\n"
        "5. Active addresses and transaction volume\n"
        "6. Top 5 competitors comparison table (Hyperliquid vs GMX vs dYdX vs Vertex vs Jupiter)"
    ),
    abilities=["search", "evm_onchain", "market_analysis", "calculate"],
    reasoning="medium",
    timeout=120,
)

print(f"  Status: {result3['status']} ({result3.get('elapsed', 0):.1f}s)")
if result3.get("content"):
    print(f"  Content length: {len(result3['content'])} chars")
    print(f"  Usage: {result3.get('usage', {})}")
save_result("hyperliquid_onchain", result3)


# ===== 汇总 =====
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

tests = [
    ("MegaETH Analysis", result1),
    ("Sentient Pre-TGE", result2),
    ("Hyperliquid On-chain", result3),
]

for name, r in tests:
    status = r.get("status", "?")
    elapsed = r.get("elapsed", 0)
    chars = len(r.get("content", ""))
    tokens = r.get("usage", {}).get("total_tokens", "?")
    print(f"  {name}: status={status}, {elapsed:.1f}s, {chars} chars, {tokens} tokens")

print(f"\nResults saved to: {OUTPUT_DIR}")
print("Done!")
