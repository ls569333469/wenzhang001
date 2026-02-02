"""
P12 验证脚本 - 测试 5 维度评分系统
"""
import sys
sys.path.insert(0, ".")

from app.agents.critic import critic_agent

# 测试素材 (简化版 1INCH 风格)
TEST_DRAFT = """
1INCH 最近搞了个大动作：Fusion+ 升级，号称要做跨链聚合的终极答案。

简单说，就是你想换币，它帮你找全网最优价格，还能跨链搞定。不用自己去比较 DEX 价格，不用担心 MEV 被夹。

技术上，用的是荷兰拍卖 + Resolver 竞争机制。Resolver 们互相卷，你就能拿到更好的价格。

但说实话，跨链这块竞争太卷了。LayerZero、Stargate、Axelar 都在抢。1INCH 能不能杀出来，还得看执行力。

我的看法：短期内先观望，等看看真实的交易量数据再说。
"""

print("=" * 60)
print("P12 验证: 5 维度评分系统测试")
print("=" * 60)

# 调用 Critic
result = critic_agent(
    draft=TEST_DRAFT,
    mode="quick_take",
    api_config={"provider": "volcengine"},  # 使用 Doubao
    length="thread",
    style="mimeng"
)

print(f"\n返回类型: {type(result)}")
print(f"\n返回结果:")

if isinstance(result, dict):
    print(f"  ✅ 返回 dict (P12 正确)")
    print(f"  - score: {result.get('score')}")
    print(f"  - verdict: {result.get('verdict')}")
    print(f"  - dimensions: {list(result.get('dimensions', {}).keys())}")
    print(f"  - penalties: {len(result.get('penalties', []))} 项")
    print(f"  - suggestions: {len(result.get('suggestions', []))} 条")
    print(f"  - cot_analysis: {result.get('cot_analysis', '')[:100]}...")
else:
    print(f"  ❌ 返回 tuple (旧版本)")
    print(f"  - 需要检查 critic.py 是否正确更新")

print("\n" + "=" * 60)
