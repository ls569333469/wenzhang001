"""重命名 Lark 字段为中文"""
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

# 字段名称映射
rename_map = {
    'content': '内容',
    'topic_category': '赛道分类',
    'publish_date': '发布日期',
    'fact_type': '内容类型',
    'source_file': '来源文件',
    'content_hash': '内容指纹',
    'quality_score': '质量评分',
    'Status': '状态',
}

# 获取所有字段
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/fields'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
resp = requests.get(url, headers=headers)
fields = resp.json().get('data', {}).get('items', [])

print(f"找到 {len(fields)} 个字段")

# 更新字段名称
for field in fields:
    old_name = field['field_name']
    if old_name in rename_map:
        field_id = field['field_id']
        new_name = rename_map[old_name]
        update_url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/fields/{field_id}'
        payload = {'field_name': new_name}
        result = requests.put(update_url, headers=headers, json=payload)
        code = result.json().get('code')
        if code == 0:
            print(f'✅ {old_name} -> {new_name}')
        else:
            msg = result.json().get('msg', str(result.json()))
            print(f'❌ {old_name}: {msg}')

print("\n完成!")
