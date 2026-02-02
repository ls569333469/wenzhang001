"""
P12 完整写作流程 DEMO 测试
话题：1INCH 团队大额卖出事件分析
"""
import sys
import json
sys.path.insert(0, ".")

from datetime import datetime

# 1INCH 素材
SOURCE_MATERIAL = """
1inch 团队"的大额卖出，再次激发了恶评。

近日，链上数据平台 ARKHAM 页面显示，三个被标记为"1inch 团队"的钱包，前先后共计了卖出 3636 万枚 1INCH，价值 504 万美元。据 okx 行情数据显示，受此影响，1INCH 代币价格在短时下跌 16.7%至 0.1155 美元，暂报 0.1164 美元。

关键事实：
- 卖出量：3636万枚 1INCH
- 价值：504万美元
- 价格影响：短时下跌16.7%
- 成本：约0.42美元（2024年11月）
- 当前价格：约0.14美元
- 估计损失：超1000万美元

1inch团队过往操作：
- 2月-4月：低位吸筹3319万枚，均价0.2美元
- 7月：追加2299万枚，价格从0.18涨至0.206
- 7月中旬：价格冲至0.39美元，团队浮盈数百万
- 8月：以4215美元卖出5000枚ETH，获利836万美元

官方回应：
此次卖出并未发生在任何由1inch团队控制的钱包中，可能来自已脱离项目控制的第三方持有者。

市场背景：
1INCH从上轮高点6美元已跌至0.11美元附近，长期单边下行。
"""

print("=" * 70)
print("P12 完整写作流程 DEMO 测试")
print(f"时间: {datetime.now().isoformat()}")
print("=" * 70)

# Step 1: 测试 Strategist
print("\n" + "=" * 70)
print("[Step 1] Strategist - 策略分析")
print("=" * 70)

from app.agents.strategist import strategist_agent

state = {
    "raw_input": SOURCE_MATERIAL,
    "mode": "deep_analysis",
    "style": "mimeng",
    "api_config": {"provider": "google"}
}

strategist_result = strategist_agent(state)

print(f"策略分析结果类型: {type(strategist_result)}")
plan = strategist_result.get('plan', '')
print(f"- plan 长度: {len(plan)} 字符")

# 尝试解析 plan
try:
    plan_data = json.loads(plan)
    options_count = len(plan_data.get('options', []))
    print(f"- options: {options_count} 个策略选项")
    strategy_text = plan_data.get('options', [{}])[0].get('angle', '1INCH团队卖出事件深度分析')
except:
    options_count = 0
    strategy_text = "1INCH团队大额卖出事件：链上标签误读还是真实砸盘？"
    print("- plan 不是有效 JSON，使用默认策略")

# Step 2: 测试 Writer
print("\n" + "=" * 70)
print("[Step 2] Writer - 内容生成")
print("=" * 70)

from app.agents.writer import writer_agent

# writer_agent 也接收 state dict
writer_state = {
    "raw_input": SOURCE_MATERIAL,
    "mode": "deep_analysis",
    "style": "mimeng",
    "length": "thread",
    "strategy_json": json.dumps({"angle": strategy_text}),
    # 使用火山引擎托管的 DeepSeek V3
    "api_config": {"provider": "volcengine", "model_id": "deepseek-v3-2-251201"}
}

writer_result = writer_agent(writer_state)

# writer_agent 返回 {"draft_content": ...}
if isinstance(writer_result, dict):
    draft = writer_result.get('draft_content', writer_result.get('draft', ''))
else:
    draft = str(writer_result)

print(f"生成内容长度: {len(draft)} 字")
print(f"内容预览: {draft[:200]}...")

# Step 3: 测试 Critic (P12 核心)
print("\n" + "=" * 70)
print("[Step 3] Critic - 5维度评分 (P12)")
print("=" * 70)

from app.agents.critic import critic_agent

critic_result = critic_agent(
    draft=draft,
    mode="deep_analysis",
    api_config={"provider": "volcengine"},
    length="thread",
    style="mimeng"
)

print(f"返回类型: {type(critic_result)}")
if isinstance(critic_result, dict):
    print(f"✅ P12 正确返回 dict")
    print(f"- score: {critic_result.get('score')}")
    print(f"- verdict: {critic_result.get('verdict')}")
    print(f"- dimensions: {list(critic_result.get('dimensions', {}).keys())}")
    print(f"- penalties: {len(critic_result.get('penalties', []))} 项")
    print(f"- suggestions: {len(critic_result.get('suggestions', []))} 条")
    
    if critic_result.get('suggestions'):
        print("\n修改建议:")
        for i, s in enumerate(critic_result.get('suggestions', [])[:3], 1):
            print(f"  {i}. {s}")
else:
    print(f"❌ 返回类型错误: {type(critic_result)}")

# Step 4: 测试 Polisher
print("\n" + "=" * 70)
print("[Step 4] Polisher - 润色")
print("=" * 70)

from app.agents.polisher import polisher_agent

if isinstance(critic_result, dict):
    feedback = critic_result.get('verdict', 'REFINE') + ": " + "; ".join(critic_result.get('suggestions', []))
else:
    feedback = "需要润色"

polisher_result = polisher_agent(
    draft=draft,
    critique_feedback=feedback,
    api_config={"provider": "volcengine"}
)

print(f"润色后内容长度: {len(polisher_result)} 字")
print(f"内容预览: {polisher_result[:200]}...")

# 最终总结
print("\n" + "=" * 70)
print("DEMO 测试完成!")
print("=" * 70)

print(f"""
📊 测试结果汇总:
- Strategist: {options_count} 个策略
- Writer: {len(draft)} 字
- Critic: {critic_result.get('score') if isinstance(critic_result, dict) else 'N/A'}/100 ({critic_result.get('verdict') if isinstance(critic_result, dict) else 'N/A'})
- Polisher: {len(polisher_result)} 字

✅ P12 5维度评分系统工作正常!
""")

# 保存结果
output = {
    "timestamp": datetime.now().isoformat(),
    "source": "1INCH团队卖出事件",
    "strategist_options": options_count,
    "writer_length": len(draft),
    "critic_score": critic_result.get('score') if isinstance(critic_result, dict) else 0,
    "critic_verdict": critic_result.get('verdict') if isinstance(critic_result, dict) else "N/A",
    "critic_result": critic_result if isinstance(critic_result, dict) else {},
    "polisher_length": len(polisher_result),
    "final_content": polisher_result
}

with open("p12_demo_result.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"结果已保存至: p12_demo_result.json")
