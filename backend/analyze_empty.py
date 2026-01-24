"""分析 Lark Knowledge_Repo 中的空白记录"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import LarkClient

client = LarkClient()
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')

print("=== 分析 Knowledge_Repo 数据质量 ===\n")

response = client.list_records(app_token, table_id)
items = response.get('data', {}).get('items', [])

print(f"总记录数: {len(items)}\n")

# 统计空白字段
empty_stats = {
    "标题": 0,
    "赛道分类": 0,
    "关键词": 0,
    "正文原文": 0,
    "正文内容": 0,
}

empty_records = []  # 记录 ID 列表

for item in items:
    fields = item.get('fields', {})
    record_id = item.get('record_id', '')
    
    # 检查关键字段是否为空
    title = fields.get('标题', '')
    content = fields.get('正文原文', '') or fields.get('正文内容', '')
    keywords = fields.get('关键词', '')
    topic = fields.get('赛道分类', '') or fields.get('主题', '')
    
    # 处理列表类型
    if isinstance(title, list):
        title = title[0].get('text', '') if title else ''
    if isinstance(content, list):
        content = ''.join([t.get('text', '') for t in content if isinstance(t, dict)])
    if isinstance(keywords, list):
        keywords = ', '.join(keywords)
    if isinstance(topic, list):
        topic = ', '.join(topic)
    
    # 统计
    if not title or title.strip() == '':
        empty_stats["标题"] += 1
        empty_records.append(record_id)
    if not content or content.strip() == '':
        empty_stats["正文原文"] += 1
    if not keywords or keywords.strip() == '':
        empty_stats["关键词"] += 1
    if not topic or topic.strip() == '':
        empty_stats["赛道分类"] += 1

print("=== 空白字段统计 ===")
for field, count in empty_stats.items():
    pct = count / len(items) * 100 if items else 0
    status = "[!]" if count > 0 else "[OK]"
    print(f"{status} {field}: {count} 条空白 ({pct:.1f}%)")

print(f"\n需要清理的记录数: {len(set(empty_records))}")

# 输出空白记录 ID（用于删除）
if empty_records:
    print("\n空白记录 ID (前 10 条):")
    for rid in list(set(empty_records))[:10]:
        print(f"  - {rid}")
