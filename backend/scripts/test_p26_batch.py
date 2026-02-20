"""
P26 批量测试脚本：短篇模式完整流水线
通过 HTTP API 调用 /analyze → /generate 完整流程
测试 10 篇素材，监控每个阶段耗时，生成报告
"""

import os
import sys
import json
import time
import re
import requests
from datetime import datetime

# ============================================
# 配置
# ============================================
API_BASE = "http://localhost:8000"
MODE = "short_article"
TIMEOUT = 600  # 单次请求超时 10 分钟（放长以免失败）

# ============================================
# 10 条测试素材
# ============================================
TEST_MATERIALS = [
    "BTC 跌破 65,000 美元，截至 2 月 6 日 13:00 (UTC+8)，BTC 报约 64,239.2 美元，24 小时跌幅 9.50%；ETH 跌破 1,900 美元，报约 1,890.17 美元，24 小时下跌 9.80%。24小时内全球清算额达到约17亿美元，其中约15亿美元为多头头寸。",
    "BitMEX 联合创始人 Arthur Hayes 发文称，近期比特币下跌可能主要源于围绕 IBIT 结构性产品的交易商对冲行为。他指出，银行发行的相关结构性产品在市场波动时会触发交易商卖出比特币现货进行对冲。",
    "Crypto.com 创始人 Kris Marszalek 以约 7000 万美元收购域名 AI.com，成为目前公开披露的史上最高价域名交易。",
    "Arkham 表示，Tesla 目前仍持有约 1.15 万枚 BTC，其在 2022 年 LUNA 崩盘期间已出售大部分比特币，仅保留最初购入量约 20%。",
    "彭博 ETF 分析师 Eric Balchunas 发推表示，美东时间 2 月 5 日，iShares Bitcoin Trust（IBIT）在价格单日下跌 13% 的情况下成交额达约 100 亿美元，刷新上市以来成交量纪录。",
]


def parse_sse_stream(resp):
    """从 SSE 流式响应中解析事件（使用 stream=True + iter_lines）"""
    events = []
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                events.append(data)
            except json.JSONDecodeError:
                pass
    return events


