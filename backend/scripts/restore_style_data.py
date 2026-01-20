"""恢复 Style_Repo 数据 v2 - 带选项值映射"""
import os
import sys
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client

base_url = os.getenv("LARK_BASE_URL", "https://open.larksuite.com/open-apis")

# 字段名映射
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
}

# 选项值映射 (旧值 -> 新值)
SNIPPET_TYPE_MAP = {
    "Hook": "开头金句",
    "Hook/Quote": "开头金句",
    "Body": "正文段落",
    "Body/Quote": "正文段落", 
    "Ending": "结尾升华",
    "Quote": "金句语录",
    "CTA": "行动号召",
    # 保留中文值
    "开头金句": "开头金句",
    "正文段落": "正文段落",
    "结尾升华": "结尾升华",
    "金句语录": "金句语录",
    "行动号召": "行动号召",
}

EMOTION_MAP = {
    "Positive": "积极",
    "Negative": "消极",
    "Neutral": "中性",
    "High Arousal": "激昂",
    "Empathy": "共情",
    # 保留中文
    "积极": "积极",
    "消极": "消极",
    "中性": "中性",
    "激昂": "激昂",
    "共情": "共情",
}

STATUS_MAP = {
    "待处理": "待处理",
    "已同步": "已审核",  # 已同步 -> 已审核
    "已审核": "已审核",
    "已入库": "已入库",
}

def transform_record(old_fields: dict, debug: bool = False) -> dict:
    """转换记录字段名和值"""
    new_fields = {}
    
    for old_key, value in old_fields.items():
        new_key = FIELD_MAPPING.get(old_key)
        if not new_key:
            continue
        
        # 处理 Lark 返回的复杂格式
        if isinstance(value, dict) and "text" in value:
            value = value["text"]
        elif isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], dict) and "text" in value[0]:
                value = value[0]["text"]
        
        # 转换选项值
        if new_key == "片段类型" and value:
            mapped = SNIPPET_TYPE_MAP.get(str(value), "开头金句")  # 默认开头金句
            if debug and mapped != value:
                print(f"  [映射] 片段类型: {value} -> {mapped}")
            value = mapped
        
        elif new_key == "情绪" and value:
            mapped = EMOTION_MAP.get(str(value), "中性")  # 默认中性
            if debug and mapped != value:
                print(f"  [映射] 情绪: {value} -> {mapped}")
            value = mapped
        
        elif new_key == "状态" and value:
            mapped = STATUS_MAP.get(str(value), "待处理")
            value = mapped
        
        elif new_key == "质量评分" and value:
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = 5.0
        
        new_fields[new_key] = value
    
    return new_fields

def main():
    app_token = os.getenv("LARK_BASE_TOKEN")
    table_id = os.getenv("LARK_TABLE_ID")
    
    token = lark_client._get_token()
    
    # 加载备份
    backup_file = Path(__file__).parent.parent / "data" / "style_repo_backup_20260118_103136.json"
    with open(backup_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"加载 {len(records)} 条备份记录")
    
    # 检查已有多少记录
    check_url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(check_url, headers=headers, params={"page_size": 1})
    existing = resp.json().get("data", {}).get("total", 0)
    print(f"表中已有 {existing} 条记录")
    
    start_index = existing
    print(f"从第 {start_index + 1} 条开始恢复...")
    
    # 测试前 3 条的转换
    print("\n--- 测试转换 (前 3 条) ---")
    for i, record in enumerate(records[start_index:start_index+3]):
        old_fields = record.get("fields", {})
        new_fields = transform_record(old_fields, debug=True)
        print(f"  [{i+1}] 内容: {new_fields.get('内容', '')[:30]}...")
        print(f"       片段类型: {new_fields.get('片段类型')}, 情绪: {new_fields.get('情绪')}, 状态: {new_fields.get('状态')}")
    
    print("\n--- 开始恢复 ---")
    headers["Content-Type"] = "application/json"
    success = 0
    fail = 0
    
    for i, record in enumerate(records[start_index:], start=start_index):
        old_fields = record.get("fields", {})
        new_fields = transform_record(old_fields)
        
        if not new_fields.get("内容"):
            fail += 1
            continue
        
        url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        try:
            result = requests.post(url, headers=headers, json={"fields": new_fields}, timeout=15)
            
            if result.json().get("code") == 0:
                success += 1
            else:
                fail += 1
                if fail <= 5:
                    print(f"  ❌ 失败: {result.json().get('msg', result.json())}")
        except Exception as e:
            fail += 1
            if fail <= 5:
                print(f"  ❌ 异常: {e}")
        
        if (i + 1) % 50 == 0:
            print(f"进度: {i + 1}/{len(records)} (成功: {success}, 失败: {fail})")
    
    print(f"\n✅ 成功: {success}")
    print(f"❌ 失败: {fail}")

if __name__ == "__main__":
    main()
