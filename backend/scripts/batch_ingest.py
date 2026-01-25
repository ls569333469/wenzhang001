"""
Quantum Studio - 分批执行入库脚本
==================================
将 42 个 Web3 素材文件夹分成 9 批执行，每批 5 个文件夹。
每批完成后暂停，等待用户确认后继续下一批。

Usage:
    cd backend
    python -m scripts.batch_ingest
    
    # 从指定批次开始
    python -m scripts.batch_ingest --start-batch 3
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    print("Missing rich. Run: pip install rich")
    sys.exit(1)

console = Console()

# ==========================================
# 配置区
# ==========================================
WEB3_DATA_DIR = Path(__file__).parent.parent / "data" / "Web3素材"
BATCH_SIZE = 5  # 每批文件夹数量

# ==========================================
# 主逻辑
# ==========================================

def get_all_folders():
    """获取所有 Web3 素材文件夹"""
    folders = sorted([f.name for f in WEB3_DATA_DIR.iterdir() if f.is_dir()])
    return folders

def split_into_batches(folders, batch_size):
    """将文件夹列表分成批次"""
    batches = []
    for i in range(0, len(folders), batch_size):
        batches.append(folders[i:i+batch_size])
    return batches

def run_ingest(folder_name):
    """运行入库脚本处理单个文件夹"""
    cmd = [
        sys.executable, "-m", "scripts.ingest_optimized",
        "--folder", folder_name
    ]
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, capture_output=False)
    return result.returncode == 0

def print_batch_summary(batch_num, total_batches, folders, results):
    """打印批次执行摘要"""
    table = Table(title=f"Batch {batch_num}/{total_batches} 执行结果")
    table.add_column("文件夹", style="cyan")
    table.add_column("状态", justify="center")
    
    for folder, success in zip(folders, results):
        status = "✅ 成功" if success else "❌ 失败"
        table.add_row(folder[:30] + "..." if len(folder) > 30 else folder, status)
    
    console.print(table)
    
    success_count = sum(results)
    console.print(f"\n📊 本批成功: {success_count}/{len(folders)}")

def print_overall_progress(current_batch, total_batches, all_results):
    """打印整体进度"""
    total_folders = sum(len(r) for r in all_results)
    total_success = sum(sum(r) for r in all_results)
    
    progress = (current_batch / total_batches) * 100
    
    console.print(Panel(
        f"📈 整体进度: {current_batch}/{total_batches} 批 ({progress:.0f}%)\n"
        f"📁 已处理文件夹: {total_folders}\n"
        f"✅ 成功: {total_success} | ❌ 失败: {total_folders - total_success}",
        title="进度报告"
    ))

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="分批执行入库脚本")
    parser.add_argument("--start-batch", type=int, default=1, help="从第几批开始 (默认 1)")
    args = parser.parse_args()
    
    # 获取所有文件夹并分批
    folders = get_all_folders()
    batches = split_into_batches(folders, BATCH_SIZE)
    total_batches = len(batches)
    
    console.print("=" * 60)
    console.print("🚀 Quantum Studio - 分批执行入库")
    console.print("=" * 60)
    console.print(f"📁 总文件夹数: {len(folders)}")
    console.print(f"📦 总批次数: {total_batches}")
    console.print(f"📊 每批文件夹: {BATCH_SIZE}")
    console.print(f"⏱️ 预计总时间: ~{total_batches * 15} 分钟")
    console.print()
    
    # 显示批次计划
    table = Table(title="执行计划")
    table.add_column("批次", justify="center", style="cyan")
    table.add_column("文件夹", style="white")
    table.add_column("状态", justify="center")
    
    for i, batch in enumerate(batches, 1):
        folders_str = ", ".join([f[:15] + "..." if len(f) > 15 else f for f in batch[:3]])
        if len(batch) > 3:
            folders_str += f" (+{len(batch)-3})"
        status = "⏳ 待执行" if i >= args.start_batch else "⏭️ 已跳过"
        table.add_row(f"Batch {i}", folders_str, status)
    
    console.print(table)
    console.print()
    
    # 确认开始
    if args.start_batch == 1:
        console.print("[yellow]按 Enter 开始执行，Ctrl+C 取消...[/yellow]")
        input()
    
    # 执行批次
    all_results = []
    start_time = datetime.now()
    
    for batch_num, batch_folders in enumerate(batches, 1):
        if batch_num < args.start_batch:
            all_results.append([True] * len(batch_folders))  # 跳过的批次标记为成功
            continue
        
        console.print()
        console.print(Panel(
            f"开始执行 Batch {batch_num}/{total_batches}\n"
            f"包含文件夹: {', '.join(batch_folders)}",
            title=f"🚀 Batch {batch_num}",
            border_style="green"
        ))
        console.print()
        
        # 执行本批次
        batch_results = []
        for folder in batch_folders:
            console.print(f"📂 处理: {folder}")
            success = run_ingest(folder)
            batch_results.append(success)
            console.print()
        
        all_results.append(batch_results)
        
        # 打印批次摘要
        print_batch_summary(batch_num, total_batches, batch_folders, batch_results)
        print_overall_progress(batch_num, total_batches, all_results)
        
        # 如果不是最后一批，暂停等待确认
        if batch_num < total_batches:
            console.print()
            console.print("[yellow]=" * 60)
            console.print(f"[yellow]⏸️ Batch {batch_num} 完成！")
            console.print(f"[yellow]   按 Enter 继续 Batch {batch_num + 1}，输入 'q' 退出...")
            console.print("[yellow]=" * 60)
            
            user_input = input().strip().lower()
            if user_input == 'q':
                console.print("[red]用户终止执行[/red]")
                break
    
    # 最终报告
    end_time = datetime.now()
    duration = end_time - start_time
    
    console.print()
    console.print("=" * 60)
    console.print("🎉 全部执行完成!")
    console.print("=" * 60)
    
    total_folders = sum(len(r) for r in all_results)
    total_success = sum(sum(r) for r in all_results)
    
    console.print(f"📁 总处理文件夹: {total_folders}")
    console.print(f"✅ 成功: {total_success}")
    console.print(f"❌ 失败: {total_folders - total_success}")
    console.print(f"⏱️ 总耗时: {duration}")
    
    # 保存执行记录
    log_file = Path(__file__).parent.parent / "data" / f"batch_ingest_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"执行时间: {start_time} - {end_time}\n")
        f.write(f"总耗时: {duration}\n")
        f.write(f"总处理: {total_folders}, 成功: {total_success}, 失败: {total_folders - total_success}\n\n")
        
        for batch_num, (batch_folders, results) in enumerate(zip(batches, all_results), 1):
            f.write(f"\nBatch {batch_num}:\n")
            for folder, success in zip(batch_folders, results):
                f.write(f"  {'✅' if success else '❌'} {folder}\n")
    
    console.print(f"\n📝 执行日志已保存: {log_file.name}")


if __name__ == "__main__":
    asyncio.run(main())
