"""
Quick scraper to test extracting long-form articles from wublock123.com
"""
import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Target articles (deep analysis / long-form)
ARTICLE_URLS = [
    "https://www.wublock123.com/article/47/56371",  # 泽西岛加密税收
    "https://www.wublock123.com/article/47/56369",  # 中国加密新规
    "https://www.wublock123.com/article/47/56365",  # 美股大崩盘反思
    "https://www.wublock123.com/article/6/56366",   # 中国RWA监管框架
    "https://www.wublock123.com/article/6/56370",   # 安永智能钱包
]


def try_extract_content(url):
    """Try multiple strategies to extract article content"""
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Strategy 1: Look for common article containers
    selectors = [
        'article', '.article-content', '.content', '.post-content',
        '.article-body', '.detail-content', '.article_content',
        '#article', '.text', '.rich_media_content',
        '.article-detail', '.news-content', '.entry-content'
    ]
    
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(separator='\n', strip=True)
            if len(text) > 200:
                return sel, text
    
    # Strategy 2: Find the largest text block
    all_divs = soup.find_all('div')
    best = ('', '')
    for div in all_divs:
        text = div.get_text(separator='\n', strip=True)
        # Skip navigation-heavy blocks
        links = div.find_all('a')
        if len(links) > 10 and len(text) < 1000:
            continue
        if len(text) > len(best[1]):
            cls = div.get('class', ['unknown'])
            best = (str(cls), text)
    
    if len(best[1]) > 200:
        return f"largest_div:{best[0]}", best[1]
    
    # Strategy 3: Check if content is in a script tag (SSR data)
    for script in soup.find_all('script'):
        text = script.string or ''
        if 'article' in text.lower() and len(text) > 500:
            # Try to find JSON data
            json_match = re.search(r'\{.*"content".*\}', text, re.DOTALL)
            if json_match:
                return "script_json", json_match.group()[:3000]
    
    # Strategy 4: Get meta description as fallback
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        return "meta_description", meta_desc.get('content', '')
    
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    if og_desc:
        return "og_description", og_desc.get('content', '')
    
    return "none", f"Failed to extract. Page title: {soup.title.string if soup.title else 'N/A'}"


def extract_title(url):
    """Extract title from URL"""
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.title.string if soup.title else 'Unknown'
    # Clean up title
    title = title.replace(' - 深度 - 吴说 - 区块链快讯与深度内容平台', '')
    title = title.replace(' - 行情 - 吴说 - 区块链快讯与深度内容平台', '')
    return title.strip()


if __name__ == '__main__':
    results = []
    
    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/5] Fetching: {url}")
        
        try:
            title = extract_title(url)
            print(f"Title: {title}")
            
            strategy, content = try_extract_content(url)
            print(f"Strategy: {strategy}")
            print(f"Content length: {len(content)} chars")
            print(f"Content preview: {content[:200]}...")
            
            results.append({
                "url": url,
                "title": title,
                "strategy": strategy,
                "content_length": len(content),
                "content": content[:5000],
            })
        except Exception as e:
            print(f"Error: {e}")
            results.append({"url": url, "error": str(e)})
    
    # Save results
    with open('scripts/wublock_articles.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Done! Saved {len(results)} articles to scripts/wublock_articles.json")
