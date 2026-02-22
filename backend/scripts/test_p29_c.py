"""P29 C组测试：精准样本匹配"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source as gs
gs.refresh_cache()  # 确保用最新数据

from app.agents.strategist import strategist_agent
from app.agents.writer.short_article import short_article_writer

TEST_INPUT = """Vitalik Buterin 发布以太坊 L1 扩展路线图，计划将 L1 Gas Limit 提升 10 倍。
核心变化：将区块 gas limit 从当前 3600万提升到 3.6亿，采用 EIP-4444 对历史数据进行过期处理。
无状态客户端 + Verkle Trees 让验证节点不需要存储完整状态。
目标：L1 本身成为高性能链，而非仅作为 DA 层。
社区反应两极化：支持者认为这是 ETH 重新夺回 DeFi 主权的关键。
反对者担心节点中心化风险加剧。Solana 社区调侃"欢迎来到 2021 年"。
当前 ETH 价格 2780美元，过去30天下跌 12%。"""

state = {
    "raw_input": TEST_INPUT,
    "mode": "short_article",
    "style": "banfo",
    "narrative_type": "project_review",
    "retention_level": 3,
    "api_config": {"provider": "google", "model_id": "gemini-2.0-flash"},
}

print("=== C组：精准样本匹配 ===\n")
print(">>> Step 1: 策略师（开头金句+行动号召样本）...")
result = strategist_agent(state)
plan_text = result["plan"]

plan_obj = {}
try:
    plan_obj = json.loads(plan_text)
    plans = plan_obj.get("plans", [])
    print(f"core_fact: {plan_obj.get('core_fact','')}")
    for i, p in enumerate(plans):
        print(f"  V{i+1}: {p.get('label','')} | tone:{p.get('tone','')} | logic_pattern:{p.get('logic_pattern','')}")
        print(f"       hook: {p.get('hook','')}")
except Exception as e:
    print(f"Parse error: {e}")
    plans = []

print("\n>>> Step 2: 写手（按logic_pattern精准取样本）...")
state["strategy_json"] = plan_text
writer_result = short_article_writer(state)

# 保存报告
report = ["# P29 C组测试：精准样本匹配\n"]
report.append("## 策略师输出\n```json")
report.append(json.dumps(plan_obj, ensure_ascii=False, indent=2))
report.append("```\n")
report.append("## 写手输出\n")
for v in writer_result.get("variants", []):
    label = v.get("label", v.get("key", ""))
    report.append(f"### {label} ({v['char_count']}字)\n\n{v['content']}\n")

rpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "reports", "P29_C组_精准匹配.md")
with open(rpath, "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print(f"\nDone: {rpath}")
