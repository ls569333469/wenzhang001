#!/usr/bin/env python
"""
调试写作流程字段调用
"""
import json
import sys
sys.path.insert(0, '.')

from app.services.sync_service import sync_service

print("=" * 60)
print("📊 调查写作流程调用的字段")
print("=" * 60)

# 1. 加载本地样本库
library = sync_service.load_library()
print(f"\n📁 本地 style_library.json 记录数: {len(library)}")

if library:
    # 2. 查看第一条记录的所有字段
    first_item = library[0]
    print(f"\n📋 样本记录包含的字段:")
    for key, value in first_item.items():
        val_preview = str(value)[:50] + "..." if len(str(value)) > 50 else value
        print(f"   - {key}: {val_preview}")
    
    # 3. 模拟 writer 调用 get_samples
    print("\n" + "=" * 60)
    print("🔍 模拟 Writer Agent 调用 get_samples()")
    print("=" * 60)
    
    # 获取所有不同的 style 值
    styles = set()
    for item in library:
        if item.get("style"):
            styles.add(item.get("style"))
    print(f"\n🎨 库中的 style 值: {styles}")
    
    # 模拟调用
    test_style = "mimeng"
    test_emotion = None
    samples = sync_service.get_samples(style=test_style, emotion=test_emotion, count=3)
    
    print(f"\n📥 调用 get_samples(style='{test_style}', emotion={test_emotion}, count=3)")
    print(f"   返回 {len(samples)} 条样本:")
    
    for i, s in enumerate(samples):
        print(f"\n   --- 样本 {i+1} ---")
        for key, value in s.items():
            val_preview = str(value)[:80] + "..." if len(str(value)) > 80 else value
            print(f"   {key}: {val_preview}")

    # 4. 检查 writer.py 使用的字段
    print("\n" + "=" * 60)
    print("📝 Writer Agent 使用的字段 (来自 writer.py):")
    print("=" * 60)
    print("""
    samples_text = ""
    for i, s in enumerate(samples, 1):
        sample_content = s['content']       # ✅ 使用 content
        logic_pattern = s.get('logic_pattern', '')  # ✅ 使用 logic_pattern
        snippet_type = s.get('snippet_type', '')    # ✅ 使用 snippet_type
        # 截断过长样本以节省 token
        if len(sample_content) > 500:
            sample_content = sample_content[:500] + "..."
        samples_text += f"\\n--- Example {i} ---\\n"
        if logic_pattern:
            samples_text += f"[逻辑公式: {logic_pattern}]\\n"
        if snippet_type:
            samples_text += f"[类型: {snippet_type}]\\n"
        samples_text += f"{sample_content}\\n"
    """)

else:
    print("⚠️ 本地样本库为空!")

print("\n" + "=" * 60)
print("📋 总结: 写作流程使用的字段")
print("=" * 60)
print("""
┌────────────────────────────────────────────────────────────┐
│  数据源: 本地 style_library.json (不是 Lark 实时查询)       │
├────────────────────────────────────────────────────────────┤
│  筛选条件:                                                 │
│    - style (匹配模式如 mimeng/diary/insider)               │
│    - emotional_valence 或 emotion (可选)                   │
├────────────────────────────────────────────────────────────┤
│  Writer 实际使用的字段:                                    │
│    ✅ content       → 样本内容,注入到 Few-Shot 提示词       │
│    ✅ logic_pattern → 逻辑公式,帮助 LLM 学习写作模式        │
│    ✅ snippet_type  → 片段类型 (Hook/Body/CTA/Quote)        │
├────────────────────────────────────────────────────────────┤
│  注意: 这些字段值来自 Lark → sync_service → 本地JSON       │
│        如果 Lark 字段值有中英文不一致,不会影响写作流程      │
└────────────────────────────────────────────────────────────┘
""")
