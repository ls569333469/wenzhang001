"""
测试 Strategist 输出多样性
"""
from app.agents.strategist import build_strategist_context, build_strategist_prompt
from app.core.llm import generate_text
import json

# 测试状态
state = {
    'raw_input': '黄金突破5280美元',
    'mode': 'mimeng',
    'style': 'mimeng',
    'retention_level': 3
}

# 构建上下文
context = build_strategist_context(state)
print('=== SAMPLES (first 500 chars) ===')
print(context.get('rag_context', 'N/A')[:500])

# 构建 prompt
system_prompt, user_prompt = build_strategist_prompt(context, state)

# 调用 LLM (temperature=0.9 更高)
print('\n=== CALLING LLM (temp=0.9) ===')
try:
    result = generate_text(user_prompt, system_prompt=system_prompt, temperature=0.9)
    print(f'Result length: {len(result)}')
    
    # 尝试解析 JSON
    try:
        data = json.loads(result)
        titles = data.get('title_candidates', [])
        print(f'\n=== TITLES ({len(titles)} found) ===')
        for t in titles[:5]:
            print(f"- {t.get('title', 'N/A')}")
    except json.JSONDecodeError:
        print(f'Raw result (first 500): {result[:500]}')
except Exception as e:
    print(f'ERROR: {e}')
