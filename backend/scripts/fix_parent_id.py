"""
P29 v3: 父记录关联修复 — 全部优化策略
Pass 1: 子串匹配（原文去空白）
Pass 2: 去标点匹配（解决标点差异问题）
Pass 3: 短指纹匹配（10字，解决短内容问题）
Pass 4: 有序传播 + 边界精确匹配
Pass 5: 最终邻居传播（扩大搜索范围到 ±50 行）
"""
import csv
import os
import hashlib
import re
import time
from pathlib import Path
from collections import Counter

CSV_PATH = r"D:\AI_Projects\Web2风格\banfo66.csv"
TXT_DIR = r"D:\AI_Projects\Web2风格\半佛仙人"
OUTPUT_PATH = r"D:\AI_Projects\Web2风格\banfo66_with_parent_v3.csv"

# === 加载原文 ===
print("Loading articles...")
articles = {}
for root, dirs, files in os.walk(TXT_DIR):
    for f in files:
        if f.endswith(".txt"):
            with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                text = fp.read()
            name_key = Path(f).stem
            pid = hashlib.md5(name_key.encode("utf-8")).hexdigest()[:12]
            text_nospace = text.replace("\r", "").replace("\n", "").replace(" ", "")
            text_nopunc = re.sub(r'[^\u4e00-\u9fff\w]', '', text)  # 只保留中文+字母数字
            articles[pid] = {"name_key": name_key, "text_nospace": text_nospace, "text_nopunc": text_nopunc}
print(f"  {len(articles)} articles")

# === 加载CSV ===
print("Loading CSV...")
with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)
if "父记录" not in fieldnames:
    fieldnames.append("父记录")
# 清空所有父记录（重新匹配）
for r in rows:
    r["父记录"] = ""
print(f"  {len(rows)} rows")

start = time.time()

# === Pass 1 + 2 + 3: 全库子串匹配（三种清洗策略）===
print("\nPass 1-3: Full-text matching (3 strategies)...")
for i, row in enumerate(rows):
    content = row.get("内容", "").strip()
    if not content:
        continue
    
    content_nospace = content.replace("\r", "").replace("\n", "").replace(" ", "")
    content_nopunc = re.sub(r'[^\u4e00-\u9fff\w]', '', content)
    
    # Strategy 1: 去空白，前80字
    fp = content_nospace[:80] if len(content_nospace) > 80 else content_nospace
    for pid, art in articles.items():
        if fp and fp in art["text_nospace"]:
            row["父记录"] = pid
            break
    if row["父记录"]:
        continue
    
    # Strategy 2: 去标点
    if content_nopunc and len(content_nopunc) >= 8:
        for pid, art in articles.items():
            if content_nopunc in art["text_nopunc"]:
                row["父记录"] = pid
                break
    if row["父记录"]:
        continue
    
    # Strategy 3: 短指纹（前10字，只保留唯一匹配）
    if len(content_nospace) >= 10:
        short_fp = content_nospace[:10]
        matches = [pid for pid, art in articles.items() if short_fp in art["text_nospace"]]
        if len(matches) == 1:
            row["父记录"] = matches[0]

p1_matched = sum(1 for r in rows if r["父记录"])
print(f"  After Pass 1-3: {p1_matched}/{len(rows)} ({p1_matched/len(rows)*100:.1f}%)")

# === Pass 4: 有序传播 + 边界精确匹配 ===
print("\nPass 4: Ordered propagation + boundary matching...")
p4_filled = 0

# 找未匹配的连续区间
gaps = []
i = 0
while i < len(rows):
    if not rows[i]["父记录"]:
        gap_start = i
        while i < len(rows) and not rows[i]["父记录"]:
            i += 1
        gaps.append((gap_start, i - 1))
    else:
        i += 1

