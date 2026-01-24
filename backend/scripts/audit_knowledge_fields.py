"""
Quantum Studio v5.1 - Knowledge_Repo 字段审计脚本
==================================================
检查 Lark Knowledge_Repo 表的字段配置，输出保留/删除建议。

Usage:
    cd backend
    python -m scripts.audit_knowledge_fields
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
# v4 规范：需要保留的 10 个字段
# ==========================================
REQUIRED_FIELDS = {
    "标题": {"type": 1, "desc": "文本 - JSON title"},
    "核心摘要": {"type": 1, "desc": "文本 - 截取前 500 字"},
    "正文原文": {"type": 1, "desc": "文本 - JSON content"},
    "赛道分类": {"type": 3, "desc": "单选 - 文件夹名称"},
    "关键词": {"type": 1, "desc": "文本 - LLM 提取"},
    "项目/人名/代币": {"type": 1, "desc": "文本 - LLM 提取"},
    "事实类型": {"type": 3, "desc": "单选 - 规则推断"},
    "质量评分": {"type": 2, "desc": "数字 - LLM 评分 (1-10)"},
    "发布日期": {"type": 5, "desc": "日期 - JSON published_at"},
    "内容指纹": {"type": 1, "desc": "文本 - MD5 哈希 (查重)"},
}

# 需要删除的字段 (v3 弃用)
DEPRECATED_FIELDS = [
    "来源链接", "信息深度", "时效性", "状态", "来源文件",
    "内容类型", "AI 来源文件", "AI 内容精简", "攻击确定评",
    "A/V 内容", "A/V 标题", "A/V 摘要", "A/V 关键词",
    "content", "topic_category", "publish_date", "fact_type",
    "source_file", "content_hash", "Status",
]


def get_retry_session():
    """创建带重试机制的 requests session"""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST", "DELETE"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def list_fields(app_token: str, table_id: str) -> dict:
    """获取表的所有字段（带重试机制）"""
    import time
    
    base_url = os.getenv("LARK_BASE_URL", "https://open.feishu.cn/open-apis")
    url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    
    for attempt in range(5):
        try:
            token = lark_client._get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            }
            session = get_retry_session()
            resp = session.get(url, headers=headers, timeout=60)
            return resp.json()
        except Exception as e:
            print(f"  ⚠️ 尝试 {attempt + 1}/5 失败: {e}")
            if attempt < 4:
                wait_time = (attempt + 1) * 3  # 3, 6, 9, 12 秒
                print(f"    等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    return {"code": -1, "msg": "网络请求失败，已重试 5 次"}


def delete_field(app_token: str, table_id: str, field_id: str) -> dict:
    """删除字段（带重试机制）"""
    import time
    
    base_url = os.getenv("LARK_BASE_URL", "https://open.feishu.cn/open-apis")
    url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
    
    for attempt in range(5):
        try:
            token = lark_client._get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            }
            session = get_retry_session()
            resp = session.delete(url, headers=headers, timeout=60)
            return resp.json()
        except Exception as e:
            print(f"    ⚠️ 删除尝试 {attempt + 1}/5 失败: {e}")
            if attempt < 4:
                wait_time = (attempt + 1) * 3
                print(f"      等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    return {"code": -1, "msg": "删除失败，已重试 5 次"}


def main():
    print("=" * 60)
    print("🔍 Quantum Studio v5.1 - Knowledge_Repo 字段审计")
    print("=" * 60)
    
    # 1. 获取配置
    app_token = os.getenv("LARK_BASE_TOKEN")
    table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
    
    if not app_token or not table_id:
        print("❌ Error: LARK_BASE_TOKEN 或 LARK_KNOWLEDGE_TABLE_ID 未配置")
        return False
    
    print(f"\n📋 Base Token: {app_token}")
    print(f"📋 Knowledge Table ID: {table_id}")
    
    # 2. 获取当前字段
    print("\n" + "-" * 60)
    print("📌 Step 1: 获取当前字段列表")
    print("-" * 60)
    
    result = list_fields(app_token, table_id)
    
    if result.get("code") != 0:
        print(f"❌ 获取字段失败: {result}")
        return False
    
    fields = result.get("data", {}).get("items", [])
    print(f"✅ 找到 {len(fields)} 个字段")
    
    # 3. 分析字段
    print("\n" + "-" * 60)
    print("📌 Step 2: 字段分析")
    print("-" * 60)
    
    keep_fields = []
    delete_fields = []
    missing_fields = set(REQUIRED_FIELDS.keys())
    
    for field in fields:
        field_name = field.get("field_name", "")
        field_id = field.get("field_id", "")
        field_type = field.get("type", 0)
        
        if field_name in REQUIRED_FIELDS:
            keep_fields.append((field_name, field_id, field_type))
            missing_fields.discard(field_name)
            print(f"  ✅ 保留: {field_name} (type={field_type})")
        else:
            delete_fields.append((field_name, field_id, field_type))
            print(f"  ❌ 待删: {field_name} (type={field_type})")
    
    # 4. 输出统计
    print("\n" + "-" * 60)
    print("📌 Step 3: 统计汇总")
    print("-" * 60)
    print(f"  ✅ 保留字段: {len(keep_fields)} 个")
    print(f"  ❌ 待删字段: {len(delete_fields)} 个")
    print(f"  ⚠️ 缺失字段: {len(missing_fields)} 个")
    
    if missing_fields:
        print(f"\n  缺失字段列表:")
        for name in missing_fields:
            info = REQUIRED_FIELDS[name]
            print(f"    - {name}: {info['desc']}")
    
    if delete_fields:
        print(f"\n  待删字段列表:")
        for name, fid, ftype in delete_fields:
            print(f"    - {name} (id={fid})")
    
    # 5. 删除多余字段
    if delete_fields:
        print("\n" + "-" * 60)
        print("📌 Step 4: 删除多余字段")
        print("-" * 60)
        
        confirm = input("  是否删除以上字段? (y/n): ").strip().lower()
        if confirm == 'y':
            for name, fid, ftype in delete_fields:
                result = delete_field(app_token, table_id, fid)
                if result.get("code") == 0:
                    print(f"  ✅ 已删除: {name}")
                else:
                    print(f"  ❌ 删除失败: {name} - {result.get('msg', 'Unknown')}")
        else:
            print("  ⏭️ 跳过删除")
    
    # 6. 提示创建缺失字段
    if missing_fields:
        print("\n" + "-" * 60)
        print("📌 Step 5: 创建缺失字段")
        print("-" * 60)
        
        confirm = input("  是否创建缺失字段? (y/n): ").strip().lower()
        if confirm == 'y':
            for name in missing_fields:
                info = REQUIRED_FIELDS[name]
                result = lark_client.create_field(app_token, table_id, name, info["type"])
                if result.get("code") == 0:
                    print(f"  ✅ 已创建: {name}")
                else:
                    print(f"  ❌ 创建失败: {name} - {result.get('msg', 'Unknown')}")
        else:
            print("  ⏭️ 跳过创建")
    
    print("\n" + "=" * 60)
    print("🎉 审计完成!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
