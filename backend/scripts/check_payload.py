"""
Check analysis_result payload structure
"""
import requests
import json

url = 'http://localhost:8000/analyze'
payload = {'input': '比特币ETF', 'mode': 'deep_analysis'}

print('Checking analysis_result payload structure...')
try:
    response = requests.post(url, json=payload, timeout=120, stream=True)
    for line in response.iter_lines(decode_unicode=True):
        if line and 'analysis_result' in line:
            print('Found analysis_result event!')
            # Parse the data line
            if line.startswith('data: '):
                data = json.loads(line[6:])
                payload_obj = data.get('payload', {})
                print(f'Payload keys: {list(payload_obj.keys())}')
                
                # Check for 'options'
                if 'options' in payload_obj:
                    opts = payload_obj['options']
                    print(f'options found: {len(opts)} items')
                    if opts:
                        print(f'First option keys: {list(opts[0].keys())}')
                        print(f'First option: {json.dumps(opts[0], ensure_ascii=False)[:300]}')
                else:
                    print('options NOT found in payload!')
                    print(f'Available keys: {list(payload_obj.keys())}')
                    # Print what we have
                    for k in payload_obj.keys():
                        v = payload_obj[k]
                        if isinstance(v, str):
                            print(f'  {k}: {v[:100]}...')
                        elif isinstance(v, list):
                            print(f'  {k}: list with {len(v)} items')
                        elif isinstance(v, dict):
                            print(f'  {k}: dict with keys {list(v.keys())[:5]}')
                        else:
                            print(f'  {k}: {type(v).__name__}')
            break
except Exception as e:
    print(f'Error: {e}')
