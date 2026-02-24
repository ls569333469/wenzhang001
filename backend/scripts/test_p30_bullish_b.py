"""P30 B方案测试：bullish_take 优化后端到端验证"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv; load_dotenv()

from app.agents.strategist import build_strategist_context, build_strategist_prompt, execute_strategist_analysis
from app.agents.writer.bullish_take import bullish_take_writer
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from app.services.sample_service import sample_service
from datetime import datetime

TEST_INPUT = """Ondo 代币化证券现已上线币安 Alpha！

在 #币安钱包 享受专业级链上证券交易体验
🔸 最低 0% 手续费
🔸 可轻松使用交易所资金购买
🔸 首批上线 10 个代币化证券
🔸 交易或持有均可赚取币安 Alpha 积分

代币化证券专属交易活动即将开启。

币安宣布Ondo代币化证券产品现已上线币安Alpha。本次更新将为您提供更便捷流畅的交易体验，帮助您在币安交易平台体验链上资产带来的创新机遇。

核心功能：
- 便捷无缝交易：可直接使用CEX账户资金交易链上代币化证券产品。
- 低交易手续费&限时零Gas费：享受低至0%的交易手续费，限时期间，在币安交易平台下单与撤单均免Gas费。
- 灵活的交易方式：除即时成交的市价单外，限价单现已支持。
- 赚取Alpha积分：每次交易或者仅持有Ondo代币化证券，均可累积币安Alpha积分用于解锁空投、TGE、Prime Sales等专属活动。

关于代币化证券：
代币化证券是用于在链上跟踪传统证券或ETF价格表现的数字证券。它们提供对标的资产价格变动的敞口，但不赋予投票权等全部股东权利。
Ondo 代币化证券产品由 Ondo 提供，这是一个专注于将证券、ETF等现实世界资产（RWA）进行代币化的区块链平台。
根据FSRA的监管规定，Ondo代币化证券产品被归类为证券（结构性产品），并通过币安Alpha向用户提供。"""

API_CONFIG = {"provider": "google", "model_id": "gemini-2.0-flash"}

print("=" * 60)
print("P30 B方案测试 — bullish_take 新版提示词")
print("=" * 60)

# Step 1: 策略师
print("\n>>> Step 1: 策略师分析...")
state = {
    "raw_input": TEST_INPUT,
    "mode": "bullish_take",
    "style": "banfo",
    "narrative_type": "bullish_take",
    "retention_level": 3,
    "api_config": API_CONFIG,
}
context = build_strategist_context(state)
sys_prompt, user_prompt = build_strategist_prompt(context, state)
strategy_text = execute_strategist_analysis(user_prompt, sys_prompt, API_CONFIG)

try:
    strategy_obj = json.loads(strategy_text)
    plans = strategy_obj.get("plans", [])
    print(f"\n✅ 策略师输出 {len(plans)} 个方案:")
    print(json.dumps(strategy_obj, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"❌ 策略师JSON解析失败: {e}")
    print(f"原始输出: {strategy_text[:500]}")
    sys.exit(1)

# Step 2: 写手
print("\n>>> Step 2: 写手生成3个版本...")
state["strategy_json"] = strategy_text
result = bullish_take_writer(state)

variants = result.get("variants", [])
print(f"\n✅ 写手生成 {len(variants)} 个版本:")

# 输出报告
report = []
report.append("# P30 B方案测试结果\n")
report.append(f"> 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
report.append("## 素材\n")
report.append(f"```\n{TEST_INPUT}\n```\n")

report.append("## 策略师输出\n")
report.append(f"```json\n{json.dumps(strategy_obj, ensure_ascii=False, indent=2)}\n```\n")

report.append("## 写手输出\n")
for i, v in enumerate(variants):
    label = v.get("label", f"版本{i+1}")
    story = v.get("instruction", "")
    content = v.get("content", "")
    chars = v.get("char_count", 0)

    plan = plans[i] if i < len(plans) else {}
    perspective = plan.get("perspective", "")
    detail = plan.get("detail", "")

    report.append(f"### {label}（{perspective}）\n")
    report.append(f"- 故事线: {story}")
    report.append(f"- 事实抓手: {detail}")
    report.append(f"- 字数: {chars}\n")
    report.append(f"{content}\n")

    print(f"\n{'='*40}")
    print(f"版本{i+1}: {label} ({perspective}) [{chars}字]")
    print(f"{'='*40}")
    print(content)

rpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "reports", "P30_B方案测试结果.md")
with open(rpath, "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print(f"\n报告已保存: {rpath}")
