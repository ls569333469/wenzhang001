
import os
import json
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add project root

load_dotenv()

from app.core.lark_client import LarkClient

def dump():
    client = LarkClient()
    base_token = os.getenv("LARK_BASE_TOKEN")
    table_id = os.getenv("LARK_TABLE_ID")
    
    print(f"Dumping from Base: {base_token}, Table: {table_id}")
    
    resp = client.list_records(base_token, table_id, page_size=100)
    items = resp.get('data', {}).get('items', [])
    
    # Filter empty items
    valid_items = [item for item in items if item.get('fields')]
    
    print(f"Found {len(items)} total items, {len(valid_items)} with data.")
    
    out_file = "backend/lark_dump.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(valid_items, f, indent=2, ensure_ascii=False)
        
    print(f"Dumped to {out_file}")

if __name__ == "__main__":
    dump()
