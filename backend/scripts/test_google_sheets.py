# Google Sheets Connection Test Script

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_google_sheets_connection():
    print("=== Google Sheets Connection Test ===\n")
    
    # Check environment variables
    print("[1] Checking environment variables...")
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "config/google_service_account.json")
    spreadsheet = os.getenv("GOOGLE_SHEETS_SPREADSHEET", "Quantum_Samples")
    sheet_name = os.getenv("GOOGLE_SHEETS_SHEET_NAME", "mimeng")
    
    print(f"    GOOGLE_SHEETS_CREDENTIALS: {creds_path}")
    print(f"    GOOGLE_SHEETS_SPREADSHEET: {spreadsheet}")
    print(f"    GOOGLE_SHEETS_SHEET_NAME: {sheet_name}")
    
    if not os.path.exists(creds_path):
        print(f"\n❌ Error: Credentials file not found at: {creds_path}")
        return False
    
    print(f"    ✅ Credentials file exists\n")
    
    # Test import
    print("[2] Testing gspread import...")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        print("    ✅ gspread and google-auth imported successfully\n")
    except ImportError as e:
        print(f"    ❌ Import error: {e}")
        print("    Run: pip install gspread google-auth")
        return False
    
    # Test connection
    print("[3] Connecting to Google Sheets...")
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        gc = gspread.authorize(creds)
        # Use open_by_key to avoid Drive API requirement
        if len(spreadsheet) > 40:
            ss = gc.open_by_key(spreadsheet)
        else:
            ss = gc.open(spreadsheet)
        print(f"    ✅ Connected to spreadsheet!\n")
    except Exception as e:
        print(f"    ❌ Connection failed: {e}")
        return False
    
    # List sheets
    print("[4] Available sheets:")
    for ws in ss.worksheets():
        print(f"    - {ws.title}")
    print()
    
    # Test reading data
    print(f"[5] Reading data from sheet: {sheet_name}...")
    try:
        worksheet = ss.worksheet(sheet_name)
        records = worksheet.get_all_records()
        print(f"    ✅ Found {len(records)} records\n")
        
        if records:
            print("[6] Sample record (first row):")
            first = records[0]
            for key, val in list(first.items())[:5]:  # Show first 5 fields
                val_str = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
                print(f"    {key}: {val_str}")
            print()
            
            # Check for style column
            styles = set(r.get("风格标签", "") for r in records)
            print(f"[7] Found styles (风格标签): {styles}\n")
            
    except Exception as e:
        print(f"    ❌ Error reading sheet: {e}")
        return False
    
    print("=== ✅ All tests passed! ===")
    return True


if __name__ == "__main__":
    success = test_google_sheets_connection()
    sys.exit(0 if success else 1)
