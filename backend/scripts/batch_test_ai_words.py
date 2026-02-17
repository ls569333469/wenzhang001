"""
P25 批量测试脚本 v2：10次 short_article 生成 → 检查 AI 词汇
两阶段流程：/analyze → 获取 plans → /generate → 获取 content
"""
import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
from pathlib import Path
from collections import Counter

# --- Config ---
API_BASE = "http://localhost:8000"
NUM_RUNS = 7
MODE = "short_article"
MODEL = "doubao-seed-2-0-lite-260215"

# P25 禁止词清单
FORBIDDEN = {
    "高频AI商业词汇": [
        "赛道", "生态", "布局", "核心竞争力", "底层逻辑", "驱动",
        "破局", "差异化", "治理错位", "迫在眉睫", "技术迭代"
    ],
    "AI伪口语句式": ["说白了", "从来都不是", "本质是"],
    "AI造词": ["自循环协作网络", "价值兑现路径", "隐性的网络扩张"],
    "中频AI词": [
        "圈层", "触达", "链接", "精准", "适配", "核心价值", "顶层设计",
        "战略布局", "赋能", "解锁", "精准匹配"
    ],
    "废话文学": [
        "让我们拭目以待", "后续值得关注", "时间会给出答案",
        "这不禁让人思考", "值得深思", "引人深省",
        "机遇与挑战并存", "众所周知", "综上所述"
    ],
    "屏蔽词": ["庄哥", "庄家", "币圈", "韭菜", "割韭菜", "凸显", "至关重要"],
    "标点禁止": ["——", "；"]
}


def load_api_key():
    config_path = Path(__file__).parent.parent / "config" / "user_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg.get("api_keys", {}).get("doubao", "")
    return os.getenv("VOLC_API_KEY", "")


def check_forbidden(text: str) -> list:
    hits = []
    for category, words in FORBIDDEN.items():
        for word in words:
            count = text.count(word)
            if count > 0:
                hits.append((category, word, count))
    return hits


def make_agent_config(api_key):
    cfg = {"provider": "volcengine", "model_id": MODEL, "api_key": api_key}
    return {
        "strategist": cfg.copy(),
        "writer": cfg.copy(),
        "critic": cfg.copy(),
        "polisher": cfg.copy()
    }


async def parse_sse(resp):
    """Parse SSE stream, return list of events"""
    events = []
    buffer = ""
    async for chunk in resp.content:
        buffer += chunk.decode("utf-8")
        while "\n\n" in buffer:
            event_str, buffer = buffer.split("\n\n", 1)
            for line in event_str.split("\n"):
                if line.startswith("data: "):
                    try:
                        events.append(json.loads(line[6:]))
                    except json.JSONDecodeError:
                        pass
    # remaining
    for line in buffer.split("\n"):
        if line.startswith("data: "):
            try:
                events.append(json.loads(line[6:]))
            except json.JSONDecodeError:
                pass
    return events


async def fetch_materials(session):
    """获取素材"""
    async with session.get(f"{API_BASE}/materials/list?page=1&page_size=20") as resp:
        if resp.status != 200:
            return []
        data = await resp.json()
        items = data.get("items", [])
        valid = []
        for m in items:
            text = m.get("content") or m.get("title") or ""
            if len(text) > 30:
                valid.append({"title": (m.get("title") or "")[:40], "text": text})
        return valid


