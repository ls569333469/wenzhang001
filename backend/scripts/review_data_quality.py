"""Knowledge_Repo 数据质量评审脚本"""
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

# 获取最新 15 条
url = f'{base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records'
params = {'page_size': 15}
resp = requests.get(url, headers=headers, params=params)
total = resp.json().get('data', {}).get('total', 0)
records = resp.json().get('data', {}).get('items', [])

print('=' * 60)
print('=== Knowledge_Repo 数据质量评审报告 ===')
print('=' * 60)
print(f'总记录数: {total}')
print(f'样本数: {len(records)}\n')

# 统计
v3_count = 0
legacy_count = 0
issues = {'empty_summary': 0, 'long_summary': 0, 'empty_keywords': 0, 'empty_depth': 0}
summary_lens = []

for r in records:
    f = r.get('fields', {})
    
    # 判断 v3 vs 旧
    s_v3 = f.get('核心摘要', '')
    s_old = f.get('摘要', '')
    depth = f.get('信息深度', '')
    fact = f.get('事实类型', '') or f.get('内容类型', '')
    kw = f.get('关键词', '')
    
    if s_v3:
        v3_count += 1
        summary = s_v3
    else:
        legacy_count += 1
        summary = s_old
    
    slen = len(str(summary))
    summary_lens.append(slen)
    
    if not summary:
        issues['empty_summary'] += 1
    if slen > 200:
        issues['long_summary'] += 1
    if not kw:
        issues['empty_keywords'] += 1
    if not depth:
        issues['empty_depth'] += 1

# 评分
score = 100
score -= issues['empty_summary'] * 15
score -= issues['long_summary'] * 5
score -= issues['empty_keywords'] * 3
score -= issues['empty_depth'] * 3
score -= legacy_count * 2
score = max(0, score)

print('--- 字段使用统计 ---')
print(f'使用 v3.0 新字段: {v3_count} 条')
print(f'使用旧字段 (遗留): {legacy_count} 条')

print('\n--- 问题统计 ---')
print(f'摘要为空: {issues["empty_summary"]} 条')
print(f'摘要过长 (>200字): {issues["long_summary"]} 条')
print(f'关键词为空: {issues["empty_keywords"]} 条')
print(f'信息深度为空: {issues["empty_depth"]} 条')

print('\n--- 摘要长度分布 ---')
print(f'最短: {min(summary_lens) if summary_lens else 0} 字')
print(f'最长: {max(summary_lens) if summary_lens else 0} 字')
print(f'平均: {sum(summary_lens)//len(summary_lens) if summary_lens else 0} 字')

print('\n' + '=' * 60)
print('=== 综合评分 ===')
print('=' * 60)
print(f'得分: {score}/100')
if score >= 90:
    grade = 'A (优秀)'
elif score >= 80:
    grade = 'B (良好)'
elif score >= 70:
    grade = 'C (合格)'
elif score >= 60:
    grade = 'D (待改进)'
else:
    grade = 'F (不合格)'
print(f'评级: {grade}')

# 逐条详情
print('\n' + '=' * 60)
print('=== 最新记录详情 (前5条) ===')
print('=' * 60)
for i, r in enumerate(records[:5]):
    f = r.get('fields', {})
    title = f.get('标题', '')[:30]
    summary = f.get('核心摘要', '') or f.get('摘要', '')
    depth = f.get('信息深度', '') or '[空]'
    fact = f.get('事实类型', '') or f.get('内容类型', '') or '[空]'
    
    print(f'\n[{i+1}] 标题: {title}...')
    print(f'    摘要长度: {len(str(summary))} 字')
    print(f'    信息深度: {depth}')
    print(f'    事实类型: {fact}')
