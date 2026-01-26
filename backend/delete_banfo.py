import os, requests
from dotenv import load_dotenv
load_dotenv()

app_id = os.getenv('LARK_APP_ID')
app_secret = os.getenv('LARK_APP_SECRET')
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_TABLE_ID')

# 获取 token
token_resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', 
    json={'app_id': app_id, 'app_secret': app_secret})
token = token_resp.json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 获取并删除 banfo 记录
resp = requests.get(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=500', headers=headers)
items = resp.json().get('data', {}).get('items', [])
banfo_ids = [item['record_id'] for item in items if item.get('fields', {}).get('博主') == 'banfo']
print(f'banfo 记录: {len(banfo_ids)}')
if banfo_ids:
    delete_resp = requests.post(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete', 
        headers=headers, json={'records': banfo_ids})
    print(f'删除成功: {delete_resp.json().get("code") == 0}')
