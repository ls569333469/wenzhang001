"""恢复逻辑公式字段数据"""
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

def main():
    app_token = os.getenv("LARK_BASE_TOKEN")
    table_id = os.getenv("LARK_TABLE_ID")
    
    token = lark_client._get_token()
    
    # 加载备份
    backup_file = Path(__file__).parent.parent / "data" / "style_repo_backup_20260118_103136.json"
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_records = json.load(f)
    
    # 筛选有逻辑公式的记录
    records_with_logic = [(r['fields'].get('内容'), r['fields'].get('逻辑公式')) 
                           for r in backup_records if r['fields'].get('逻辑公式')]
    print(f"备份中有逻辑公式的记录: {len(records_with_logic)} 条")
    
    if not records_with_logic:
        print("无需更新")
        return
    
    # 获取当前表中的所有记录
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    all_records = []
    page_token = None
    
    while True:
        url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        params = {"page_size": 100}
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json().get("data", {})
        all_records.extend(data.get("items", []))
        page_token = data.get("page_token")
        if not page_token:
            break
    
    print(f"当前表中记录: {len(all_records)} 条")
    
    # 建立内容到record_id的映射
    content_to_record = {}
    for r in all_records:
        content = r['fields'].get('内容', '')
        if content:
            content_to_record[content[:100]] = r['record_id']  # 用前100字符作为key
    
    # 更新逻辑公式
    updated = 0
    for content, logic in records_with_logic:
        key = content[:100] if content else None
        if key and key in content_to_record:
            record_id = content_to_record[key]
            url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
            payload = {"fields": {"逻辑公式": logic}}
            try:
                result = requests.put(url, headers=headers, json=payload, timeout=10)
                if result.json().get("code") == 0:
                    updated += 1
            except Exception as e:
                pass
        
        if updated % 20 == 0 and updated > 0:
            print(f"  已更新 {updated} 条...")
    
    print(f"\n✅ 成功更新逻辑公式: {updated} 条")

if __name__ == "__main__":
    main()
