import asyncio
import json
from app.graph import app_graph

async def test():
    inputs = {
        'raw_input': '据 Coinglass 数据显示，全网在过去 4 小时内爆仓 3.33 亿美元，其中多单爆仓 3.27 亿美元。此外，ETH 爆仓达 1.38 亿美元，BTC 爆仓约 7460 万美元。',
        'mode': 'quick_summary',
        'style': 'mimeng',
        'length': 'thread',
        'retention_level': 3,
        'narrative_type': 'project_review',
        'references': [],
        'api_config': {'provider': 'volcengine'},
        'agent_config': {}
    }
    
    results = {}
    async for event in app_graph.astream(inputs, stream_mode='updates'):
        for node, data in event.items():
            results[node] = data
    
    # Save to file
    with open('test_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print('=== Results saved to test_result.json ===')
    
    # Print key info
    if 'writer' in results:
        print('\n--- WRITER DRAFT ---')
        print(results['writer'].get('draft', 'N/A'))
    
    if 'critic' in results:
        print('\n--- CRITIC ---')
        print(f"Score: {results['critic'].get('critique_score', 'N/A')}")
        print(f"Verdict: {results['critic'].get('critique_verdict', 'N/A')}")
        cr = results['critic'].get('critique_result', {})
        if cr:
            print(f"Suggestions: {cr.get('suggestions', [])}")
    
    if 'polisher' in results:
        print('\n--- POLISHER (FINAL) ---')
        print(results['polisher'].get('final_content', 'N/A'))

if __name__ == '__main__':
    asyncio.run(test())
