
import os
import sys
from dotenv import load_dotenv

# Add app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app.core.lark_client import LarkClient
from app.core.config import get_logger

logger = get_logger("test_lark")

def test_connection():
    print("🚀 Testing Lark Connection...")
    
    app_id = os.getenv("LARK_APP_ID")
    base_token = os.getenv("LARK_BASE_TOKEN")
    table_id = os.getenv("LARK_TABLE_ID")
    
    print(f"📋 Configuration:")
    print(f"   App ID: {app_id}")
    print(f"   Base Token: {base_token}")
    print(f"   Table ID: {table_id}")
    
    client = LarkClient()
    
    # 1. Test Auth (Get Token)
    try:
        print("\n🔑 Step 1: Requesting Tenant Access Token...")
        token = client._get_token()
        print(f"   ✅ Success! Token preview: {token[:10]}...")
    except Exception as e:
        print(f"   ❌ Auth Failed: {str(e)}")
        return

    # 2. Test List Records
    try:
        print("\n📄 Step 2: Listing Records from Base...")
        resp = client.list_records(base_token, table_id, page_size=5)
        
        if resp.get("code") == 0:
            count = resp['data']['total']
            items = resp['data']['items']
            print(f"   ✅ Success! Found {count} records.")
            if items:
                print(f"   First record preview: {items[0]['fields']}")
            else:
                print(f"   (Table is empty, but connection works)")
        else:
            print(f"   ❌ API Error: {resp}")
            
    except Exception as e:
        print(f"   ❌ List Records Failed: {str(e)}")

    # 3. Test Sync Service Logic
    print("\n🔄 Step 3: Testing Sync Service Logic...")
    from app.services.sync_service import sync_service
    
    # We won't actually update Lark status in this test unless we want to consume the data.
    # But wait, the user said "Verified". Let's run a real sync!
    # It will pull "Pending" records and save to local JSON.
    
    # Debug: Dump to file
    print("\n🐛 Debug: Dumping raw records to backend/debug_lark_records.json ...")
    raw_resp = client.list_records(base_token, table_id, page_size=5)
    items = raw_resp.get('data', {}).get('items', [])
    
    debug_file = Path("backend/debug_lark_records.json")
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    result = sync_service.sync_from_lark()
    print(f"   Sync Result: {result}")
    
    # Verify local file
    from app.services.sync_service import STYLE_LIBRARY_FILE
    if STYLE_LIBRARY_FILE.exists():
        import json
        with open(STYLE_LIBRARY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   Local Library Size: {len(data)}")
            if data:
                print(f"   Latest Item: {data[-1]}")
    else:
        print("   Local library file not created yet.")

if __name__ == "__main__":
    test_connection()
