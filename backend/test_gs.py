"""Test Google Sheets connection"""
from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source

print('Testing Google Sheets connection...')
print('Available:', google_sheets_source.is_available())

samples = google_sheets_source.get_samples('mimeng', count=3)
print(f'Samples found: {len(samples)}')
if len(samples) == 0:
    # Debug: Check raw data if no samples found
    print("Debug: Checking raw data keys from source...")
    raw_records = google_sheets_source._load_sheet_data('mimeng')
    if raw_records:
        print(f"First record keys: {list(raw_records[0].keys())}")
        print(f"First record style value: {raw_records[0].get('style', 'N/A')}")
    content = s.get('content', '')[:80]
    print(f'  Sample {i}: {content}...')
