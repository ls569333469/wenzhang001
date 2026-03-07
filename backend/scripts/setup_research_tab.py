"""
P32-B1: 创建 投研记录 Tab + 导入历史数据
运行: cd backend && python scripts/setup_research_tab.py
"""
import os
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.google_sheets_source import google_sheets_source

TAB_NAME = "投研记录"
HEADERS = ["项目名", "Twitter", "赛道", "上次分析时间", "催化剂摘要", "评级", "一句话摘要", "发布状态", "侦察次数"]

PROJECTS_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "projects"


def extract_info_from_report(filepath: Path) -> dict:
    """从策略官报告中提取摘要和催化剂"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    info = {}

    # 提取项目定位（第一段有效文字）
    pos_match = re.search(
        r"##\s*(?:📊\s*项目定位|\d+\.\s*项目概要[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        content, re.DOTALL,
    )
    if pos_match:
        text = pos_match.group(1).strip()
        lines = [
            l.strip() for l in text.split("\n")
            if l.strip()
            and not l.strip().startswith("|")
            and not l.strip().startswith("-")
            and not l.strip().startswith("**")
            and len(l.strip()) > 8
        ]
        if lines:
            info["summary"] = lines[0][:60]

    # 提取催化剂
    cat_match = re.search(
        r"##\s*(?:🔥\s*近期催化剂|\d+\.\s*近期催化剂[^\n]*)\s*\n+(.*?)(?=\n##|\Z)",
        content, re.DOTALL,
    )
    if cat_match:
        for l in cat_match.group(1).strip().split("\n"):
            l = l.strip().lstrip("-•·* ")
            if l and not l.startswith("|") and not l.startswith("#"):
                info["catalyst"] = l[:30]
                break

    # 提取赛道（从第一行或标题猜测）
    # 尝试找到类似 "赛道: xxx" 的模式
    track_match = re.search(r"赛道[：:]\s*(.+)", content)
    if track_match:
        info["category"] = track_match.group(1).strip()[:20]

    return info


def main():
    print("=" * 60)
    print("  P32-B1: 创建 投研记录 Tab + 导入历史数据")
    print("=" * 60)

    # 连接 Sheets
    if not google_sheets_source._init_client():
        print("❌ Google Sheets 连接失败")
        return

    spreadsheet = google_sheets_source._spreadsheet
    print(f"✅ 已连接到 Google Sheets\n")

    # 创建或获取 Tab
    try:
        ws = spreadsheet.worksheet(TAB_NAME)
        print(f"📋 Tab '{TAB_NAME}' 已存在")
        existing = ws.get_all_values()
        if len(existing) > 1:
            print(f"  ⚠️ 已有 {len(existing) - 1} 条数据，跳过导入")
            print("  如需重新导入，请先手动清空 Tab")
            return
    except Exception:
        ws = spreadsheet.add_worksheet(title=TAB_NAME, rows=100, cols=len(HEADERS))
        print(f"🆕 Tab '{TAB_NAME}' 已创建")

    # 写入表头
    ws.update("A1:I1", [HEADERS])
    print(f"📝 表头写入: {HEADERS}")

    # 扫描历史报告
    if not PROJECTS_DIR.exists():
        print(f"\n⚠️ 项目目录不存在: {PROJECTS_DIR}")
        print("  跳过历史导入")
        return

    report_files = sorted(PROJECTS_DIR.glob("*_*.md"))
    print(f"\n📂 扫描到 {len(report_files)} 个历史报告")

    rows = []
    seen_names = set()

    for f in report_files:
        parts = f.stem.rsplit("_", 1)
        if len(parts) != 2:
            continue

        name = parts[0]
        date_str = parts[1]

        # 同名项目只保留最新的
        name_key = name.lower()
        if name_key in seen_names:
            continue
        seen_names.add(name_key)

        # 从报告内容提取信息
        info = extract_info_from_report(f)

        # 格式化日期
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
            time_str = dt.strftime("%Y-%m-%d 00:00")
        except ValueError:
            time_str = date_str

        row = [
            name,                              # 项目名
            "",                                # Twitter
            info.get("category", ""),          # 赛道
            time_str,                          # 上次分析时间
            info.get("catalyst", ""),          # 催化剂摘要
            "",                                # 评级
            info.get("summary", ""),           # 一句话摘要
            "已分析",                          # 发布状态
            "1",                               # 侦察次数
        ]
        rows.append(row)
        print(f"  📄 {name:20s} | {time_str} | {info.get('summary', '(无)')[:30]}")

    if rows:
        # 按分析时间倒序
        rows.sort(key=lambda r: r[3], reverse=True)
        ws.update(f"A2:I{len(rows) + 1}", rows)
        print(f"\n✅ 导入 {len(rows)} 条历史记录到 '{TAB_NAME}' Tab")
    else:
        print("\n⚠️ 没有可导入的历史记录")

    print("\n" + "=" * 60)
    print("  ✅ B1 完成！")
    print(f"  📊 Tab: {TAB_NAME}")
    print(f"  📝 记录数: {len(rows)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
