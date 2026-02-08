"""
修复验证：重新测试 P23v3 短篇 Writer（修复后 - 六法框架完整传递）
使用与 batch2 相同的 3 篇文章对比
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def scrape_article(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    title_tag = soup.title
    title = title_tag.string if title_tag else ''
    title = re.sub(r'\s*-\s*(深度|行情|矿业|监管|交易所|DeFi|NFT)\s*-\s*吴说.*$', '', title).strip()
    content_el = soup.select_one('.entry-content')
    if not content_el:
        return None
    for tag in content_el.find_all(['script', 'style', 'nav']):
        tag.decompose()
    raw_text = content_el.get_text(separator='\n')
    lines = []
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if '根据央行等部门发布' in line:
            break
        if '风险提示' in line:
            break
        if line.startswith('声明：'):
            continue
        if line.startswith('原文链接：'):
            continue
        lines.append(line)
    return {'title': title, 'url': url, 'content': '\n'.join(lines)}


if __name__ == '__main__':
    from app.agents.writer.short_article import short_article_writer
    from app.core.config import get_api_key

    api_key = get_api_key("doubao")

    # 同样 3 篇文章
    urls = [
        "https://www.wublock123.com/article/6/56363",  # NBA/Kalshi
        "https://www.wublock123.com/article/6/56359",  # Bithumb
        "https://www.wublock123.com/article/6/56355",  # 易理华
    ]

    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/3] 爬取: {url}")
        try:
            article = scrape_article(url)
        except Exception as e:
            print(f"  ❌ 爬取异常: {e}")
            continue
        if not article:
            print("  ❌ 爬取失败")
            continue

        print(f"  标题: {article['title']} ({len(article['content'])} 字)")

        state = {
            "raw_input": article['content'],
            "style": "mimeng",
            "narrative_type": "project_review",
            "api_config": {
                "provider": "volcengine",
                "api_key": api_key,
            },
            "strategy_json": "{}",
        }

        result = short_article_writer(state)
        draft = result.get("draft_content", "")
        variants = result.get("variants", [])

        article_result = {
            "source_title": article['title'],
            "source_url": url,
            "source_chars": len(article['content']),
            "draft": draft,
            "draft_chars": len(draft),
            "variants_count": len(variants),
            "variants": [{
                "label": v.get("label", ""),
                "methods": v.get("methods", []),
                "content": v.get("content", ""),
                "chars": v.get("char_count", 0),
            } for v in variants],
        }
        results.append(article_result)

        print(f"  Output: {len(draft)} chars | {len(variants)} variants")
        for v in variants:
            print(f"    {v.get('label','')}: {v.get('char_count',0)} 字")

    # 保存
    with open('scripts/test_fixed_sixmethod.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成 MD
    md = "# P23v3 修复后测试报告（六法框架完整传递）\n\n"
    md += "> 测试时间：2026-02-08\n"
    md += "> 修复内容：dynamic 分支现在包含完整六法框架 + 示例 + 风格要求\n"
    md += "> 对比基线：test_long_to_short_batch2.md（修复前）\n\n---\n\n"

    for r in results:
        md += f"## {r['source_title']}\n\n"
        md += f"**原文**：{r['source_chars']} 字\n\n"
        for v in r['variants']:
            md += f"### {v['label']}（{v['chars']} 字）\n"
            md += f"方法：{', '.join(v['methods'])}\n\n"
            md += f"{v['content']}\n\n---\n\n"

    with open('scripts/test_fixed_sixmethod.md', 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"\n{'='*60}")
    print("修复验证完成！")
    print("  JSON: scripts/test_fixed_sixmethod.json")
    print("  MD:   scripts/test_fixed_sixmethod.md")
