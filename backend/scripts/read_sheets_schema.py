"""读取 Google Sheets 所有工作表名 + 表头 - 输出到文件"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source

if not google_sheets_source._init_client():
    print("ERROR: 无法连接 Google Sheets")
    sys.exit(1)

spreadsheet = google_sheets_source._spreadsheet

output = []
output.append(f"表单: {spreadsheet.title}")
output.append(f"ID: {spreadsheet.id}")
output.append("")

worksheets = spreadsheet.worksheets()
output.append(f"共 {len(worksheets)} 个工作表:")
output.append("-" * 60)

for ws in worksheets:
    output.append(f"\n[{ws.title}]  ({ws.row_count} rows x {ws.col_count} cols)")
    try:
        headers = ws.row_values(1)
        if headers:
            output.append(f"  表头: {' | '.join(headers)}")
            col_a = ws.col_values(1)
            data_count = len([v for v in col_a[1:] if v.strip()]) if len(col_a) > 1 else 0
            output.append(f"  实际数据: ~{data_count} 行")
        else:
            output.append("  (空表)")
    except Exception as e:
        output.append(f"  错误: {e}")

result = "\n".join(output)
print(result)

# 也写到文件
with open("scripts/sheets_schema_output.txt", "w", encoding="utf-8") as f:
    f.write(result)
print("\n\n已保存到 scripts/sheets_schema_output.txt")
