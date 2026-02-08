import json

with open("scripts/wublock_articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i, a in enumerate(data, 1):
    title = a.get("title", "?")[:60]
    strategy = a.get("strategy", "?")
    length = a.get("content_length", 0)
    content = a.get("content", "")
    
    # Get meaningful content lines
    lines = [l.strip() for l in content.split("\n") if l.strip() and len(l.strip()) > 20]
    preview = "\n    ".join(lines[:5])
    
    print(f"[{i}] {title}")
    print(f"    Strategy: {strategy}")
    print(f"    Content: {length} chars")
    print(f"    Preview:")
    print(f"    {preview[:400]}")
    print()
