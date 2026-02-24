import csv

with open(r"D:\AI_Projects\Web2风格\banfo66_with_parent_v3.csv", "r", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

total = len(rows)
matched = sum(1 for r in rows if r.get("父记录", "").strip())
empty = total - matched
print(f"Total: {total}")
print(f"Matched: {matched} ({matched/total*100:.1f}%)")
print(f"Empty: {empty} ({empty/total*100:.1f}%)")

print("\nSample unmatched rows:")
shown = 0
for i, r in enumerate(rows):
    if not r.get("父记录", "").strip() and shown < 10:
        snippet_type = r.get("片段类型", "")
        content = r.get("内容", "")[:60]
        print(f"  Row {i}: [{snippet_type}] {content}")
        shown += 1