async def run_single_generation(session, material_text: str, run_id: int, api_key: str):
    """Two-phase: /analyze → get plans → /generate → get content"""
    agent_config = make_agent_config(api_key)
    api_config = {"provider": "volcengine", "model_id": MODEL, "api_key": api_key}
    start = time.time()

    # Phase 1: /analyze
    analyze_payload = {
        "input": material_text[:2000],
        "mode": MODE,
        "style": "mimeng",
        "retention_level": 3,
        "temperature": 0.88,
        "narrative_type": "project_review",
        "references": [],
        "api_config": api_config,
        "agent_config": agent_config
    }

    try:
        async with session.post(
            f"{API_BASE}/analyze", json=analyze_payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            if resp.status != 200:
                return {"run_id": run_id, "error": f"analyze HTTP {resp.status}", "content": ""}

            events = await parse_sse(resp)

        # Find analysis_result with auto_proceed
        analysis_payload = None
        for ev in events:
            if ev.get("type") == "analysis_result":
                analysis_payload = ev.get("payload", {})
                break

        if not analysis_payload:
            return {"run_id": run_id, "error": "No analysis_result event", "content": ""}

        # Phase 2: /generate with selected_option = full analysis payload (auto_proceed)
        generate_payload = {
            "input": material_text[:2000],
            "mode": MODE,
            "style": "mimeng",
            "retention_level": 3,
            "narrative_type": "project_review",
            "references": [],
            "selected_option": analysis_payload,
            "info_anchors": analysis_payload.get("info_anchors"),
            "api_config": api_config,
            "agent_config": agent_config
        }

        async with session.post(
            f"{API_BASE}/generate", json=generate_payload,
            timeout=aiohttp.ClientTimeout(total=150)
        ) as resp2:
            if resp2.status != 200:
                return {"run_id": run_id, "error": f"generate HTTP {resp2.status}", "content": ""}

            events2 = await parse_sse(resp2)

        # Extract final content
        content = ""
        for ev in events2:
            if ev.get("type") == "content_preview":
                content = ev.get("payload", "")
            elif ev.get("type") == "final_result":
                content = ev.get("payload", content)

        duration = round(time.time() - start, 1)
        return {
            "run_id": run_id,
            "content": content,
            "duration": duration,
            "char_count": len(content)
        }

    except asyncio.TimeoutError:
        return {"run_id": run_id, "error": "Timeout", "content": ""}
    except Exception as e:
        return {"run_id": run_id, "error": str(e), "content": ""}


async def main():
    api_key = load_api_key()
    if not api_key:
        print("❌ 未找到 API Key")
        return

    print(f"🚀 P25 批量测试 v2 - {NUM_RUNS}次 {MODE} 生成")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 模型: {MODEL}")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        materials = await fetch_materials(session)
        if not materials:
            print("❌ 没有可用素材")
            return
        print(f"📦 {len(materials)} 条素材就绪\n")

        results = []
        for i in range(NUM_RUNS):
            mat = materials[i % len(materials)]
            print(f"[{i+1}/{NUM_RUNS}] {mat['title']}...", end="", flush=True)

            result = await run_single_generation(session, mat["text"], i + 1, api_key)

            if result.get("error"):
                print(f" ❌ {result['error']}")
            else:
                hits = check_forbidden(result["content"])
                hit_str = f"⚠️{len(hits)}词: {','.join(h[1] for h in hits)}" if hits else "✅清洁"
                print(f" {result['char_count']}字/{result['duration']}s {hit_str}")

            results.append(result)

    # === 生成报告 ===
    report_lines = [
        f"# P25 批量测试报告\n",
        f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 模式: {MODE} | 次数: {NUM_RUNS} | 模型: {MODEL}\n",
        "---\n"
    ]

    total_hits = Counter()
    all_hits_detail = []
    success_count = 0

    for r in results:
        rid = r["run_id"]
        content = r.get("content", "")
        report_lines.append(f"## 第 {rid} 次生成\n")

        if r.get("error"):
            report_lines.append(f"❌ **错误**: {r['error']}\n\n---\n")
            continue

        success_count += 1
        report_lines.append(f"- 字数: {r['char_count']} | 耗时: {r['duration']}s\n")
        report_lines.append(f"### 内容\n\n{content}\n")

        hits = check_forbidden(content)
        report_lines.append(f"\n### AI词汇检查\n")
        if hits:
            for cat, word, count in hits:
                report_lines.append(f"- ⚠️ **{word}** ({cat}) ×{count}")
                total_hits[word] += count
                all_hits_detail.append((rid, cat, word))
        else:
            report_lines.append("✅ 无禁止词命中\n")
        report_lines.append("\n---\n")

    # 总结
    report_lines.append(f"\n## 📊 总体统计\n")
    report_lines.append(f"- 成功: {success_count}/{NUM_RUNS}")
    report_lines.append(f"- 总禁止词命中: {sum(total_hits.values())} 次\n")

    if total_hits:
        report_lines.append("### 命中排行\n\n| 词汇 | 命中次数 |\n|---|---|")
        for word, count in total_hits.most_common():
            report_lines.append(f"| {word} | {count} |")

        report_lines.append("\n### 每轮命中详情\n\n| 轮次 | 类别 | 词汇 |\n|---|---|---|")
        for rid, cat, word in all_hits_detail:
            report_lines.append(f"| {rid} | {cat} | {word} |")
    else:
        report_lines.append("🎉 **零命中！所有生成内容均通过 P25 检查**\n")

    output_path = Path(__file__).parent.parent / "reports" / "batch_test_results.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n{'='*60}")
    print(f"📝 报告: {output_path}")
    print(f"✅ 成功: {success_count}/{NUM_RUNS}")
    print(f"⚠️ 总命中: {sum(total_hits.values())} 次")
    if total_hits:
        print(f"   Top: {', '.join(f'{w}({c})' for w, c in total_hits.most_common(5))}")


if __name__ == "__main__":
    asyncio.run(main())
