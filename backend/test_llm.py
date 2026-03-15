#!/usr/bin/env python3
"""
容器内 LLM 快速诊断脚本
用法: docker exec quantum-studio-backend-1 python /app/test_llm.py
"""
import os
import sys
import json

print("=" * 60)
print("🔍 Quantum Studio — LLM 容器诊断")
print("=" * 60)

# 1. 检查环境变量
print("\n📋 环境变量检查:")
keys = ["ARK_API_KEY", "GOOGLE_GENAI_API_KEY", "SURF_API_KEY", "GROK_API_KEY", "TWITTER_TOKEN"]
for k in keys:
    v = os.environ.get(k, "")
    if v:
        print(f"  ✅ {k} = {v[:6]}****{v[-4:]}")
    else:
        print(f"  ❌ {k} = 空")

# 2. 检查 user_config.json
print("\n📋 user_config.json 检查:")
config_path = "/app/config/user_config.json"
if os.path.exists(config_path):
    with open(config_path) as f:
        cfg = json.load(f)
    print(f"  文件存在: {config_path}")
    for k, v in cfg.items():
        if "key" in k.lower() or "token" in k.lower():
            if v:
                print(f"  ✅ {k} = {str(v)[:6]}****")
            else:
                print(f"  ⚠️ {k} = 空 (会覆盖 env!)")
        else:
            print(f"  📌 {k} = {v}")
else:
    print(f"  文件不存在 (将用 env 变量)")

# 3. 测试 generate_text
print("\n📋 LLM 调用测试:")
try:
    sys.path.insert(0, "/app")
    from app.core.llm import generate_text, get_client, get_config_api_key
    
    # 先看 get_config_api_key 返回什么
    for provider_key in ["doubao", "volcengine"]:
        result = get_config_api_key(provider_key)
        if result:
            print(f"  get_config_api_key('{provider_key}') = {result[:6]}****")
        else:
            print(f"  get_config_api_key('{provider_key}') = None/空")
    
    # 实际调用
    print("\n  🚀 测试 volcengine generate_text...")
    result = generate_text(
        prompt="回复'测试成功'两个字即可",
        provider="volcengine",
        temperature=0.1,
        max_tokens=20,
    )
    print(f"  ✅ volcengine 成功: {result}")
    
except Exception as e:
    print(f"  ❌ volcengine 失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 检查推文文件
print("\n📋 推文文件检查:")
import glob
tweet_files = sorted(glob.glob("/app/reports/research/tweets_*"))
if tweet_files:
    for f in tweet_files[-3:]:
        size = os.path.getsize(f)
        print(f"  📄 {os.path.basename(f)} ({size} bytes)")
else:
    print("  ❌ 无推文文件")

report_files = sorted(glob.glob("/app/reports/research/daily_research_*"))
if report_files:
    for f in report_files[-3:]:
        size = os.path.getsize(f)
        print(f"  📄 {os.path.basename(f)} ({size} bytes)")

print("\n" + "=" * 60)
print("诊断完成")
