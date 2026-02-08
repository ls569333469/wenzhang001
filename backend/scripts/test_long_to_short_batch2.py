"""
Batch 2: Test 5 more wublock articles through short_article pipeline
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def scrape_article(url):
    """Scrape a wublock123 article and return clean content"""
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
    
    clean_text = '\n'.join(lines)
    return {
        'title': title,
        'url': url,
        'content': clean_text,
        'char_count': len(clean_text),
    }


def test_short_article(material):
    from app.agents.writer import writer_agent
    
    state = {
        "raw_input": material['content'],
        "mode": "short_article",
        "style": "mimeng",
        "custom_length": 0,
        "retention_level": 3,
        "narrative_type": "project_review",
        "references": [],
        "selected_option": None,
        "api_config": {
            "provider": os.getenv("DEFAULT_PROVIDER", "volcengine"),
            "api_key": os.getenv("VOLCENGINE_API_KEY", ""),
            "model_id": os.getenv("VOLCENGINE_MODEL_ID", ""),
        },
        "agent_config": {},
        "custom_prompts": {},
        "strategy_plan": "",
        "strategy_json": "",
        "web3_knowledge": "",
        "info_anchors": {},
    }
    
    return writer_agent(state)


if __name__ == '__main__':
    # 5 new articles (different from batch 1)
    urls = [
        "https://www.wublock123.com/article/6/56358",  # Hyperliquid 爆仓巨鲸转5000BTC入币安
        "https://www.wublock123.com/article/6/56359",  # Bithumb误发奖励110%赔偿
        "https://www.wublock123.com/article/6/56352",  # Arthur Hayes IBIT对冲
        "https://www.wublock123.com/article/6/56355",  # 易理华与BTC OG巨鲸同地址
        "https://www.wublock123.com/article/6/56363",  # NBA球员投资预测市场Kalshi
    ]
    
    print("=" * 60)
    print("BATCH 2: Scraping 5 articles from wublock123.com")
    print("=" * 60)
    
    articles = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/5] {url}")
        article = scrape_article(url)
        if article:
            print(f"  Title: {article['title']}")
            print(f"  Content: {article['char_count']} chars")
            articles.append(article)
        else:
            print(f"  FAILED to extract")
    
    print(f"\n{'='*60}")
    print(f"RUNNING SHORT ARTICLE WRITER ON ALL {len(articles)}")
    print(f"{'='*60}")
    
    results = []
    for i, article in enumerate(articles, 1):
        print(f"\n--- [{i}/{len(articles)}] {article['title'][:50]} ---")
        print(f"  Source: {article['char_count']} chars")
        
        try:
            result = test_short_article(article)
            draft = result.get("draft_content", "")
            variants = result.get("variants", [])
            
            print(f"  Output: {len(draft)} chars | {len(variants)} variants")
            print(f"  Draft:\n{draft}")
            
            results.append({
                "source_title": article['title'],
                "source_url": article['url'],
                "source_chars": article['char_count'],
                "draft": draft,
                "draft_chars": len(draft),
                "variants_count": len(variants),
                "variants": [{"method": v.get("method",""), "content": v.get("content",""), "chars": len(v.get("content",""))} for v in variants],
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Save
    with open('scripts/test_long_to_short_batch2.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"BATCH 2 COMPLETE - {len(results)} results")
    print(f"{'='*60}")
    for r in results:
        ratio = r['draft_chars'] / r['source_chars'] * 100 if r['source_chars'] > 0 else 0
        print(f"  {r['source_title'][:45]}")
        print(f"    {r['source_chars']} → {r['draft_chars']} chars ({ratio:.0f}%)")
