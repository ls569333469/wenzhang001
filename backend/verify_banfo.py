import os, requests
from dotenv import load_dotenv
load_dotenv()

app_id = os.getenv('LARK_APP_ID')
app_secret = os.getenv('LARK_APP_SECRET')
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_TABLE_ID')

token_resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', 
    json={'app_id': app_id, 'app_secret': app_secret})
token = token_resp.json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}'}

resp = requests.get(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=20', headers=headers)
items = resp.json().get('data', {}).get('items', [])

print('=== 验证新入库的 banfo 数据 ===')
for item in items[:5]:
    f = item.get('fields', {})
    if f.get('博主') == 'banfo':
        print(f"片段类型: {f.get('片段类型')}")
        print(f"情绪: {f.get('情绪')}")
        print(f"风格标签: {f.get('风格标签')}")
        lp = f.get('逻辑公式', '')
        print(f"逻辑公式: {lp[:40]}..." if lp else "逻辑公式: 无")
        print()
