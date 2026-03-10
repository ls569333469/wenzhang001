"""
P35 F2: 一次性迁移脚本
将 reports/research/projects/ 目录下的 113 份策略官报告导入 ChromaDB research_reports

用法: python scripts/migrate_reports_to_chroma.py
"""
import sys
import re
from pathlib import Path

# 确保可以导入 app 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.chroma_service import get_chroma_service

PROJECTS_DIR = Path(__file__).parent.parent.parent / "reports" / "research" / "projects"


def extract_metadata(filepath: Path) -> dict:
    """从文件名和内容中提取 metadata"""
    stem = filepath.stem  # e.g. "0G_Labs_20260307"

    # 从文件名提取 date (最后 8 位数字)
    date_match = re.search(r"(\d{8})$", stem)
    date = date_match.group(1) if date_match else ""

    # 从文件名提取 twitter handle (去掉日期后缀)
    twitter = stem
    if date_match:
        twitter = stem[:date_match.start()].rstrip("_")

    # 从文件第一行提取项目名
    content = filepath.read_text(encoding="utf-8")
    name_match = re.match(r"# 🔬\s*(.+?)\s*[—–-]\s*投研报告", content)
    name = name_match.group(1).strip() if name_match else twitter

    return {
        "twitter": f"@{twitter}",
        "date": date,
        "name": name,
        "content": content,
    }


def main():
    if not PROJECTS_DIR.exists():
        print(f"❌ 目录不存在: {PROJECTS_DIR}")
        return

    files = sorted(PROJECTS_DIR.glob("*.md"))
    print(f"📁 发现 {len(files)} 份报告文件")

    if not files:
        return

    chroma = get_chroma_service()
    success = 0
    errors = 0

    for f in files:
        try:
            meta = extract_metadata(f)
            if not meta["date"] or not meta["content"]:
                print(f"  ⚠️ 跳过 {f.name}: 无日期或内容")
                errors += 1
                continue

            chroma.add_research_report(
                twitter=meta["twitter"],
                date=meta["date"],
                name=meta["name"],
                content=meta["content"],
            )
            success += 1
        except Exception as e:
            print(f"  ❌ {f.name}: {e}")
            errors += 1

    # 统计
    stats = chroma.get_stats()
    print(f"\n✅ 迁移完成: {success} 成功, {errors} 失败")
    print(f"📊 research_reports: {stats.get('research_reports', 0)} 条记录")


if __name__ == "__main__":
    main()
