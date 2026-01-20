"""
Quantum Studio v5.1 - Knowledge_Repo 自动配置脚本
==================================================
自动在 Lark Base 中创建 Knowledge_Repo 表并配置字段。

Usage:
    cd backend
    python -m scripts.setup_knowledge_repo
"""

import os
import sys
import requests
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client

# ==========================================
# 配置区
# ==========================================

# 42 个赛道选项
TOPIC_CATEGORIES = [
    "DeFi进展与分析", "Layer2动态与分析", "MemeCoin研究所", "NFT市场动态",
    "比特币生态", "以太坊生态", "Solana生态", "公链竞争格局",
    "稳定币与支付", "交易所动态", "监管与合规", "宏观经济与加密",
    "AI与加密交叉", "GameFi与元宇宙", "DePIN与硬件", "安全事件与漏洞",
    "DAO治理", "质押与再质押", "跨链与互操作", "钱包与用户体验",
    "开发者工具", "融资与投资", "人物与访谈", "社区文化与Meme",
    "数据分析与指标", "技术深度解析", "项目评测", "行业周报月报",
    "预测市场", "RWA实物资产", "隐私与匿名", "比特币Ordinals",
    "空投与撸毛", "衍生品与期权", "链上数据分析", "机构动态",
    "矿业与能源", "Web3社交", "去中心化存储", "身份与信用", 
    "Telegram生态", "其他热点"
]

# Status 选项
STATUS_OPTIONS = ["待处理", "已审核", "已入库"]

# Fact Type 选项
FACT_TYPE_OPTIONS = ["Hard_Fact", "Narrative", "Slang"]

# ==========================================
# API 函数
# ==========================================

def get_base_url():
    """获取 Lark API Base URL"""
    return os.getenv("LARK_BASE_URL", "https://open.larksuite.com/open-apis")

def create_table(app_token: str, table_name: str, fields: list) -> dict:
    """
    创建新的数据表
    Docs: https://open.larksuite.com/document/server-docs/docs/bitable-v1/app-table/create
    """
    token = lark_client._get_token()
    base_url = get_base_url()
    url = f"{base_url}/bitable/v1/apps/{app_token}/tables"
    
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
    """
    添加字段到表格
    
    field_type:
        1 = Text (多行文本)
        2 = Number (数字)
        3 = SingleSelect (单选)
        4 = MultiSelect (多选)
        5 = DateTime (日期时间)
    """
    token = lark_client._get_token()
    base_url = get_base_url()
    url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "field_name": field_name,
        "type": field_type
    }
    
    # 如果是单选/多选，添加选项
    if field_type in [3, 4] and options:
        payload["property"] = {
            "options": [{"name": opt} for opt in options]
        }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    return resp.json()

def update_style_repo_add_status(app_token: str, table_id: str) -> dict:
    """给现有的 Style_Repo 表添加 Status 字段"""
    return add_field(app_token, table_id, "Status", 3, STATUS_OPTIONS)

# ==========================================
# 主流程
# ==========================================

def main():
    print("=" * 60)
    print("🚀 Quantum Studio v5.1 - Knowledge_Repo 自动配置")
    print("=" * 60)
    
    # 1. 获取配置
    app_token = os.getenv("LARK_BASE_TOKEN")
    style_table_id = os.getenv("LARK_TABLE_ID")  # 现有的 Style_Repo 表
    
    if not app_token:
        print("❌ Error: LARK_BASE_TOKEN 未配置")
        return False
    
    print(f"\n📋 Base Token: {app_token}")
    print(f"📋 Style Table ID: {style_table_id}")
    
    # 2. 定义 Knowledge_Repo 表的初始字段
    # 注意：Lark API 创建表时需要至少一个字段
    initial_fields = [
        {"field_name": "content", "type": 1},  # Text
    ]
    
    print("\n" + "-" * 60)
    print("📌 Step 1: 创建 Knowledge_Repo 表")
    print("-" * 60)
    
    result = create_table(app_token, "Knowledge_Repo", initial_fields)
    
    if result.get("code") != 0:
        print(f"❌ 创建表失败: {result}")
        # 如果表已存在，尝试继续
        if "already exist" in str(result).lower() or "duplicate" in str(result).lower():
            print("⚠️ 表可能已存在，请手动获取 table_id 后继续")
        return False
    
    knowledge_table_id = result.get("data", {}).get("table_id")
    print(f"✅ 表创建成功! Table ID: {knowledge_table_id}")
    
    # 3. 添加其他字段
    print("\n" + "-" * 60)
    print("📌 Step 2: 添加 Knowledge_Repo 字段")
    print("-" * 60)
    
    fields_to_add = [
        ("topic_category", 3, TOPIC_CATEGORIES),  # 单选 + 42个选项
        ("publish_date", 5, None),                 # 日期
        ("fact_type", 3, FACT_TYPE_OPTIONS),       # 单选
        ("source_file", 1, None),                  # 文本
        ("content_hash", 1, None),                 # 文本
        ("Status", 3, STATUS_OPTIONS),             # 单选
    ]
    
    for field_name, field_type, options in fields_to_add:
        result = add_field(app_token, knowledge_table_id, field_name, field_type, options)
        if result.get("code") == 0:
            print(f"  ✅ 添加字段: {field_name}")
        else:
            msg = result.get("msg", "Unknown error")
            if "already exist" in msg.lower() or "duplicate" in msg.lower():
                print(f"  ⚠️ 字段已存在: {field_name}")
            else:
                print(f"  ❌ 添加失败: {field_name} - {msg}")
    
    # 4. 更新 Style_Repo 表，添加 Status 字段
    if style_table_id:
        print("\n" + "-" * 60)
        print("📌 Step 3: 更新 Style_Repo 表 (添加 Status 字段)")
        print("-" * 60)
        
        result = update_style_repo_add_status(app_token, style_table_id)
        if result.get("code") == 0:
            print("  ✅ Style_Repo 添加 Status 字段成功")
        else:
            msg = result.get("msg", "Unknown error")
            if "already exist" in msg.lower() or "duplicate" in msg.lower():
                print("  ⚠️ Status 字段已存在")
            else:
                print(f"  ❌ 添加失败: {msg}")
    
    # 5. 输出配置信息
    print("\n" + "=" * 60)
    print("🎉 配置完成!")
    print("=" * 60)
    print(f"\n请将以下内容添加到 .env 文件:")
    print(f"  LARK_KNOWLEDGE_TABLE_ID={knowledge_table_id}")
    print(f"\n或更新 user_config.json:")
    print(f'  "lark_knowledge_table_id": "{knowledge_table_id}"')
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
