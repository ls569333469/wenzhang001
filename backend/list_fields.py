"""查询 Lark 表字段列表"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import LarkClient

client = LarkClient()
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')

print("=== 查询 Lark 表字段列表 ===\n")

# 获取 token
token = client._get_token()
url = f"{client.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

resp = requests.get(url, headers=headers, timeout=15)
result = resp.json()

if result.get("code") == 0:
    fields = result.get("data", {}).get("items", [])
    print(f"共 {len(fields)} 个字段:\n")
    for field in fields:
        print(f"  - {field.get('field_name')} ({field.get('type')})")
else:
    print(f"错误: {result}")
