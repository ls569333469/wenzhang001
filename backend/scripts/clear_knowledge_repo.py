"""清空 Knowledge_Repo 表中所有记录"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client
import requests

token = lark_client._get_token()
base_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')
base_url = 'https://open.larksuite.com/open-apis'

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 获取所有记录
print('=== 清空 Knowledge_Repo ===')
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records'
resp = requests.get(url, headers=headers, params={'page_size': 100})
records = resp.json().get('data', {}).get('items', [])
print(f'找到 {len(records)} 条记录')

if not records:
    print('表已为空')
    exit(0)

# 批量删除
record_ids = [r['record_id'] for r in records]
print(f'准备删除 {len(record_ids)} 条记录...')

# Lark 批量删除 API
delete_url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records/batch_delete'
payload = {'records': record_ids}
result = requests.post(delete_url, headers=headers, json=payload, timeout=30)

if result.json().get('code') == 0:
    print(f'✅ 成功删除 {len(record_ids)} 条记录')
else:
    print(f'❌ 删除失败: {result.json()}')
