import requests
import json
import sys

url = "http://localhost:8000/api/rewrite"
payload = {
    "selected_text": "Hello world, this is a test.",
    "instruction": "Make it more formal.",
    "api_config": {
        "provider": "volcengine"
    }
}

try:
    print(f"Testing {url}...")
    with requests.post(url, json=payload, stream=True, timeout=60) as r:
        if r.status_code == 200:
            print("Response stream:")
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    print(chunk.decode('utf-8'), end='', flush=True)
            print("\nSuccess!")
        else:
            print(f"Failed with status: {r.status_code}")
            print(r.text)
            sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
