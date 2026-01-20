"""修改 Lark 表视图名称为中文"""
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
base_url = 'https://open.larksuite.com/open-apis'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 获取并修改视图名称
tables = [
    ('Style_Repo', os.getenv('LARK_TABLE_ID'), '风格库'),
    ('Knowledge_Repo', os.getenv('LARK_KNOWLEDGE_TABLE_ID'), '知识库')
]

for table_name, table_id, chinese_name in tables:
    # 获取视图列表
    url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/views'
    resp = requests.get(url, headers=headers)
    views = resp.json().get('data', {}).get('items', [])
    
    print(f'\n=== {table_name} ===')
    for v in views:
        view_id = v['view_id']
        view_name = v['view_name']
        view_type = v['view_type']
        print(f'  现有视图: {view_name} (type={view_type})')
        
        # 修改默认视图名称
        if view_name == '默认视图' or view_name == 'Default View':
            new_name = f'{chinese_name}主视图'
            update_url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/views/{view_id}'
            payload = {'view_name': new_name}
            result = requests.patch(update_url, headers=headers, json=payload)
            if result.json().get('code') == 0:
                print(f'  ✅ 视图重命名: {view_name} -> {new_name}')
            else:
                print(f'  ❌ 重命名失败: {result.json().get("msg", result.json())}')