for gap_start, gap_end in gaps:
    prev_pid = rows[gap_start - 1]["父记录"] if gap_start > 0 else ""
    next_pid = rows[gap_end + 1]["父记录"] if gap_end < len(rows) - 1 else ""
    
    if prev_pid and next_pid and prev_pid == next_pid:
        # 前后同一篇，直接继承
        for j in range(gap_start, gap_end + 1):
            rows[j]["父记录"] = prev_pid
            p4_filled += 1
    else:
        # 边界区间：逐行尝试匹配前后两篇
        candidates = list(set(filter(None, [prev_pid, next_pid])))
        for j in range(gap_start, gap_end + 1):
            content = rows[j].get("内容", "").strip()
            if not content:
                continue
            content_nopunc = re.sub(r'[^\u4e00-\u9fff\w]', '', content)
            
            # 尝试匹配前后两篇
            for pid in candidates:
                if pid in articles and content_nopunc and content_nopunc in articles[pid]["text_nopunc"]:
                    rows[j]["父记录"] = pid
                    p4_filled += 1
                    break

print(f"  Pass 4 filled: {p4_filled}")

# === Pass 5: 最终邻居传播（扩大范围 ±50）===
print("\nPass 5: Extended neighbor propagation (range 50)...")
p5_filled = 0
for i in range(len(rows)):
    if rows[i]["父记录"]:
        continue
    
    content = rows[i].get("内容", "").strip()
    content_nopunc = re.sub(r'[^\u4e00-\u9fff\w]', '', content) if content else ""
    
    # 寻找最近的已匹配邻居（±50范围）
    prev_pid = ""
    next_pid = ""
    for j in range(i - 1, max(i - 50, -1), -1):
        if rows[j]["父记录"]:
            prev_pid = rows[j]["父记录"]
            break
    for j in range(i + 1, min(i + 50, len(rows))):
        if rows[j]["父记录"]:
            next_pid = rows[j]["父记录"]
            break
    
    # 如果前后同一篇，直接继承
    if prev_pid and prev_pid == next_pid:
        rows[i]["父记录"] = prev_pid
        p5_filled += 1
        continue
    
    # 前后不同，尝试匹配两篇
    for pid in [prev_pid, next_pid]:
        if pid and pid in articles and content_nopunc:
            if content_nopunc in articles[pid]["text_nopunc"]:
                rows[i]["父记录"] = pid
                p5_filled += 1
                break
    
    # 还是没匹配到，如果只有一个邻居就用它
    if not rows[i]["父记录"]:
        if prev_pid and not next_pid:
            rows[i]["父记录"] = prev_pid
            p5_filled += 1
        elif next_pid and not prev_pid:
            rows[i]["父记录"] = next_pid
            p5_filled += 1

print(f"  Pass 5 filled: {p5_filled}")

# === 统计 ===
total_matched = sum(1 for r in rows if r["父记录"])
still_empty = len(rows) - total_matched
elapsed = time.time() - start
print(f"\n=== FINAL RESULT ({elapsed:.1f}s) ===")
print(f"  Total:     {len(rows)}")
print(f"  Matched:   {total_matched} ({total_matched/len(rows)*100:.1f}%)")
print(f"  Remaining: {still_empty} ({still_empty/len(rows)*100:.1f}%)")

pids = [r["父记录"] for r in rows if r["父记录"]]
pid_counter = Counter(pids)
print(f"  Unique articles: {len(pid_counter)}")
print(f"  Avg fragments/article: {len(pids)/max(len(pid_counter),1):.1f}")

if still_empty > 0:
    print(f"\n  Remaining unmatched samples:")
    shown = 0
    for i, r in enumerate(rows):
        if not r["父记录"] and shown < 5:
            print(f"    Row {i}: [{r.get('片段类型','')}] {r.get('内容','')[:60]}")
            shown += 1

# === 写入 ===
print(f"\nWriting {OUTPUT_PATH}...")
with open(OUTPUT_PATH, "w", encoding="utf-8-sig", newline="") as fp:
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
print("Done!")
