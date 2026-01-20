"""查看 Style_Repo 现有字段和数据量"""
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
table_id = os.getenv('LARK_TABLE_ID')  # Style_Repo
base_url = 'https://open.larksuite.com/open-apis'

headers = {'Authorization': f'Bearer {token}'}

# 获取字段
print("=== Style_Repo 字段 ===")
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/fields'
resp = requests.get(url, headers=headers)
fields = resp.json().get('data', {}).get('items', [])
for f in fields:
    prop = f.get('property') or {}
    opts = [o.get('name') for o in prop.get('options', [])] if prop.get('options') else []
    print(f"  {f['field_name']}: type={f['type']}, options={opts[:6]}{'...' if len(opts) > 6 else ''}")

# 获取记录数
print("\n=== Style_Repo 数据量 ===")
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records'
resp = requests.get(url, headers=headers, params={'page_size': 1})
data = resp.json().get('data', {})
total = data.get('total', 0)
print(f"  总记录数: {total}")
