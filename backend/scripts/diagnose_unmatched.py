"""诊断未匹配片段：分析失败原因并尝试更激进的匹配"""
import csv
import os
import hashlib
import re
from pathlib import Path
from collections import Counter

CSV_PATH = r"D:\AI_Projects\Web2风格\banfo66_with_parent_v2.csv"
TXT_DIR = r"D:\AI_Projects\Web2风格\半佛仙人"

# 加载原文
articles = {}
for root, dirs, files in os.walk(TXT_DIR):
    for f in files:
        if f.endswith(".txt"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as fp:
                text = fp.read()
            name_key = Path(f).stem
            pid = hashlib.md5(name_key.encode("utf-8")).hexdigest()[:12]
            # 多种清洗版本
            text_clean = text.replace("\r", "").replace("\n", "").replace(" ", "")
            # 更激进：去标点
            text_nopunc = re.sub(r'[^\w]', '', text)
            articles[pid] = {
                "name_key": name_key,
                "text_clean": text_clean,
                "text_nopunc": text_nopunc,
            }

# 加载 v2 结果
with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

unmatched = [(i, r) for i, r in enumerate(rows) if not r.get("父记录", "").strip()]
print(f"Total unmatched: {len(unmatched)}")

# === 分析 1: 内容长度分布 ===
lengths = [len(r.get("内容", "")) for _, r in unmatched]
print(f"\nContent length stats:")
print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.0f}")
short = sum(1 for l in lengths if l <= 10)
medium = sum(1 for l in lengths if 10 < l <= 30)
long = sum(1 for l in lengths if l > 30)
print(f"  <=10 chars: {short}")
print(f"  11-30 chars: {medium}")
print(f"  >30 chars: {long}")

# === 分析 2: 片段类型分布 ===
types = Counter(r.get("片段类型", "") for _, r in unmatched)
print(f"\nSnippet type distribution:")
for t, c in types.most_common():
    print(f"  {c:>4}x {t}")

# === 分析 3: 尝试更激进匹配 ===
print(f"\n=== 尝试优化匹配 ===")
fixed = 0
still_fail = 0
fail_samples = []

for idx, (i, row) in enumerate(unmatched):
    content = row.get("内容", "").strip()
    if not content:
        still_fail += 1
        continue
    
    content_clean = content.replace("\r", "").replace("\n", "").replace(" ", "")
    content_nopunc = re.sub(r'[^\w]', '', content)
    
    # 策略 A: 用去标点版本匹配
    matches_a = []
    for pid, art in articles.items():
        if content_nopunc and content_nopunc in art["text_nopunc"]:
            matches_a.append(pid)
    
    if len(matches_a) >= 1:
        row["_fix"] = matches_a[0]
        fixed += 1
        continue
    
    # 策略 B: 用更短的指纹（前20字）
    if len(content_clean) >= 15:
        short_fp = content_clean[:20]
        matches_b = []
        for pid, art in articles.items():
            if short_fp in art["text_clean"]:
                matches_b.append(pid)
        if len(matches_b) >= 1:
            row["_fix"] = matches_b[0]
            fixed += 1
            continue
    
    # 策略 C: 只要内容中有连续 10 个字出现在某原文中
    if len(content_clean) >= 10:
        chunk = content_clean[:10]
        matches_c = []
        for pid, art in articles.items():
            if chunk in art["text_clean"]:
                matches_c.append(pid)
        if len(matches_c) == 1:
            row["_fix"] = matches_c[0]
            fixed += 1
            continue
    
    still_fail += 1
    if len(fail_samples) < 15:
        # 看看它周围的邻居
        prev_pid = ""
        next_pid = ""
        for j in range(i-1, max(i-5, -1), -1):
            p = rows[j].get("父记录", "").strip()
            if p:
                prev_pid = p
                break
        for j in range(i+1, min(i+5, len(rows))):
            p = rows[j].get("父记录", "").strip()
            if p:
                next_pid = p
                break
        
        fail_samples.append({
            "row": i,
            "type": row.get("片段类型", ""),
            "content": content[:80],
            "len": len(content),
            "prev_pid": prev_pid,
            "next_pid": next_pid,
        })

print(f"  Fixable with aggressive matching: {fixed}")
print(f"  Still failing: {still_fail}")

print(f"\n=== Still failing samples ===")
for s in fail_samples:
    prev_name = ""
    next_name = ""
    if s["prev_pid"] in articles:
        prev_name = articles[s["prev_pid"]]["name_key"][:30]
    if s["next_pid"] in articles:
        next_name = articles[s["next_pid"]]["name_key"][:30]
    same = "SAME" if s["prev_pid"] == s["next_pid"] and s["prev_pid"] else "DIFF"
    print(f"  Row {s['row']:>5} [{s['type']:>6}] ({s['len']:>3}ch) {same} | {s['content'][:60]}")
    if same == "SAME":
        print(f"          neighbors: {prev_name}")
    else:
        print(f"          prev: {prev_name}")
        print(f"          next: {next_name}")
