"""Quick test for /analyze endpoint with longer timeout"""
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import time

url = "http://localhost:8000/analyze"
payload = {"input": "比特币突破10万美元，创历史新高"}

print("=" * 60)
print("Testing /analyze API")
print("=" * 60)
print(f"Input: {payload['input']}")
print("Calling API (timeout: 120s)...")
print()

start = time.time()
try:
    r = requests.post(url, json=payload, timeout=120)
    elapsed = time.time() - start
    
    print(f"✅ Status: {r.status_code} (took {elapsed:.1f}s)")
    print()
    
    if r.status_code == 200:
        data = r.json()
        
        # Check SampleService source
        if "sample_source" in data:
            print(f"📊 Sample Source: {data['sample_source']}")
        
        # Display titles
        titles = data.get("title_candidates", [])
        print(f"📌 Title Candidates: {len(titles)}")
        for i, t in enumerate(titles[:5], 1):
            if isinstance(t, dict):
                print(f"  {i}. {t.get('title', 'N/A')}")
                if t.get('formula'):
                    print(f"     Formula: {t.get('formula')}")
            else:
                print(f"  {i}. {t}")
        
        # Display options
        options = data.get("options", [])
        print(f"\n📋 Strategy Options: {len(options)}")
        for i, opt in enumerate(options[:3], 1):
            if isinstance(opt, dict):
                print(f"  {i}. {opt.get('angle', opt.get('title', 'N/A'))}")
            else:
                print(f"  {i}. {opt}")
    else:
        print(f"Error response: {r.text[:500]}")
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"❌ Timeout after {elapsed:.1f}s")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)
