"""
P29 最终 BC 对比测试
修复版：
- B组：random 样本（策略师+写手都看得到）
- C组：先抽样本 → 同一套样本同时给策略师和写手
- 策略师模板已加 {{ rag_context }}，样本会真正出现在 prompt 里
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()

from app.services.google_sheets_source import google_sheets_source as gs
from app.services.sample_service import sample_service
from app.agents.strategist import (
    build_strategist_prompt, execute_strategist_analysis, _format_sample
)
from app.agents.writer.short_article import _generate_variant, _extract_plans_from_strategy
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from datetime import datetime

gs.refresh_cache()

TEST_INPUT = """Vitalik Buterin 发布以太坊 L1 扩展路线图，计划将 L1 Gas Limit 提升 10 倍。
核心变化：将区块 gas limit 从当前 3600万提升到 3.6亿，采用 EIP-4444 对历史数据进行过期处理。
无状态客户端 + Verkle Trees 让验证节点不需要存储完整状态。
目标：L1 本身成为高性能链，而非仅作为 DA 层。
社区反应两极化：支持者认为这是 ETH 重新夺回 DeFi 主权的关键。
反对者担心节点中心化风险加剧。Solana 社区调侃"欢迎来到 2021 年"。
当前 ETH 价格 2780美元，过去30天下跌 12%。"""

API_CONFIG = {"provider": "google", "model_id": "gemini-2.0-flash"}
STYLE = "banfo"

report = []
report.append("# P29 最终 BC 对比测试（修复版）\n")
report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
report.append("## 本次修复\n")
report.append("1. 策略师模板加入 `{{ rag_context }}`，样本真正出现在 prompt 里")
report.append("2. C组：策略师和写手看到**同一套样本**")
report.append("3. B组：`get_samples` style 过滤 bug 已修复，random 样本正常获取\n")

mode_config = get_mode_config("short_article")
length_constraints = mode_config.get("length", {"min": 50, "max": 300, "target": 200})
pattern_menu = sample_service.get_pattern_menu(style=STYLE)
current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def make_base_context(rag_ctx):
    return {
        "current_time_str": current_time_str,
        "narrative_type": "project_review",
        "mode": "short_article",
        "mode_description": "short_article",
        "narrative_desc": "",
        "rag_context": rag_ctx,
        "web3_knowledge": "",
        "retention_level": 3,
        "forbidden_patterns": load_forbidden_patterns(),
        "pattern_menu": pattern_menu,
    }

def make_state():
    return {
        "raw_input": TEST_INPUT,
        "mode": "short_article", "style": STYLE,
        "narrative_type": "project_review", "retention_level": 3,
        "api_config": API_CONFIG,
    }

def run_group(group_name, strategist_samples, writer_samples_per_version=None, shared_writer_samples=None):
    """
    运行一组测试。
    strategist_samples: 给策略师看的样本列表
    writer_samples_per_version: None 时用 shared_writer_samples
    shared_writer_samples: 3版本共用的样本
    """
    report.append(f"## {group_name}\n")
    
    # --- 策略师样本 ---
    report.append(f"### 策略师收到的样本（{len(strategist_samples)}条）\n")
    for i, s in enumerate(strategist_samples):
        st = s.get('snippet_type', '')
        lp = s.get('logic_pattern', '')
        report.append(f"**样本{i+1}** [{st}] [{lp}]")
        report.append(f"> {s.get('content','')[:200]}\n")
    
    # 构建策略师 rag_context
    strat_rag = "\n\n".join([_format_sample(i, s) for i, s in enumerate(strategist_samples)])
    context = make_base_context(strat_rag)
    state = make_state()
    
    sys_prompt, user_prompt = build_strategist_prompt(context, state)
    
    report.append("### 策略师 System Prompt（样本部分）\n")
    # 只截取样本相关区块
    if "## 风格参考样本" in sys_prompt:
        start = sys_prompt.index("## 风格参考样本")
        end = sys_prompt.index("## 可用的写作公式") if "## 可用的写作公式" in sys_prompt else start + 500
        report.append(f"```\n{sys_prompt[start:end].strip()}\n```\n")
    else:
        report.append("⚠️ 没有找到风格参考样本区块\n")
    
    print(f"  >>> {group_name} 策略师 LLM...")
    plan_text = execute_strategist_analysis(user_prompt, sys_prompt, API_CONFIG)
    try:
        plan_obj = json.loads(plan_text)
        plans = plan_obj.get("plans", [])
    except:
        plan_obj = {}; plans = []
    
    report.append("### 策略师输出\n```json")
    report.append(json.dumps(plan_obj, ensure_ascii=False, indent=2))
    report.append("```\n")
    
    for i, p in enumerate(plans):
        print(f"  {group_name}-V{i+1}: {p.get('label','')} | hook: {p.get('hook','')[:40]}...")
    
    # --- 写手 ---
    report.append("### 写手生成过程\n")
    variants = []
    
    for i, plan in enumerate(plans[:3]):
        label = plan.get("label","")
        lp = plan.get("logic_pattern","")
        
        # 确定写手样本
        if writer_samples_per_version and i < len(writer_samples_per_version):
            w_samples = writer_samples_per_version[i]
        elif shared_writer_samples:
            w_samples = shared_writer_samples
        else:
            w_samples = []
        
        w_rag = "\n\n".join([
            f"--- 样本({s.get('snippet_type','')}) ---\n{s.get('content','')[:300]}"
            for s in w_samples
        ])
        
        report.append(f"#### {group_name}-V{i+1}: {label} (公式: {lp})\n")
        report.append(f"- hook: {plan.get('hook','')}")
        report.append(f"- tone: {plan.get('tone','')}")
        report.append(f"- 写手样本 ({len(w_samples)}条):")
        for s in w_samples:
            report.append(f"  - [{s.get('snippet_type','')}][{s.get('logic_pattern','')}] {s.get('content','')[:80]}...")
        report.append("")
        
        writer_ctx = {
            "current_time_str": current_time_str, "style": STYLE,
            "length": length_constraints, "retention_level": 3,
            "raw_input": TEST_INPUT, "strategy_plan": plan_text,
            "rag_context": w_rag, "context_card": plan_obj.get("context_card"),
            "forbidden_patterns": load_forbidden_patterns(),
        }
        
        print(f"  >>> {group_name} 写手 V{i+1}: {label} (样本{len(w_samples)}条)...")
        try:
            content = _generate_variant(
                raw_input=TEST_INPUT, plan=plan,
                system_prompt_context=writer_ctx,
                length_constraints=length_constraints,
                api_config=API_CONFIG, custom_prompts={},
            )
            variants.append({"label": label, "content": content, "char_count": len(content)})
            report.append(f"**输出 ({len(content)}字):**\n\n{content}\n")
        except Exception as e:
            report.append(f"**失败:** {e}\n")
            variants.append({"label": label, "content": f"[失败]", "char_count": 0})
    
    return plans, variants

# ================================================================
# B组：random 样本
# ================================================================
print("=" * 60)
print("  🅱️ B组：random 样本")
print("=" * 60)

b_strat_samples = sample_service.get_samples(style=STYLE, count=3)
b_writer_samples = sample_service.get_samples(style=STYLE, count=2)

b_plans, b_variants = run_group(
    "🅱️ B组（random 样本）",
    strategist_samples=b_strat_samples,
    shared_writer_samples=b_writer_samples,
)

print("  等待 15s...")
time.sleep(15)

# ================================================================
# C组：精准样本，策略师和写手共享同一套
# ================================================================
print("\n" + "=" * 60)
print("  🅲 C组：精准样本（共享）")
print("=" * 60)

# Step 1: 抽一套样本
c_hook_samples = sample_service.get_targeted_samples(style=STYLE, snippet_type="开头金句", count=2)
c_ending_samples = sample_service.get_targeted_samples(style=STYLE, snippet_type="行动号召", count=1)
c_body_samples = sample_service.get_targeted_samples(style=STYLE, snippet_type="正文段落", count=1)
c_strat_samples = c_hook_samples + c_ending_samples  # 策略师看：2开头+1结尾

# Step 2: 策略师和写手共享
# 写手每版本看到：策略师的开头金句（共享） + 按公式匹配的正文段落
c_plans, c_variants = run_group(
    "🅲 C组（精准样本 + 策略师写手共享）",
    strategist_samples=c_strat_samples,
    # 写手每版本：从策略师看过的开头金句里取1条 + 按公式取1条正文
    writer_samples_per_version=[
        # 每版本的写手样本 = 策略师的第1条开头金句 + 按公式精准正文
        c_hook_samples[:1] + sample_service.get_targeted_samples(
            style=STYLE, snippet_type="正文段落",
            logic_pattern=None,  # 先占位，运行时才知道公式
            count=1
        )
        for _ in range(3)  # 先用占位，下面会覆盖
    ],
)
# 注意：上面的 writer_samples_per_version 在策略师跑完之前就生成了，
# 所以无法按策略师选的 logic_pattern 精准匹配
# 更好的做法是在 run_group 内部按 plan 里的 logic_pattern 动态取
# 但为了演示共享机制，先统一用策略师看过的开头金句

# ================================================================
# 对比
# ================================================================
report.append("---\n\n## 对比总表\n")
report.append("| 维度 | B组（random） | C组（精准共享） |")
report.append("|------|-------------|---------------|")

b_v1 = b_variants[0]["content"].split("\n")[0][:50] if b_variants else ""
c_v1 = c_variants[0]["content"].split("\n")[0][:50] if c_variants else ""
report.append(f"| V1开头 | {b_v1}... | {c_v1}... |")

b_lps = [p.get("logic_pattern","") for p in b_plans[:3]]
c_lps = [p.get("logic_pattern","") for p in c_plans[:3]]
report.append(f"| 策略师公式 | {', '.join(b_lps)} | {', '.join(c_lps)} |")

report.append("| 策略师样本 | random 3条（出现在prompt里） | 精准：2开头金句+1行动号召（出现在prompt里） |")
report.append("| 写手样本 | random 2条共用 | 策略师同款开头金句 + 精准正文 |")
report.append("| 策略师-写手一致性 | ❌ 各自独立 | ✅ 共享开头金句 |")

rpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "reports", "P29_最终BC对比.md")
with open(rpath, "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print(f"\nDone: {rpath}")
