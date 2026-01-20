"""
Quantum Studio v5.1 - Lark 字段选项汉化脚本
==================================================
更新 Lark 表格的字段选项为中文。

Usage:
    cd backend
    python -m scripts.update_lark_labels
"""

import os
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client

# ==========================================
# 中文标签配置
# ==========================================

# 内容类型 (Web3 Knowledge + Web2 Style 通用)
FACT_TYPE_OPTIONS = [
    {"name": "硬数据", "color": 0},      # data - 链上数据、价格、TVL
    {"name": "深度分析", "color": 1},    # analysis - 技术解析、研报
    {"name": "观点评论", "color": 2},    # opinion - 主观看法、预测
    {"name": "梗_黑话", "color": 3},     # meme - WAGMI、Diamond Hands
    {"name": "快讯资讯", "color": 4},    # news - 事件报道
]

# 片段类型 (Style_Repo 专用)
SNIPPET_TYPE_OPTIONS = [
    {"name": "开头金句", "color": 0},    # hook
    {"name": "正文段落", "color": 1},    # body
    {"name": "结尾升华", "color": 2},    # ending
    {"name": "金句语录", "color": 3},    # golden
    {"name": "行动号召", "color": 4},    # cta
]

# 状态 (通用)
STATUS_OPTIONS = [
    {"name": "待处理", "color": 0},
    {"name": "已审核", "color": 1},
    {"name": "已入库", "color": 2},
]

# ==========================================
# API 函数
# ==========================================

def get_base_url():
    return os.getenv("LARK_BASE_URL", "https://open.larksuite.com/open-apis")

def list_fields(app_token: str, table_id: str):
    """列出表格所有字段"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    return resp.json()

def update_field_options(app_token: str, table_id: str, field_id: str, field_name: str, options: list):
    """更新单选字段的选项 - 使用删除并重建的方式"""
    token = lark_client._get_token()
    base_url = get_base_url()
    
    # Lark API 不支持直接更新选项，需要删除后重建字段
    # 先删除旧字段
    delete_url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    delete_resp = requests.delete(delete_url, headers=headers)
    if delete_resp.json().get("code") != 0:
        # 如果删除失败，尝试直接添加新字段
        pass
    
    # 创建新字段（带新选项）
    create_url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    payload = {
        "field_name": field_name,
        "type": 3,  # SingleSelect
        "property": {
            "options": options
        }
    }
    
    resp = requests.post(create_url, headers=headers, json=payload)
    return resp.json()

def find_field_by_name(fields: list, name: str) -> dict:
    """根据字段名查找字段"""
    for field in fields:
        if field.get("field_name") == name:
            return field
    return None

# ==========================================
# 主流程
# ==========================================

def update_table_fields(app_token: str, table_id: str, table_name: str, field_updates: dict):
    """更新指定表格的字段选项"""
    print(f"\n{'='*60}")
    print(f"📋 处理表格: {table_name}")
    print(f"{'='*60}")
    
    # 获取现有字段
    result = list_fields(app_token, table_id)
    if result.get("code") != 0:
        print(f"❌ 获取字段失败: {result}")
        return False
    
    fields = result.get("data", {}).get("items", [])
    print(f"   找到 {len(fields)} 个字段")
    
    # 更新字段
    for field_name, options in field_updates.items():
        field = find_field_by_name(fields, field_name)
        if not field:
            print(f"   ⚠️ 字段不存在: {field_name}")
            continue
        
        field_id = field.get("field_id")
        result = update_field_options(app_token, table_id, field_id, options)
        
        if result.get("code") == 0:
            print(f"   ✅ 更新成功: {field_name}")
        else:
            print(f"   ❌ 更新失败: {field_name} - {result.get('msg', result)}")
    
    return True

def main():
    print("=" * 60)
    print("🚀 Quantum Studio v5.1 - Lark 字段选项汉化")
    print("=" * 60)
    
    app_token = os.getenv("LARK_BASE_TOKEN")
    knowledge_table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
    style_table_id = os.getenv("LARK_TABLE_ID")
    
    if not app_token:
        print("❌ LARK_BASE_TOKEN 未配置")
        return
    
    # 1. 更新 Knowledge_Repo 表
    if knowledge_table_id:
        update_table_fields(
            app_token, 
            knowledge_table_id, 
            "Knowledge_Repo",
            {
                "fact_type": FACT_TYPE_OPTIONS,
                "Status": STATUS_OPTIONS,
            }
        )
    else:
        print("⚠️ LARK_KNOWLEDGE_TABLE_ID 未配置，跳过 Knowledge_Repo")
    
    # 2. 更新 Style_Repo 表
    if style_table_id:
        update_table_fields(
            app_token, 
            style_table_id, 
            "Style_Repo",
            {
                "snippet_type": SNIPPET_TYPE_OPTIONS,
                "Status": STATUS_OPTIONS,
            }
        )
    else:
        print("⚠️ LARK_TABLE_ID 未配置，跳过 Style_Repo")
    
    print("\n" + "=" * 60)
    print("🎉 字段选项汉化完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
