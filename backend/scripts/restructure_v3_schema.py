"""v3.0 Schema 重构脚本"""
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
knowledge_table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')
style_table_id = os.getenv('LARK_TABLE_ID')
base_url = 'https://open.larksuite.com/open-apis'

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# ==========================================
# Knowledge_Repo 字段重命名
# ==========================================
print("\n=== Knowledge_Repo 字段调整 ===")

# 获取现有字段
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{knowledge_table_id}/fields'
resp = requests.get(url, headers=headers)
fields = resp.json().get('data', {}).get('items', [])

rename_map = {
    '内容': '正文原文',
    '摘要': '核心摘要',
    '内容类型': '事实类型',
}

# 需要更新选项的字段
option_update = {
    '事实类型': ['事实', '观点', '黑话']  # v3.0 新选项
}

for field in fields:
    field_name = field['field_name']
    field_id = field['field_id']
    field_type = field['type']
    
    # 重命名
    if field_name in rename_map:
        new_name = rename_map[field_name]
        update_url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{knowledge_table_id}/fields/{field_id}'
        payload = {'field_name': new_name}
        
        # 如果需要更新选项
        if new_name in option_update and field_type == 3:  # 单选字段
            payload['property'] = {
                'options': [{'name': opt} for opt in option_update[new_name]]
            }
        
        result = requests.put(update_url, headers=headers, json=payload, timeout=15)
        if result.json().get('code') == 0:
            print(f'  ✅ 重命名: {field_name} -> {new_name}')
        else:
            print(f'  ❌ 失败 {field_name}: {result.json().get("msg", result.json())}')

# ==========================================
# Style_Repo 新增风格标签字段
# ==========================================
print("\n=== Style_Repo 字段调整 ===")

# 新增风格标签 (多选)
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{style_table_id}/fields'
payload = {
    'field_name': '风格标签',
    'type': 4,  # 4 = 多选
    'property': {
        'options': [
            {'name': '毒舌'}, {'name': '焦虑'}, {'name': '逻辑'},
            {'name': '共情'}, {'name': '对比'}, {'name': '反差'},
            {'name': '讽刺'}, {'name': '煽情'}, {'name': '数据流'}
        ]
    }
}
result = requests.post(url, headers=headers, json=payload, timeout=15)
if result.json().get('code') == 0:
    print('  ✅ 新增: 风格标签 (多选)')
else:
    msg = result.json().get('msg', str(result.json()))
    if 'duplicate' in msg.lower() or 'exist' in msg.lower():
        print('  ⚠️ 风格标签 已存在')
    else:
        print(f'  ❌ 风格标签: {msg}')

print("\n✅ Schema 调整完成!")
