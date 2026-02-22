"""P29 B组补测：IoTex素材 + random 样本"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()

from app.services.google_sheets_source import google_sheets_source as gs
from app.services.sample_service import sample_service
from app.agents.strategist import build_strategist_prompt, execute_strategist_analysis, _format_sample
from app.agents.writer.short_article import _generate_variant
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from datetime import datetime

gs.refresh_cache()

TEST_INPUT = """IoTex在 X 平台发布此前私钥泄露黑客攻击事件的更新进展，其中表示团队已控制相关安全事件，IoTeX Chain 正在加固安全，目前确认此次攻击损失金额约 200 万美元，涉及 USDC、USDT、IOTX 及 WBTC 等资产。

据悉，此次为专业攻击者策划已久的复杂攻击行动，目标涉及多个区块链网络，IoTeX 正与交易所及执法机构密切合作，尝试冻结被盗资金并推进调查与追回工作。链上运行及充值功能将在完成安全升级后 24–48 小时内恢复，同时还承诺后续将保持透明披露进展。"""

API_CONFIG = {"provider": "google", "model_id": "gemini-2.0-flash"}
STYLE = "banfo"

report = []
report.append("# P29 B组测试 — IoTex素材（random样本）\n")
report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

mode_config = get_mode_config("short_article")
length_constraints = mode_config.get("length", {"min": 50, "max": 300, "target": 200})
pattern_menu = sample_service.get_pattern_menu(style=STYLE)
current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# B组：random 样本
b_samples = sample_service.get_samples(style=STYLE, count=3)
b_rag = "\n\n".join([_format_sample(i, s) for i, s in enumerate(b_samples)])

report.append("## 策略师收到的样本（random 3条）\n")
for i, s in enumerate(b_samples):
    report.append(f"**样本{i+1}** [{s.get('snippet_type','')}] [{s.get('logic_pattern','')}]")
    report.append(f"> {s.get('content','')[:200]}\n")

context = {
    "current_time_str": current_time_str,
    "narrative_type": "project_review",
    "mode": "short_article", "mode_description": "short_article",
    "narrative_desc": "", "rag_context": b_rag,
    "web3_knowledge": "", "retention_level": 3,
    "forbidden_patterns": load_forbidden_patterns(),
    "pattern_menu": pattern_menu,
}
state = {
    "raw_input": TEST_INPUT, "mode": "short_article", "style": STYLE,
    "narrative_type": "project_review", "retention_level": 3,
    "api_config": API_CONFIG,
}

sys_prompt, user_prompt = build_strategist_prompt(context, state)

# 截取样本区块
report.append("## 策略师 Prompt 中的样本区块\n")
if "## 风格参考样本" in sys_prompt:
    start = sys_prompt.index("## 风格参考样本")
    end = sys_prompt.index("## 可用的写作公式") if "## 可用的写作公式" in sys_prompt else start + 500
    report.append(f"```\n{sys_prompt[start:end].strip()}\n```\n")

print(">>> B 策略师...")
plan_text = execute_strategist_analysis(user_prompt, sys_prompt, API_CONFIG)
try:
    plan_obj = json.loads(plan_text)
    plans = plan_obj.get("plans", [])
except:
    plan_obj = {}; plans = []

report.append("## 策略师输出\n```json")
report.append(json.dumps(plan_obj, ensure_ascii=False, indent=2))
report.append("```\n")

for i, p in enumerate(plans):
    print(f"  B-V{i+1}: {p.get('label','')} | hook: {p.get('hook','')[:50]}...")

# 写手：random 2条共用
b_writer = sample_service.get_samples(style=STYLE, count=2)
b_w_rag = "\n\n".join([f"--- 样本({s.get('snippet_type','')}) ---\n{s.get('content','')[:300]}" for s in b_writer])

report.append("## 写手收到的样本（random 2条共用）\n")
for i, s in enumerate(b_writer):
    report.append(f"**样本{i+1}** [{s.get('snippet_type','')}] [{s.get('logic_pattern','')}]")
    report.append(f"> {s.get('content','')[:150]}\n")

report.append("## 写手生成过程\n")
for i, plan in enumerate(plans[:3]):
    label = plan.get("label","")
    lp = plan.get("logic_pattern","")
    
    writer_ctx = {
        "current_time_str": current_time_str, "style": STYLE,
        "length": length_constraints, "retention_level": 3,
        "raw_input": TEST_INPUT, "strategy_plan": plan_text,
        "rag_context": b_w_rag, "context_card": plan_obj.get("context_card"),
        "forbidden_patterns": load_forbidden_patterns(),
    }
    
    report.append(f"### V{i+1}: {label} (公式: {lp})\n")
    report.append(f"- hook: {plan.get('hook','')}")
    report.append(f"- tone: {plan.get('tone','')}\n")
    
    print(f"  >>> B 写手 V{i+1}: {label}...")
    try:
        content = _generate_variant(
            raw_input=TEST_INPUT, plan=plan,
            system_prompt_context=writer_ctx,
            length_constraints=length_constraints,
            api_config=API_CONFIG, custom_prompts={},
        )
        report.append(f"**输出 ({len(content)}字):**\n\n{content}\n")
    except Exception as e:
        report.append(f"**失败:** {e}\n")

rpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "reports", "P29_B组_IoTex素材.md")
with open(rpath, "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print(f"\nDone: {rpath}")
