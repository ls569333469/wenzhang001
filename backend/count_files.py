import os
from pathlib import Path

base = Path('data/Web3素材')
folders = sorted(base.iterdir())

print("| 序号 | 赛道 | JSON数量 |")
print("|------|------|----------|")

total = 0
for i, f in enumerate(folders):
    count = len(list(f.glob("*.json")))
    total += count
    name = f.name if len(f.name) <= 30 else f.name[:27] + "..."
    print(f"| {i+1} | {name} | {count} |")

print(f"|  | **总计** | **{total}** |")
