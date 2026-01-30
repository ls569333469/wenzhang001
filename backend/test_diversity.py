"""Test Strategist title diversity by making two API calls"""
from dotenv import load_dotenv
load_dotenv()

import requests
import json

url = "http://localhost:8000/analyze"
payload = {"input": "比特币突破10万美元，创历史新高"}

print("=" * 60)
print("Testing Strategist Title Diversity")
print("=" * 60)

# First call
print("\n📌 First API Call...")
try:
    r1 = requests.post(url, json=payload, timeout=60)
    data1 = r1.json()
    titles1 = data1.get("title_candidates", [])
    print(f"Status: {r1.status_code}")
    print(f"Titles generated: {len(titles1)}")
    for i, t in enumerate(titles1[:3], 1):
        title_text = t.get("title", t) if isinstance(t, dict) else t
        print(f"  {i}. {title_text}")
except Exception as e:
    print(f"Error: {e}")
    titles1 = []

# Second call
print("\n📌 Second API Call (same input)...")
try:
    r2 = requests.post(url, json=payload, timeout=60)
    data2 = r2.json()
    titles2 = data2.get("title_candidates", [])
    print(f"Status: {r2.status_code}")
    print(f"Titles generated: {len(titles2)}")
    for i, t in enumerate(titles2[:3], 1):
        title_text = t.get("title", t) if isinstance(t, dict) else t
        print(f"  {i}. {title_text}")
except Exception as e:
    print(f"Error: {e}")
    titles2 = []

# Compare
print("\n" + "=" * 60)
print("📊 Diversity Analysis")
print("=" * 60)

if titles1 and titles2:
    t1_set = set(str(t.get("title", t) if isinstance(t, dict) else t) for t in titles1)
    t2_set = set(str(t.get("title", t) if isinstance(t, dict) else t) for t in titles2)
    overlap = t1_set & t2_set
    
    if len(overlap) == 0:
        print("✅ SUCCESS: All titles are different between calls!")
    elif len(overlap) < len(t1_set):
        print(f"⚠️ PARTIAL: {len(overlap)}/{len(t1_set)} titles overlap")
    else:
        print("❌ FAIL: All titles are identical - diversity fix may not be working")
    
    print(f"\nOverlapping titles: {list(overlap)[:2] if overlap else 'None'}")
else:
    print("❌ Could not compare - one or both calls failed")
