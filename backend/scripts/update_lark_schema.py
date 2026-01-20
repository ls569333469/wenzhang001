"""
P12 辅助脚本：获取并添加 Lark 表格字段
"""
import os
import sys
import requests

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client

def get_fields():
    """获取表格现有字段"""
    base_token = os.getenv('LARK_BASE_TOKEN')
    table_id = os.getenv('LARK_TABLE_ID')
    
    print(f"Base Token: {base_token}")
    print(f"Table ID: {table_id}")
    
    # 获取 access token
    token = lark_client._get_token()
    print(f"Access Token: {token[:20]}...")
    
    # 获取表格字段列表
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    
    if data.get("code") == 0:
        fields = data.get("data", {}).get("items", [])
        print(f"\n现有字段列表 ({len(fields)} 个):")
        for f in fields:
            print(f"  - {f.get('field_name')}: Type {f.get('type')}")
        return fields
    else:
        print(f"获取字段失败: {data}")
        return []

def add_field(field_name: str, field_type: int):
    """添加新字段
    
    field_type:
        1 = Text
        2 = Number
        3 = SingleSelect
        7 = Checkbox
    """
    base_token = os.getenv('LARK_BASE_TOKEN')
    table_id = os.getenv('LARK_TABLE_ID')
    token = lark_client._get_token()
    
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "field_name": field_name,
        "type": field_type
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()
    
    if data.get("code") == 0:
        print(f"✅ 成功添加字段: {field_name}")
        return True
    else:
        msg = data.get("msg", "Unknown error")
        if "already exist" in msg.lower() or "duplicate" in msg.lower():
            print(f"⚠️ 字段已存在: {field_name}")
        else:
            print(f"❌ 添加字段失败: {field_name} - {msg}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("P12 Lark Schema 更新工具")
    print("=" * 50)
    
    # 1. 先获取现有字段
    existing_fields = get_fields()
    existing_names = [f.get("field_name") for f in existing_fields]
    
    # 2. 添加 P12 新字段
    print("\n添加 P12 新字段...")
    
    fields_to_add = [
        ("逻辑公式", 1),  # Text
        ("质量分", 2),    # Number
        ("情绪", 1),      # Text - P12 新增
        ("content_hash", 1), # Text - P12.1 去重专用
    ]
    
    for field_name, field_type in fields_to_add:
        if field_name not in existing_names:
            add_field(field_name, field_type)
        else:
            print(f"⚠️ 字段已存在，跳过: {field_name}")
    
    # 3. 验证
    print("\n验证最终字段列表...")
    get_fields()
