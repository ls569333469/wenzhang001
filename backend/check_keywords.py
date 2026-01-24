"""检查关键词字段的实际内容"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import LarkClient

client = LarkClient()
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')

print("=== 检查关键词字段内容 ===\n")

response = client.list_records(app_token, table_id)
items = response.get('data', {}).get('items', [])

# 分类统计
has_keywords = 0
empty_keywords = 0

print("关键词为空或简短的记录:")
print("-" * 60)

for item in items[:30]:  # 只看前 30 条
    fields = item.get('fields', {})
    title = fields.get('标题', 'N/A')
    keywords = fields.get('关键词', '')
    
    # 处理列表类型
    if isinstance(title, list):
        title = title[0].get('text', 'N/A') if title else 'N/A'
    if isinstance(keywords, list):
        keywords = ', '.join(keywords)
    
    if not keywords or len(keywords.strip()) < 3:
        empty_keywords += 1
        print(f"[空] {title[:30]}")
    else:
        has_keywords += 1
        print(f"[OK] {title[:30]} | 关键词: {keywords[:40]}")

print(f"\n统计: 有关键词 {has_keywords}, 无关键词 {empty_keywords}")
