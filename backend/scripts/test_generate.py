"""测试 Quantum Studio 写作流程 v2 - 调试版"""
import requests
import json
import sys

# 素材内容
content = """JustLend DAO 今日正式完成第二次 JST 代币回购销毁，共计销毁 5.25 亿枚 JST，价值约 2100 万美元，代币已转入黑洞地址。"""

print('=' * 60)
print('=== 调用 Generate 生成文章 (咪蒙风格) ===')
print('=' * 60)

payload = {
    'input': content,
    'mode': 'mimeng',
    'narrative_type': 'project_review',
    'references': []
}

try:
    resp = requests.post('http://localhost:8004/generate', json=payload, timeout=300, stream=True)
    print(f'Status: {resp.status_code}\n')
    
    if resp.status_code != 200:
        print(f'Error: {resp.text}')
        sys.exit(1)
    
    # SSE 流式读取 - 详细调试
    all_data = []
    for line in resp.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = line_str[6:]
                if data == '[DONE]':
                    break
                try:
                    parsed = json.loads(data)
                    all_data.append(parsed)
                    
                    # 打印所有字段
                    if 'type' in parsed:
                        print(f"[TYPE: {parsed['type']}]")
                        if parsed['type'] == 'final':
                            print("\n=== FINAL CONTENT ===")
                            print(parsed.get('content', 'NO CONTENT'))[:500]
                        elif parsed['type'] == 'result':
                            print("\n=== RESULT ===")
                            if 'state' in parsed:
                                state = parsed['state']
                                if 'polished_draft' in state:
                                    print("Polished draft found!")
                                    print(state['polished_draft'][:500] if state['polished_draft'] else 'Empty')
                    elif 'agent' in parsed:
                        print(f"[{parsed['agent']}] {parsed.get('status', '')[:50]}")
                except Exception as e:
                    print(f"Parse error: {e}")
    
    # 保存所有数据到文件
    with open('sse_debug.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("\n\nSaved all SSE data to sse_debug.json")

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
