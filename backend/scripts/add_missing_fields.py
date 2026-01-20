"""补充缺失的中文字段"""
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

# 需要添加的字段
fields_to_add = [
    ("来源文件", 1, None),                 # 文本
    ("内容指纹", 1, None),                 # 文本 (用于去重)
    ("质量评分", 2, None),                 # 数字
    ("状态", 3, ["待处理", "已审核", "已入库"]),  # 单选
]

for field_name, field_type, options in fields_to_add:
    url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/fields'
    payload = {
        "field_name": field_name,
        "type": field_type
    }
    if options:
        payload["property"] = {"options": [{"name": opt} for opt in options]}
    
    result = requests.post(url, headers=headers, json=payload, timeout=15)
    code = result.json().get('code')
    if code == 0:
        print(f'✅ {field_name}')
    else:
        msg = result.json().get('msg', str(result.json()))
        print(f'❌ {field_name}: {msg}')

print("\n完成!")
