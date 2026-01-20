"""
重建 Style_Repo 表 - 统一中文字段
==================================
1. 备份现有数据到本地 JSON
2. 删除旧表
3. 创建新表（中文字段）
4. 恢复数据

Usage:
    cd backend
    python -m scripts.recreate_style_repo
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client

# ==========================================
# 中文字段配置
# ==========================================

# 博主选项
BLOGGER_OPTIONS = ["咪蒙", "半佛仙人", "视觉志", "新世相", "小红书", "富达", "lianbushou"]

# 片段类型选项
SNIPPET_TYPE_OPTIONS = ["开头金句", "正文段落", "结尾升华", "金句语录", "行动号召"]

# 情绪选项
EMOTION_OPTIONS = ["积极", "消极", "中性", "激昂", "共情"]

# 状态选项
STATUS_OPTIONS = ["待处理", "已审核", "已入库"]

# 字段映射：旧字段名 -> 新字段名
FIELD_MAPPING = {
    "内容": "内容",
    "A= 内容": "内容",
    "作者": "博主",
    "风格": "博主",
    "类型": "片段类型",
    "状态": "状态",
    "Status": "状态",
    "质量分": "质量评分",
    "情绪": "情绪",
    "content_hash": "内容指纹",
    "逻辑公式": None,  # 不迁移
}

# ==========================================
# API 函数
# ==========================================

def get_base_url():
    return os.getenv("LARK_BASE_URL", "https://open.larksuite.com/open-apis")

def get_all_records(app_token: str, table_id: str) -> list:
    """获取所有记录"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_records = []
    page_token = None
    
    while True:
        params = {"page_size": 100}
        if page_token:
            params["page_token"] = page_token
        
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        data = resp.json()
        
        if data.get("code") != 0:
            print(f"❌ 获取记录失败: {data}")
            break
        
        items = data.get("data", {}).get("items", [])
        all_records.extend(items)
        
        page_token = data.get("data", {}).get("page_token")
        if not page_token:
            break
        
        print(f"  已获取 {len(all_records)} 条...")
    
    return all_records

def delete_table(app_token: str, table_id: str) -> dict:
    """删除表"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers, timeout=15)
    return resp.json()

def create_table(app_token: str, table_name: str, fields: list) -> dict:
    """创建表"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "table": {
            "name": table_name,
            "default_view_name": "默认视图",
            "fields": fields
        }
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    return resp.json()

def add_field(app_token: str, table_id: str, field_name: str, field_type: int, options: list = None) -> dict:
    """添加字段"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"field_name": field_name, "type": field_type}
    if options:
        payload["property"] = {"options": [{"name": opt} for opt in options]}
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    return resp.json()

def create_record(app_token: str, table_id: str, fields: dict) -> dict:
    """创建记录"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"fields": fields}
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    return resp.json()

def transform_record(old_fields: dict) -> dict:
    """转换记录字段名"""
    new_fields = {}
    
    for old_key, value in old_fields.items():
        new_key = FIELD_MAPPING.get(old_key)
        if new_key is None:
            continue  # 跳过不需要迁移的字段
        
        # 处理单选字段（Lark 返回的格式可能是 dict）
        if isinstance(value, dict) and "text" in value:
            value = value["text"]
        elif isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], dict) and "text" in value[0]:
                value = value[0]["text"]
        
        new_fields[new_key] = value
    
    return new_fields

# ==========================================
# 主流程
# ==========================================

def main():
    print("=" * 60)
    print("🔄 重建 Style_Repo 表 (统一中文字段)")
    print("=" * 60)
    
    app_token = os.getenv("LARK_BASE_TOKEN")
    old_table_id = os.getenv("LARK_TABLE_ID")
    
    if not app_token or not old_table_id:
        print("❌ 配置缺失")
        return False
    
    # Step 1: 备份数据
    print("\n📌 Step 1: 备份现有数据")
    print("-" * 60)
    
    records = get_all_records(app_token, old_table_id)
    print(f"  ✅ 获取 {len(records)} 条记录")
    
    # 保存到本地
    backup_file = Path(__file__).parent.parent / "data" / f"style_repo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 备份保存到: {backup_file}")
    
    # Step 2: 删除旧表
    print("\n📌 Step 2: 删除旧表")
    print("-" * 60)
    
    result = delete_table(app_token, old_table_id)
    if result.get("code") == 0:
        print("  ✅ 旧表删除成功")
    else:
        print(f"  ⚠️ 删除结果: {result.get('msg', result)}")
    
    # Step 3: 创建新表
    print("\n📌 Step 3: 创建新表 (中文字段)")
    print("-" * 60)
    
    initial_fields = [
        {"field_name": "内容", "type": 1},
    ]
    
    result = create_table(app_token, "Style_Repo", initial_fields)
    
    if result.get("code") != 0:
        print(f"  ❌ 创建失败: {result}")
        return False
    
    new_table_id = result.get("data", {}).get("table_id")
    print(f"  ✅ 新表创建成功! Table ID: {new_table_id}")
    
    # Step 4: 添加其他字段
    print("\n📌 Step 4: 添加其他字段")
    print("-" * 60)
    
    fields_to_add = [
        ("博主", 3, BLOGGER_OPTIONS),
        ("片段类型", 3, SNIPPET_TYPE_OPTIONS),
        ("情绪", 3, EMOTION_OPTIONS),
        ("内容指纹", 1, None),
        ("质量评分", 2, None),
        ("状态", 3, STATUS_OPTIONS),
    ]
    
    for field_name, field_type, options in fields_to_add:
        result = add_field(app_token, new_table_id, field_name, field_type, options)
        if result.get("code") == 0:
            print(f"  ✅ {field_name}")
        else:
            print(f"  ❌ {field_name}: {result.get('msg', result)}")
    
    # Step 5: 恢复数据
    print("\n📌 Step 5: 恢复数据")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, record in enumerate(records):
        old_fields = record.get("fields", {})
        new_fields = transform_record(old_fields)
        
        if not new_fields.get("内容"):
            fail_count += 1
            continue
        
        result = create_record(app_token, new_table_id, new_fields)
        if result.get("code") == 0:
            success_count += 1
        else:
            fail_count += 1
        
        if (i + 1) % 50 == 0:
            print(f"  进度: {i + 1}/{len(records)}")
    
    print(f"  ✅ 成功恢复: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    
    # 完成
    print("\n" + "=" * 60)
    print("🎉 重建完成!")
    print("=" * 60)
    print(f"\n⚠️ 请更新 .env 文件:")
    print(f"  LARK_TABLE_ID={new_table_id}")
    
    return new_table_id

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
