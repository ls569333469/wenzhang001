# -*- coding: utf-8 -*-
"""End-to-end test: featured-only via Playwright"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, ".")
from app.services.material_fetcher.chaincatcher import ChainCatcherFetcher

f = ChainCatcherFetcher()
results = f.fetch_latest(count=20)

featured = [r for r in results if r.get("content_type") == "精选快讯"]
articles = [r for r in results if r.get("content_type") == "长文"]

print(f"\n{'='*60}")
print(f"Total: {len(results)} | Featured: {len(featured)} | Articles: {len(articles)}")
print(f"{'='*60}")
print(f"\nFeatured ({len(featured)}):")
for i, item in enumerate(featured, 1):
    print(f"  {i}. {item['title'][:70]}")
print(f"\nArticles (first 3 of {len(articles)}):")
for item in articles[:3]:
    t = item.get('title','')[:70]
    print(f"  - {t}")
