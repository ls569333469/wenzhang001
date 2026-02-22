"""清除缓存，重新检查 Google Sheets 数据 + 跑完整测试"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source as gs

# Step 1: 清缓存
print(">>> 清除缓存...")
gs.refresh_cache()

# Step 2: 重新加载
print(">>> 重新加载风格_半佛...")
data = gs._load_sheet_data("风格_半佛")
total = len(data)

has_lp = [r for r in data if r.get("logic_pattern")]
empty_lp = [r for r in data if not r.get("logic_pattern")]
has_content = [r for r in data if r.get("content")]

print(f"总记录: {total}")
print(f"有 content: {len(has_content)}")
print(f"有 logic_pattern: {len(has_lp)}")
print(f"无 logic_pattern: {len(empty_lp)}")

# Step 3: 公式菜单
print("\n>>> 公式菜单:")
menu = gs.get_pattern_menu("banfo")
for i, p in enumerate(menu):
    print(f"  {i+1}. {p}")
print(f"共 {len(menu)} 个")

# Step 4: 随机样本
print("\n>>> 随机3条样本:")
samples = gs.get_samples("banfo", count=3)
for i, s in enumerate(samples):
    c = s.get("content", "")[:80]
    lp = s.get("logic_pattern", "")
    st = s.get("snippet_type", "")
    print(f"  样本{i+1}: [{st}] [{lp}] {c}")

if len(menu) > 0 and len(has_content) > 0:
    print("\n✅ 数据正常，开始跑完整测试...")
    
    from app.agents.strategist import strategist_agent
    from app.agents.writer.short_article import short_article_writer
    
    state = {
        "raw_input": """Vitalik Buterin 发布以太坊 L1 扩展路线图，计划将 L1 Gas Limit 提升 10 倍。
核心变化：将区块 gas limit 从当前 3600万提升到 3.6亿，采用 EIP-4444 对历史数据进行过期处理。
无状态客户端 + Verkle Trees 让验证节点不需要存储完整状态。
目标：L1 本身成为高性能链，而非仅作为 DA 层。
社区反应两极化：支持者认为这是 ETH 重新夺回 DeFi 主权的关键。
反对者担心节点中心化风险加剧。Solana 社区调侃"欢迎来到 2021 年"。
当前 ETH 价格 2780美元，过去30天下跌 12%。""",
        "mode": "short_article",
        "style": "banfo",
        "narrative_type": "project_review",
        "retention_level": 3,
        "api_config": {"provider": "google", "model_id": "gemini-2.0-flash"},
    }
    
    print("\n>>> 策略师分析...")
    result = strategist_agent(state)
    plan_text = result["plan"]
    
    try:
        plan_obj = json.loads(plan_text)
        plans = plan_obj.get("plans", [])
        print(f"\ncore_fact: {plan_obj.get('core_fact', '')}")
        for i, p in enumerate(plans):
            print(f"  V{i+1}: {p.get('label','')} | tone:{p.get('tone','')} | logic_pattern:{p.get('logic_pattern','')}")
            print(f"       hook: {p.get('hook','')}")
    except Exception as e:
        print(f"策略师输出解析失败: {e}")
        plan_obj = {}
        plans = []
    
    print("\n>>> 写手生成...")
    state["strategy_json"] = plan_text
    writer_result = short_article_writer(state)
    
    # 保存报告
    report = ["# P29 验证测试（清理后）\n"]
    report.append(f"数据概况: {total}条 | 有logic_pattern: {len(has_lp)} | 公式菜单: {len(menu)}个\n")
    report.append("## 策略师输出\n```json")
    report.append(json.dumps(plan_obj, ensure_ascii=False, indent=2))
    report.append("```\n")
    report.append("## 写手输出\n")
    for v in writer_result.get("variants", []):
        label = v.get("label", v.get("key", ""))
        report.append(f"### {label} ({v['char_count']}字)\n\n{v['content']}\n")
    
    rpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "reports", "P29_验证测试_清理后.md")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"\n报告: {rpath}")
else:
    print("\n❌ 数据仍有问题，请检查 Google Sheets")