def call_analyze(material):
    """调用 /analyze 策略官，返回策略 JSON"""
    payload = {
        "input": material,
        "mode": MODE,
        "style": "auto",
        "api_config": {"provider": "volcengine"},
    }
    resp = requests.post(
        f"{API_BASE}/analyze",
        json=payload,
        stream=True,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"

    events = parse_sse_stream(resp)
    # 提取 analysis_result
    for ev in events:
        if ev.get("type") == "analysis_result":
            return ev.get("payload", {})
        if ev.get("type") == "error":
            raise RuntimeError(f"Analyze error: {ev.get('message')}")
    raise RuntimeError("No analysis_result received")


def call_generate(material, strategy_data):
    """调用 /generate 写作流水线，返回最终内容和思考步骤"""
    # P25 短篇模式：传完整 strategy_data 作为 selected_option
    # node_strategist 检查 "plans" in plan_data 来决定是否保留 plans 数组
    # 如果只传 plans[0]（单个方案），writer 的 _extract_plans_from_strategy 会找不到 plans 键
    selected_option = strategy_data  # 传完整策略数据，保留 plans 数组

    payload = {
        "input": material,
        "mode": MODE,
        "style": "auto",
        "selected_option": selected_option,
        "info_anchors": strategy_data.get("info_anchors"),
        "api_config": {"provider": "volcengine"},
    }
    resp = requests.post(
        f"{API_BASE}/generate",
        json=payload,
        stream=True,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"

    events = parse_sse_stream(resp)

    # 收集信息
    final_content = ""
    draft_preview = ""
    agent_steps = []
    errors = []

    for ev in events:
        evt_type = ev.get("type")
        if evt_type == "final_result":
            final_content = ev.get("payload", "")
        elif evt_type == "content_preview":
            draft_preview = ev.get("payload", "")
        elif evt_type == "agent_update":
            agent_steps.append({
                "agent": ev.get("step"),
                "status": ev.get("status"),
                "logs": ev.get("logs", []),
            })
        elif evt_type == "error":
            errors.append(ev.get("message", ""))

    return {
        "final_content": final_content,
        "draft_preview": draft_preview,
        "agent_steps": agent_steps,
        "errors": errors,
    }


def check_forbidden_words(text):
    """检查禁用词"""
    forbidden = [
        "赛道", "生态", "布局", "底层逻辑", "核心竞争力",
        "破局", "赋能", "差异化",
        "庄哥", "庄家", "币圈", "韭菜", "割韭菜",
        "——",  # 破折号
    ]
    hits = []
    for word in forbidden:
        if word in text:
            hits.append(word)
    return hits


def run_batch():
    """主测试流程"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*70}")
    print(f"  P26 短篇完整流水线批量测试")
    print(f"  模式: {MODE}  |  素材: {len(TEST_MATERIALS)} 篇")
    print(f"  超时: {TIMEOUT}s  |  开始: {timestamp}")
    print(f"{'='*70}\n")

    results = []
    errors_list = []

    for i, material in enumerate(TEST_MATERIALS, 1):
        print(f"\n{'─'*60}")
        print(f"  📝 素材 #{i}/{len(TEST_MATERIALS)}")
        print(f"  输入: {material[:80]}...")
        print(f"{'─'*60}")

        record = {
            "id": i,
            "input": material,
            "input_preview": material[:100],
        }

        try:
            # ===== Step 1: Analyze (策略官) =====
            print(f"  ⏳ [1/2] 策略官分析中...")
            t0 = time.time()
            strategy_data = call_analyze(material)
            t_analyze = time.time() - t0
            print(f"  ✅ 策略官完成 ({t_analyze:.1f}s)")

            # 提取策略信息
            plans = strategy_data.get("plans", strategy_data.get("options", []))
            plan_labels = [p.get("label", "?") for p in plans]
            print(f"     方案: {plan_labels}")

            record["strategy_time_s"] = round(t_analyze, 1)
            record["strategy_plans"] = plan_labels
            record["core_fact"] = strategy_data.get("core_fact", "")

            # ===== Step 2: Generate (写手 + 润色) =====
            print(f"  ⏳ [2/2] 写手+润色中...")
            t1 = time.time()
            gen_result = call_generate(material, strategy_data)
            t_generate = time.time() - t1
            print(f"  ✅ 创作完成 ({t_generate:.1f}s)")

            final = gen_result["final_content"]
            draft = gen_result["draft_preview"]

            # 用最终内容；如果没有则用草稿
            content = final or draft
            char_count = len(content)

            # 禁用词检查
            forbidden_hits = check_forbidden_words(content)

            record["generate_time_s"] = round(t_generate, 1)
            record["total_time_s"] = round(t_analyze + t_generate, 1)
            record["output"] = content
            record["char_count"] = char_count
            record["in_range"] = 50 <= char_count <= 300
            record["forbidden_hits"] = forbidden_hits
            record["agent_steps"] = gen_result["agent_steps"]
            record["status"] = "✅ 成功"

            # 输出预览
            range_icon = "✅" if record["in_range"] else "❌"
            forbidden_icon = "✅" if not forbidden_hits else f"❌ {forbidden_hits}"
            print(f"  📊 字数: {char_count} {range_icon} | 禁词: {forbidden_icon}")
            print(f"  ⏱  总耗时: {record['total_time_s']}s")
            print(f"  内容预览: {content[:120]}...")

            results.append(record)

        except Exception as e:
            import traceback
            t_total = time.time() - t0 if 't0' in dir() else 0
            record["status"] = f"❌ 失败: {str(e)[:200]}"
            record["total_time_s"] = round(t_total, 1)
            record["error"] = str(e)
            errors_list.append(record)
            print(f"  ❌ 失败: {e}")
            traceback.print_exc()

    # ============================================
    # 汇总报告
    # ============================================
    total = len(TEST_MATERIALS)
    success = len(results)
    failed = len(errors_list)

    print(f"\n\n{'='*70}")
    print(f"  📊 P26 批量测试汇总报告")
    print(f"{'='*70}")
    print(f"  总测试: {total}  |  成功: {success}  |  失败: {failed}")

    if results:
        counts = [r["char_count"] for r in results]
        times = [r["total_time_s"] for r in results]
        in_range_count = sum(1 for r in results if r["in_range"])
        forbidden_count = sum(1 for r in results if r.get("forbidden_hits"))
        analyze_times = [r["strategy_time_s"] for r in results]
        generate_times = [r["generate_time_s"] for r in results]

        print(f"\n  📏 字数统计:")
        print(f"    平均: {sum(counts)/len(counts):.0f} 字")
        print(f"    最短: {min(counts)} 字  |  最长: {max(counts)} 字")
        print(f"    合格率: {in_range_count}/{success} ({in_range_count/success*100:.0f}%)")

        print(f"\n  ⏱  耗时统计:")
        print(f"    策略官平均: {sum(analyze_times)/len(analyze_times):.1f}s")
        print(f"    写手+润色平均: {sum(generate_times)/len(generate_times):.1f}s")
        print(f"    总平均: {sum(times)/len(times):.1f}s")
        print(f"    最快: {min(times):.1f}s  |  最慢: {max(times):.1f}s")

        print(f"\n  🚫 禁用词统计:")
        print(f"    含禁词: {forbidden_count}/{success} ({forbidden_count/success*100:.0f}%)")
        if forbidden_count:
            for r in results:
                if r.get("forbidden_hits"):
                    print(f"    #{r['id']}: {r['forbidden_hits']}")

    if errors_list:
        print(f"\n  ❌ 失败列表:")
        for e in errors_list:
            print(f"    #{e['id']}: {e.get('error', '未知')[:120]}")

    # ============================================
    # 保存 JSON 报告
    # ============================================
    report = {
        "test_name": "P26 短篇完整流水线批量测试",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "mode": MODE,
            "timeout_s": TIMEOUT,
            "total_materials": total,
        },
        "summary": {
            "total": total,
            "success": success,
            "failed": failed,
            "avg_char_count": round(sum(counts)/len(counts), 0) if results else 0,
            "min_char_count": min(counts) if results else 0,
            "max_char_count": max(counts) if results else 0,
            "in_range_rate": f"{in_range_count}/{success}" if results else "N/A",
            "avg_total_time_s": round(sum(times)/len(times), 1) if results else 0,
            "avg_strategy_time_s": round(sum(analyze_times)/len(analyze_times), 1) if results else 0,
            "avg_generate_time_s": round(sum(generate_times)/len(generate_times), 1) if results else 0,
            "forbidden_word_count": forbidden_count if results else 0,
        },
        "results": results,
        "errors": errors_list,
    }

    # 保存 JSON
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(report_dir, exist_ok=True)
    json_path = os.path.join(report_dir, "P26_batch_test_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 JSON 报告: {json_path}")

    # 保存 Markdown 报告
    md_path = os.path.join(report_dir, "P26_batch_test_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# P26 短篇完整流水线批量测试报告\n\n")
        f.write(f"> 测试时间: {timestamp}\n\n")
        f.write(f"## 概要\n\n")
        f.write(f"| 指标 | 值 |\n")
        f.write(f"|------|----|\n")
        f.write(f"| 测试总数 | {total} |\n")
        f.write(f"| 成功 | {success} |\n")
        f.write(f"| 失败 | {failed} |\n")
        if results:
            f.write(f"| 平均字数 | {sum(counts)/len(counts):.0f} |\n")
            f.write(f"| 字数范围 | {min(counts)} ~ {max(counts)} |\n")
            f.write(f"| 字数合格率 (50-300) | {in_range_count}/{success} ({in_range_count/success*100:.0f}%) |\n")
            f.write(f"| 策略官平均耗时 | {sum(analyze_times)/len(analyze_times):.1f}s |\n")
            f.write(f"| 写手+润色平均耗时 | {sum(generate_times)/len(generate_times):.1f}s |\n")
            f.write(f"| 总平均耗时 | {sum(times)/len(times):.1f}s |\n")
            f.write(f"| 含禁用词数 | {forbidden_count}/{success} |\n")

        f.write(f"\n---\n\n## 逐篇结果\n\n")
        all_records = results + errors_list
        all_records.sort(key=lambda x: x["id"])
        for r in all_records:
            f.write(f"### #{r['id']}\n\n")
            f.write(f"**素材:** {r['input'][:120]}...\n\n")
            f.write(f"**状态:** {r['status']}\n\n")
            if "output" in r:
                f.write(f"**字数:** {r['char_count']}  ")
                f.write(f"**合格:** {'✅' if r.get('in_range') else '❌'}  ")
                f.write(f"**禁词:** {r.get('forbidden_hits', [])}\n\n")
                f.write(f"**策略官:** {r.get('strategy_time_s', '?')}s  ")
                f.write(f"**写手+润色:** {r.get('generate_time_s', '?')}s  ")
                f.write(f"**总耗时:** {r.get('total_time_s', '?')}s\n\n")
                f.write(f"**方案:** {r.get('strategy_plans', [])}\n\n")
                f.write(f"**核心事实:** {r.get('core_fact', '')}\n\n")
                f.write(f"**输出内容:**\n\n")
                f.write(f"```\n{r['output']}\n```\n\n")
            elif "error" in r:
                f.write(f"**错误:** {r['error']}\n\n")
            f.write(f"---\n\n")

    print(f"  📝 Markdown 报告: {md_path}")

    # 输出完整内容供审阅
    print(f"\n\n{'='*70}")
    print(f"  📝 全部输出内容")
    print(f"{'='*70}")
    for r in results:
        print(f"\n{'─'*50}")
        print(f"#{r['id']} ({r['char_count']}字) [{r['total_time_s']}s]")
        if r.get("forbidden_hits"):
            print(f"⚠️ 禁词: {r['forbidden_hits']}")
        print(f"{'─'*50}")
        print(r["output"])

    return results, errors_list


if __name__ == "__main__":
    run_batch()
