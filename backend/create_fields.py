"""创建 Lark 表字段"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import LarkClient

client = LarkClient()
app_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')

print("=== 创建 Lark 表字段 ===\n")

# 创建 "项目/人名/代币" 字段 (文本类型 = 1)
print("创建字段: 项目/人名/代币 (文本)")
result1 = client.create_field(app_token, table_id, "项目/人名/代币", field_type=1)
print(f"  结果: {result1.get('code')} - {result1.get('msg', 'OK')}")

# 创建 "质量评分" 字段 (数字类型 = 2)
print("创建字段: 质量评分 (数字)")
result2 = client.create_field(app_token, table_id, "质量评分", field_type=2)
print(f"  结果: {result2.get('code')} - {result2.get('msg', 'OK')}")

print("\n=== 完成 ===")
