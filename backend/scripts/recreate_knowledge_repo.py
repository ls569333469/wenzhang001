"""
重建 Knowledge_Repo 表 - 使用中文字段名
=========================================
删除现有表，重新创建带有中文字段名的表。

Usage:
    cd backend
    python -m scripts.recreate_knowledge_repo
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
# 中文字段配置
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

# 中文内容类型选项
FACT_TYPE_OPTIONS = ["硬数据", "深度分析", "观点评论", "梗_黑话", "快讯资讯"]

# 状态选项
STATUS_OPTIONS = ["待处理", "已审核", "已入库"]

# ==========================================
# API 函数
# ==========================================

def get_base_url():
    return os.getenv("LARK_BASE_URL", "https://open.larksuite.com/open-apis")

def delete_table(app_token: str, table_id: str) -> dict:
    """删除数据表"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers, timeout=15)
    return resp.json()

def create_table(app_token: str, table_name: str, fields: list) -> dict:
    """创建新的数据表"""
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
    """添加字段到表格"""
    token = lark_client._get_token()
    url = f"{get_base_url()}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "field_name": field_name,
        "type": field_type
    }
    if field_type in [3, 4] and options:
        payload["property"] = {
            "options": [{"name": opt} for opt in options]
        }
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    return resp.json()

# ==========================================
# 主流程
# ==========================================

def main():
    print("=" * 60)
    print("🔄 重建 Knowledge_Repo 表 (中文字段)")
    print("=" * 60)
    
    app_token = os.getenv("LARK_BASE_TOKEN")
    old_table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
    
    if not app_token:
        print("❌ LARK_BASE_TOKEN 未配置")
        return False
    
    # Step 1: 删除旧表
    if old_table_id:
        print(f"\n📌 Step 1: 删除旧表 ({old_table_id})")
        print("-" * 60)
        result = delete_table(app_token, old_table_id)
        if result.get("code") == 0:
            print("  ✅ 旧表删除成功")
        else:
            msg = result.get("msg", str(result))
            print(f"  ⚠️ 删除结果: {msg}")
    else:
        print("\n📌 Step 1: 跳过删除 (无旧表 ID)")
    
    # Step 2: 创建新表 (带中文字段)
    print("\n📌 Step 2: 创建新表 (中文字段)")
    print("-" * 60)
    
    # 初始字段必须包含一个，我们用"内容"
    initial_fields = [
        {"field_name": "内容", "type": 1},  # Text
    ]
    
    result = create_table(app_token, "Knowledge_Repo", initial_fields)
    
    if result.get("code") != 0:
        print(f"  ❌ 创建失败: {result}")
        return False
    
    new_table_id = result.get("data", {}).get("table_id")
    print(f"  ✅ 新表创建成功! Table ID: {new_table_id}")
    
    # Step 3: 添加其他中文字段
    print("\n📌 Step 3: 添加其他字段")
    print("-" * 60)
    
    fields_to_add = [
        ("赛道分类", 3, TOPIC_CATEGORIES),    # 单选
        ("发布日期", 5, None),                 # 日期
        ("内容类型", 3, FACT_TYPE_OPTIONS),    # 单选 (中文选项)
        ("来源文件", 1, None),                 # 文本
        ("内容指纹", 1, None),                 # 文本 (用于去重)
        ("质量评分", 2, None),                 # 数字
        ("状态", 3, STATUS_OPTIONS),           # 单选
    ]
    
    for field_name, field_type, options in fields_to_add:
        result = add_field(app_token, new_table_id, field_name, field_type, options)
        if result.get("code") == 0:
            print(f"  ✅ {field_name}")
        else:
            msg = result.get("msg", "Unknown error")
            print(f"  ❌ {field_name}: {msg}")
    
    # Step 4: 输出新配置
    print("\n" + "=" * 60)
    print("🎉 重建完成!")
    print("=" * 60)
    print(f"\n⚠️ 请更新 .env 文件:")
    print(f"  LARK_KNOWLEDGE_TABLE_ID={new_table_id}")
    
    return new_table_id

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
