"""Analyze banfo data quality for P29 assessment"""
from app.services.google_sheets_source import GoogleSheetsDataSource
from collections import Counter

gs = GoogleSheetsDataSource()
gs._cache['风格_半佛'] = gs._load_sheet_data('风格_半佛')
records = gs._cache.get('风格_半佛', [])

print(f"Total records: {len(records)}")

# 1) logic_pattern
patterns = [r.get("logic_pattern", "") for r in records]
non_empty = [p for p in patterns if p]
print(f"\nRecords with logic_pattern: {len(non_empty)} / {len(records)}")

counter = Counter(non_empty)
combo = [p for p in non_empty if "+" in p]
print(f"Unique patterns: {len(counter)}")
print(f"Combo patterns (with +): {len(combo)} records ({len(set(combo))} unique)")

print("\nTop 20 patterns:")
for p, c in counter.most_common(20):
    tag = "[COMBO]" if "+" in p else "       "
    print(f"  {tag} {c:>4}x  {p}")

# 2) snippet_type
types = [r.get("snippet_type", "") for r in records]
type_counter = Counter([t for t in types if t])
print(f"\nsnippet_type distribution ({len(type_counter)} types):")
for t, c in type_counter.most_common():
    print(f"  {c:>4}x  {t}")

# 3) parent_id
parents = [r.get("parent_id", "") for r in records]
has_parent = len([p for p in parents if p])
print(f"\nRecords with parent_id: {has_parent} / {len(records)}")
