"""查看 Lark 表字段"""
import os
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client
import requests

token = lark_client._get_token()
base_token = os.getenv('LARK_BASE_TOKEN')

for name, table_id in [
    ("Knowledge_Repo", os.getenv('LARK_KNOWLEDGE_TABLE_ID')),
    ("Style_Repo", os.getenv('LARK_TABLE_ID'))
]:
    print(f"\n=== {name} ({table_id}) ===")
    url = f'https://open.larksuite.com/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/fields'
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    
    if data.get('code') == 0:
        fields = data.get('data', {}).get('items', [])
        for f in fields:
            prop = f.get('property') or {}
            opts = prop.get('options', [])
            opt_names = [o.get('name') for o in opts] if opts else []
            print(f"  {f['field_name']}: type={f['type']}, options={opt_names}")
    else:
        print(f"  Error: {data}")
