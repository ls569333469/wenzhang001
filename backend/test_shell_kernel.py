"""
Shell-Kernel 合成测试
"""
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from app.core.llm import generate_text

prompt = """
# 角色
你是 Quantum Studio 的主笔。

# 任务
请根据【逻辑公式】重写【Web3 事实】。

# 输入素材
1. 逻辑公式 (Shell): "自问自答 + 肯定残酷现实 + 强化贫穷焦虑"
2. 原文句式参考: "长得美的就一定过得比你好吗？是的！"
3. Web3 事实 (Kernel): "贝莱德 IBIT 比特币 ETF 交易量刚刚突破 10 亿美元。"

# 要求
仿照逻辑公式，用咪蒙的语气写一段话，打击那些没买 BTC 的人。
"""

result = generate_text(prompt, provider='volcengine', temperature=0.7)
print('=== Shell-Kernel 合成结果 ===')
print(result)
