"""Test: /analyze SSE flow - capture full error detail"""
import requests, json, time

LONG_MATERIAL = "Blockchain 合伙人：加密资产正在经历价值重估。" * 20  # ~600 chars

body = {
    "input": LONG_MATERIAL,
    "mode": "short_article",
    "style": "banfo",
    "narrative_type": "project_review",
    "references": [],
    "api_config": {"provider": "google", "model_id": "gemini-2.0-flash"},
}

print(f"Material: {len(LONG_MATERIAL)} chars")
r = requests.post("http://localhost:8000/analyze", json=body, stream=True, timeout=120)
print(f"Status: {r.status_code}")

for line in r.iter_lines(decode_unicode=True):
    if line and line.startswith("data: "):
        try:
            evt = json.loads(line[6:])
            etype = evt.get("type", "?")
            if etype == "error":
                print(f"ERROR: {evt}")
            elif etype == "analysis_result":
                payload = evt.get("payload", {})
                print(f"RESULT: auto_proceed={payload.get('auto_proceed')}, plans={len(payload.get('plans', []))}")
            else:
                print(f"  {etype}: {str(evt.get('detail', evt.get('payload', '')))[:100]}")
        except Exception as e:
            print(f"PARSE: {e} | {line[:100]}")
