#!/usr/bin/env python
"""
CSV 批量导出脚本
===============
将已清洗但未成功上传的数据导出为 CSV，供 Lark 手动导入。

Usage:
    python scripts/export_to_csv.py --folder data/Web2风格/半佛仙人 --author banfo --style banfo
"""

import os
import sys
import csv
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Import from cleaner_cli
from tools.cleaner_cli import (
    AsyncLLMProvider,
    CleanedSnippet,
    SHELL_MINER_PROMPT,
    SNIPPET_TYPE_MAP,
    EMOTION_MAP,
    prepare_lark_fields,
    CHECKPOINT_FILE,
    CHUNK_SIZE,
    get_content_hash
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"

async def process_file_to_csv(
    file_path: Path,
    author: str,
    style: str,
    provider: AsyncLLMProvider,
    source_category: str = "Shell"
) -> list:
    """处理单个文件并返回记录列表"""
    records = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if len(content) < 50:
            return records
            
        # 分片处理
        chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        
        for chunk in chunks:
            prompt = SHELL_MINER_PROMPT.format(
                current_date=datetime.now().strftime("%Y-%m-%d"),
                author=author
            )
            
            try:
                response = await provider.client.chat.completions.create(
                    model=provider.model_name,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"【文章片段】\n{chunk}"}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                result_text = response.choices[0].message.content
                result = json.loads(result_text)
                snippets = result.get("snippets", [])
                
                print(f"  LLM返回: {len(snippets)} 条")
                
                for s in snippets:
                    if s.get("quality_score", 5) < 3:
                        continue  # 跳过低质量
                    
                    snippet = CleanedSnippet(
                        original_text=s.get("original_text", ""),
                        clean_text=s.get("clean_text", ""),
                        snippet_type=s.get("snippet_type", "Quote"),
                        logic_pattern=s.get("logic_pattern", ""),
                        emotional_valence=s.get("emotional_valence", "Neutral"),
                        quality_score=s.get("quality_score", 5)
                    )
                    
                    fields = prepare_lark_fields(snippet, author, style, source_category)
                    records.append(fields)
                    
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON解析失败: {e}")
            except Exception as e:
                print(f"  ❌ 处理异常: {e}")
                
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
    
    return records


async def export_folder_to_csv(
    folder: str,
    author: str,
    style: str,
    model: str = "deepseek",
    source_category: str = "Shell",
    skip_processed: bool = True
):
    """将整个文件夹的数据导出为 CSV"""
    
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"❌ 文件夹不存在: {folder}")
        return
    
    # 初始化 LLM
    provider = AsyncLLMProvider(model)
    provider.connect()
    print(f"✅ 已连接 {model} 模型: {provider.model_name}")
    
    # 获取文件列表
    txt_files = sorted(folder_path.glob("*.txt"))
    print(f"📁 找到 {len(txt_files)} 个 TXT 文件")
    
    # 加载已处理记录
    processed_files = set()
    if skip_processed and CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
                processed_files = set(checkpoint.get("processed_files", []))
            print(f"📋 已处理文件: {len(processed_files)} 个")
        except:
            pass
    
    # 过滤待处理文件
    pending_files = [f for f in txt_files if str(f) not in processed_files]
    print(f"⏳ 待处理文件: {len(pending_files)} 个")
    
    if not pending_files:
        print("✅ 所有文件已处理完成！")
        return
    
    # 收集所有记录
    all_records = []
    
    for i, file_path in enumerate(pending_files[:50]):  # 限制每批50个
        print(f"\n[{i+1}/{len(pending_files)}] 处理: {file_path.name}")
        records = await process_file_to_csv(file_path, author, style, provider, source_category)
        all_records.extend(records)
        print(f"  ✅ 提取 {len(records)} 条记录")
    
    # 导出 CSV
    if all_records:
        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = OUTPUT_DIR / f"lark_import_{style}_{timestamp}.csv"
        
        # 写入 CSV (UTF-8 with BOM for Excel compatibility)
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            if source_category.lower() == "shell":
                fieldnames = ["内容", "博主", "片段类型", "情绪", "内容指纹", "质量评分", "状态", "逻辑公式", "风格标签"]
            else:
                fieldnames = ["标题", "内容", "赛道分类", "内容类型", "来源文件", "来源链接", "内容指纹", "质量评分", "状态"]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for record in all_records:
                # 处理风格标签列表
                if "风格标签" in record and isinstance(record["风格标签"], list):
                    record["风格标签"] = ",".join(record["风格标签"])
                writer.writerow(record)
        
        print(f"\n" + "=" * 60)
        print(f"🎉 导出完成！")
        print(f"📄 CSV 文件: {csv_path}")
        print(f"📊 总记录数: {len(all_records)} 条")
        print(f"=" * 60)
        print(f"\n📋 下一步操作:")
        print(f"1. 打开 Lark Bitable 网页版")
        print(f"2. 点击 '导入' → 选择 '{csv_path.name}'")
        print(f"3. 映射字段后确认导入")
    else:
        print("⚠️ 没有提取到有效记录")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导出清洗数据为 CSV")
    parser.add_argument("--folder", required=True, help="数据文件夹路径")
    parser.add_argument("--author", required=True, help="作者/博主名")
    parser.add_argument("--style", required=True, help="风格标签")
    parser.add_argument("--model", default="deepseek", help="LLM 模型 (deepseek/doubao/gemini)")
    parser.add_argument("--category", default="Shell", help="数据类型 (Shell/Kernel)")
    
    args = parser.parse_args()
    
    asyncio.run(export_folder_to_csv(
        folder=args.folder,
        author=args.author,
        style=args.style,
        model=args.model,
        source_category=args.category
    ))
