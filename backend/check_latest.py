from dotenv import load_dotenv
load_dotenv()
import os
from app.core.lark_client import lark_client

app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')

result = lark_client.list_records(app_token, table_id, page_size=10)
records = result.get('data', {}).get('items', [])

print("最近上传的记录:")
print("="*60)
for i, r in enumerate(records[:5], 1):
    fields = r.get('fields', {})
    title = fields.get('标题', 'N/A')
    topic = fields.get('赛道分类', 'N/A')
    summary = str(fields.get('核心摘要', ''))[:60]
    print(f"{i}. 【{topic}】")
    print(f"   标题: {title}")
    print(f"   摘要: {summary}...")
    print()
