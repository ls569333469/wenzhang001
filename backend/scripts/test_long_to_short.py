"""
Test: scrape wublock long articles → run through short_article writer
Purpose: validate the "long article → short commentary" creation pipeline
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
    
    # Get title
    title_tag = soup.title
    title = title_tag.string if title_tag else ''
    title = re.sub(r'\s*-\s*(深度|行情|矿业|监管|交易所|DeFi|NFT)\s*-\s*吴说.*$', '', title).strip()
    
    # Get content from .entry-content
    content_el = soup.select_one('.entry-content')
    if not content_el:
        return None
    
    # Remove script/style tags
    for tag in content_el.find_all(['script', 'style', 'nav']):
        tag.decompose()
    
    # Get text with proper line breaks
    raw_text = content_el.get_text(separator='\n')
    
    # Clean up: remove excessive whitespace, keep meaningful lines
    lines = []
    for line in raw_text.split('\n'):
        line = line.strip()
        # Skip empty lines, very short lines, and boilerplate
        if not line or len(line) < 5:
            continue
        if '根据央行等部门发布' in line:
            break  # Stop at disclaimer
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
    """Run material through the short_article writer"""
    from app.agents.writer import writer_agent
    from app.core.mode_configs import get_mode_config
    
    mode_config = get_mode_config("short_article")
    length_config = mode_config.get("length", {})
    
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
    
    print(f"\n  Calling short_article_writer...")
    result = writer_agent(state)
    
    return result


if __name__ == '__main__':
    # Step 1: Scrape 5 articles
    urls = [
        "https://www.wublock123.com/article/47/56371",  # 泽西岛加密税收
        "https://www.wublock123.com/article/47/56369",  # 中国加密新规
        "https://www.wublock123.com/article/47/56365",  # 美股大崩盘反思
        "https://www.wublock123.com/article/6/56366",   # 中国RWA监管框架
        "https://www.wublock123.com/article/6/56370",   # 安永智能钱包
    ]
    
    print("=" * 60)
    print("STEP 1: Scraping articles from wublock123.com")
    print("=" * 60)
    
    articles = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/5] {url}")
        article = scrape_article(url)
        if article:
            print(f"  ✅ {article['title']} ({article['char_count']} chars)")
            articles.append(article)
        else:
            print(f"  ❌ Failed to extract content")
    
    print(f"\nScraped {len(articles)} articles successfully")
    
    # Step 2: Pick the best 2 and run through short_article
    print("\n" + "=" * 60)
    print("STEP 2: Running through short_article writer (top 2)")
    print("=" * 60)
    
    # Sort by content length (prefer longer = more depth)
    articles.sort(key=lambda x: x['char_count'], reverse=True)
    
    results = []
    for i, article in enumerate(articles[:2], 1):
        print(f"\n{'='*60}")
        print(f"[Test {i}/2] Source: {article['title']}")
        print(f"  Original: {article['char_count']} chars")
        print(f"  Content preview: {article['content'][:150]}...")
        
        try:
            result = test_short_article(article)
            draft = result.get("draft_content", "")
            variants = result.get("variants", [])
            
            print(f"\n  ✅ Generated draft ({len(draft)} chars)")
            print(f"  Variants: {len(variants)}")
            print(f"\n  --- DRAFT OUTPUT ---")
            print(f"  {draft}")
            print(f"  --- END ---")
            
            results.append({
                "source_title": article['title'],
                "source_chars": article['char_count'],
                "draft": draft,
                "draft_chars": len(draft),
                "variants_count": len(variants),
            })
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Step 3: Save results
    output_path = 'scripts/test_long_to_short.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"RESULTS SAVED: {output_path}")
    print(f"{'='*60}")
    for r in results:
        ratio = r['draft_chars'] / r['source_chars'] * 100 if r['source_chars'] > 0 else 0
        print(f"  {r['source_title'][:40]}")
        print(f"    {r['source_chars']} chars → {r['draft_chars']} chars ({ratio:.0f}% compression)")
