import os
import sys
# Add backend directory to sys.path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import re
from app.core.lark_client import lark_client

DATA_FILE = r"d:\AI_Projects\2026001\mimeng_dataset_clean.txt"

def parse_and_upload():
    if not os.path.exists(DATA_FILE):
        print(f"File not found: {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by sections
    sections = re.split(r"##\s+", content)
    
    app_token = os.getenv("LARK_BASE_TOKEN")
    table_id = os.getenv("LARK_TABLE_ID")
    
    if not app_token or not table_id:
        print("Error: LARK_BASE_TOKEN or LARK_TABLE_ID not set")
        return

    print(f"Target Base: {app_token}, Table: {table_id}")

    total_uploaded = 0

    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split("\n")
        header = lines[0].strip() # e.g. "Hooks (Startings)"
        
        # Determine Type based on Header
        item_type = "Quote"
        if "Hooks" in header:
            item_type = "Hook"
        elif "Golden" in header:
            item_type = "Quote"
            
        print(f"Processing Section: {header} -> Type: {item_type}")
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering "1. ", "10. "
            content_text = re.sub(r"^\d+\.\s*", "", line)
            
            if not content_text:
                continue

            fields = {
                "内容": content_text,
                "作者": "咪蒙",
                "风格": "mimeng",
                "类型": item_type,
                "状态": "待处理" # Pending
            }
            
            try:
                print(f"Uploading: {content_text[:20]}...")
                lark_client.create_record(app_token, table_id, fields)
                total_uploaded += 1
            except Exception as e:
                print(f"Failed to upload: {e}")

    print(f"Done! Total uploaded: {total_uploaded}")

if __name__ == "__main__":
    parse_and_upload()
