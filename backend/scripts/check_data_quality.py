"""检查 Knowledge_Repo 数据质量"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from app.core.lark_client import lark_client
import requests

token = lark_client._get_token()
base_token = os.getenv('LARK_BASE_TOKEN')
table_id = os.getenv('LARK_KNOWLEDGE_TABLE_ID')
base_url = 'https://open.larksuite.com/open-apis'

headers = {'Authorization': f'Bearer {token}'}

# 获取最新的 15 条记录
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records'
params = {'page_size': 15}
resp = requests.get(url, headers=headers, params=params)
records = resp.json().get('data', {}).get('items', [])

print(f'=== Knowledge_Repo 数据质量检查报告 ===')
print(f'总记录数: {resp.json().get("data", {}).get("total", 0)}')
print(f'检查样本: {len(records)} 条\n')

# 统计指标
issues = {
    'empty_summary': 0,
    'long_summary': 0,  # 超过 200 字
    'empty_keywords': 0,
    'empty_info_depth': 0,
    'empty_fact_type': 0,
    'v3_fields_used': 0,
    'legacy_fields_used': 0,
}

print('=' * 60)

for i, r in enumerate(records):
    fields = r.get('fields', {})
    
    # v3.0 字段
    summary_v3 = fields.get('核心摘要', '')
    info_depth = fields.get('信息深度', '')
    fact_type = fields.get('事实类型', '')
    
    # 旧字段
    summary_old = fields.get('摘要', '')
    content_type = fields.get('内容类型', '')
    content_old = fields.get('内容', '')
    
    # 通用字段
    title = fields.get('标题', '')
    keywords = fields.get('关键词', '')
    topic = fields.get('赛道分类', '')
    content_new = fields.get('正文原文', '')
    
    # 判断使用的是 v3 还是旧字段
    if summary_v3 or info_depth or fact_type:
        issues['v3_fields_used'] += 1
        summary = summary_v3
    else:
        issues['legacy_fields_used'] += 1
        summary = summary_old
    
    # 检查问题
    if not summary:
        issues['empty_summary'] += 1
    elif len(str(summary)) > 200:
        issues['long_summary'] += 1
    
    if not keywords:
        issues['empty_keywords'] += 1
    if not info_depth:
        issues['empty_info_depth'] += 1
    if not fact_type and not content_type:
        issues['empty_fact_type'] += 1
    
    # 打印详情
    print(f'\n--- 记录 {i+1} ---')
    print(f'标题: {str(title)[:40]}{"..." if len(str(title)) > 40 else ""}')
    print(f'赛道: {topic}')
    
    if summary_v3:
        print(f'核心摘要 (v3): {str(summary_v3)[:80]}...')
        print(f'  → 长度: {len(str(summary_v3))} 字')
    elif summary_old:
        print(f'摘要 (旧): {str(summary_old)[:80]}...')
        print(f'  → 长度: {len(str(summary_old))} 字')
    else:
        print(f'摘要: [空!]')
    
    print(f'关键词: {keywords if keywords else "[空!]"}')
    print(f'信息深度: {info_depth if info_depth else "[空!]"}')
    print(f'事实类型: {fact_type if fact_type else content_type if content_type else "[空!]"}')
    
    content = content_new or content_old
    print(f'正文长度: {len(str(content))} 字')

print('\n' + '=' * 60)
print('=== 问题统计 ===')
print(f'使用 v3.0 字段: {issues["v3_fields_used"]} 条')
print(f'使用旧字段: {issues["legacy_fields_used"]} 条')
print(f'摘要为空: {issues["empty_summary"]} 条')
print(f'摘要过长 (>200字): {issues["long_summary"]} 条')
print(f'关键词为空: {issues["empty_keywords"]} 条')
print(f'信息深度为空: {issues["empty_info_depth"]} 条')
print(f'事实类型为空: {issues["empty_fact_type"]} 条')
