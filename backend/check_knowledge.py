"""检查 Knowledge_Repo 数据"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import LarkClient

client = LarkClient()
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')

print(f'app_token: {app_token}')
print(f'table_id: {table_id}')

resp = client.list_records(app_token, table_id)
items = resp.get('data', {}).get('items', [])
print(f'Total records: {len(items)}')

for i, item in enumerate(items[:5]):
    fields = item.get('fields', {})
    title = fields.get('标题', 'N/A')
    if isinstance(title, list):
        title = title[0].get('text', 'N/A') if title else 'N/A'
    score = fields.get('质量评分', 0)
    print(f'Record {i+1}: {str(title)[:40]}, Score: {score}')
