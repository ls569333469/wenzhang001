"""输出到文件看列名"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from app.services.google_sheets_source import google_sheets_source as gs
gs._init_client()
ws = gs._spreadsheet.worksheet("风格_半佛")
rows = ws.get_all_values()
with open("reports/columns_debug.txt", "w", encoding="utf-8") as f:
    f.write(f"总行数: {len(rows)}\n\n")
    f.write(f"第1行(列头):\n")
    for i, col in enumerate(rows[0]):
        f.write(f"  col[{i}] = '{col}'\n")
    f.write(f"\n第2行(数据):\n")
    for i, val in enumerate(rows[1]):
        f.write(f"  col[{i}] = '{val[:100]}'\n")
    f.write(f"\n第3行(数据):\n")
    for i, val in enumerate(rows[2]):
        f.write(f"  col[{i}] = '{val[:100]}'\n")
print("Done")
