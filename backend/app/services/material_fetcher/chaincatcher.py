"""
ChainCatcher Fetcher - 链捕手爬虫
P23 Phase 1a: 抓取快讯 + 长文

策略: HTML 页面抓取 (SSR 渲染, 无需 JS)
  - 快讯列表: https://www.chaincatcher.com/news
  - 长文列表: https://www.chaincatcher.com/article
  - 单篇详情: https://www.chaincatcher.com/article/{id}
"""

import re
import time
import random
from datetime import datetime
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseFetcher
from app.core.config import get_logger

logger = get_logger("chaincatcher")

# UA pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

CC_BASE = "https://www.chaincatcher.com"


class ChainCatcherFetcher(BaseFetcher):
    """链捕手爬虫 — HTML 抓取快讯 + 长文"""

    @property
    def source_name(self) -> str:
        return "链捕手"

    @staticmethod
    def _clean_title(raw_title: str) -> str:
        """清理标题：去掉微信扫码、时间戳、ChainCatcher消息等拼接噪音"""
        # 截断：从'微信扫码'开始的一切都是噪音
        for noise in ['微信扫码', 'ChainCatcher 消息', 'ChainCatcher消息']:
            idx = raw_title.find(noise)
            if idx > 0:
                raw_title = raw_title[:idx]
        # 去掉末尾的时间戳 如 '02-14 22:06'
        raw_title = re.sub(r'\d{2}-\d{2}\s+\d{2}:\d{2}.*$', '', raw_title)
        return raw_title.strip()

    def fetch_latest(self, count: int = 100, featured_only: bool = True) -> List[Dict]:
        """抓取最新快讯 + 长文。快讯默认只取精选（蓝色标题），跳过纯数据搬运类快讯。"""
        results = []

        # 1. 快讯（默认精选）
        label = "精选快讯" if featured_only else "快讯"
        logger.info(f"[ChainCatcher] 抓取{label} (目标 {count} 条)...")
        news = self._fetch_news_list(count=count, featured_only=featured_only)
        results.extend(news)
        logger.info(f"[ChainCatcher] {label}: {len(news)} 条")

        # 2. 长文（不受精选筛选影响）
        logger.info(f"[ChainCatcher] 抓取长文 (目标 {count} 条)...")
        articles = self._fetch_article_list(count=count)
        results.extend(articles)
        logger.info(f"[ChainCatcher] 长文: {len(articles)} 条")

        logger.info(f"[ChainCatcher] 总计: {len(results)} 条")
        return results

    def _fetch_news_list(self, count: int, featured_only: bool = True) -> List[Dict]:
        """
        从 /news 页面抓取快讯列表。
        featured_only=True 时使用 Playwright 模拟浏览器滚动加载 + 点击"只看精选"：
          因为精选标记（selectedClass）由客户端 JS 动态添加，SSR HTML 里只有 1 条，
          需要浏览器执行 JS 才能获取全部精选条目。
        featured_only=False 时使用 requests 直接解析 SSR HTML（更快）。
        """
        if featured_only:
            items = self._fetch_featured_via_browser(count)
            if items:
                return items
            logger.info("  [Playwright 失败，回退到 SSR 解析]")

        # 非精选模式 或 Playwright 失败时回退
        url = f"{CC_BASE}/news"
        soup = self._get_page(url)
        if not soup:
            return []
        items = self._parse_news_page(soup, featured_only=featured_only)
        label = "精选" if featured_only else "全部"
        logger.info(f"  [SSR 解析完成] {len(items)} 条{label}快讯")
        return items[:count]

    def _fetch_featured_via_browser(self, count: int) -> List[Dict]:
        """使用 Playwright 浏览器抓取精选快讯。滚动加载更多内容 → 只看精选。"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.info("  [Playwright 未安装]")
            return []

        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-proxy-server", "--disable-gpu"]
                )
                page = browser.new_page()

                logger.info("  [Browser] 加载页面...")
                page.goto(f"{CC_BASE}/news", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)

                # 关闭弹窗
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)

                # 滚动加载更多内容
                logger.info("  [Browser] 滚动加载...")
                for i in range(8):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1500)

                total = page.evaluate(
                    "document.querySelectorAll('.v-timeline-item').length"
                )
                logger.info(f"  [Browser] 已加载 {total} 条快讯")

                # 点击"只看精选"
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(500)
                try:
                    page.locator(".v-input--switch").first.click(force=True, timeout=3000)
                    page.wait_for_timeout(2000)
                    logger.info("  [Browser] 只看精选 ON")
                except Exception:
                    logger.info("  [Browser] 无法点击精选开关，改为提取 selectedClass 条目")

                # 提取精选条目
                raw_items = page.evaluate("""
                    () => {
                        const results = [];
                        const items = document.querySelectorAll('.v-timeline-item');
                        for (const item of items) {
                            const style = getComputedStyle(item);
                            if (style.display === 'none') continue;

                            const link = item.querySelector('a[href*="/article/"]');
                            if (!link) continue;

                            const titleSpan = item.querySelector('.text');
                            const hasSelected = titleSpan && titleSpan.classList.contains('selectedClass');
                            if (!hasSelected) continue;

                            let title = link.textContent || '';
                            title = title.split('微信扫码')[0].trim();
                            const href = link.getAttribute('href');

                            if (title.length > 5) {
                                results.push({title: title.substring(0, 200), href});
                            }
                        }
                        return results;
                    }
                """)

                browser.close()

                seen_urls = set()
                for raw in raw_items:
                    href = raw.get("href", "")
                    if not href or href in seen_urls:
                        continue
                    full_url = f"{CC_BASE}{href}" if href.startswith("/") else href
                    seen_urls.add(href)
                    title = self._clean_title(raw["title"])
                    if not title or len(title) < 5:
                        continue
                    items.append({
                        "source": self.source_name,
                        "title": title,
                        "url": full_url,
                        "content": "",
                        "published_at": "",
                        "content_type": "精选快讯",
                        "is_featured": True,
                    })

                logger.info(f"  [Browser] 精选快讯: {len(items)} 条")

        except Exception as e:
            logger.warning(f"  [Browser] 异常: {e}")
            return []

        return items[:count]

    def _fetch_article_list(self, count: int) -> List[Dict]:
        """从 /article 页面抓取文章列表"""
        items = []
        page = 1

        while len(items) < count:
            url = f"{CC_BASE}/article" if page == 1 else f"{CC_BASE}/article?page={page}"
            soup = self._get_page(url)
            if not soup:
                break

            found = self._parse_article_page(soup)
            if not found:
                break

            items.extend(found)
            page += 1
            time.sleep(random.uniform(1.0, 2.0))

            if len(found) < 10:
                break

        return items[:count]

    def _parse_news_page(self, soup: BeautifulSoup, featured_only: bool = False) -> List[Dict]:
        """解析快讯列表页。使用 v-timeline-item 结构，通过 selectedClass 识别精选条目。"""
        items = []

        # ChainCatcher 使用 Vuetify v-timeline — 每条快讯是一个 v-timeline-item
        timeline_items = soup.find_all(class_=re.compile(r"v-timeline-item"))

        if not timeline_items:
            # Fallback: 旧的 link-based 解析
            return self._parse_news_page_fallback(soup, featured_only)

        seen_urls = set()
        for item in timeline_items:
            # 检测精选：蓝色标题的 <span class="text selectedClass">
            # 备选：topping class 或 topping 图片（蓝色圆点）
            is_featured = (
                item.find(class_="selectedClass") is not None or
                item.find(class_="topping") is not None or
                item.find("img", src=re.compile(r"topping")) is not None
            )

            if featured_only and not is_featured:
                continue

            link = item.find("a", href=re.compile(r"/article/\d+"))
            if not link:
                continue

            href = link.get("href", "")
            if not href or href in seen_urls:
                continue

            full_url = f"{CC_BASE}{href}" if href.startswith("/") else href
            seen_urls.add(href)

            title = self._clean_title(link.get_text(strip=True))
            if not title or len(title) < 5:
                continue

            if any(skip in title for skip in ["下载", "关于", "招聘", "隐私", "免责"]):
                continue

            content_type = "精选快讯" if is_featured else "快讯"

            items.append({
                "source": self.source_name,
                "title": title[:200],
                "url": full_url,
                "content": "",
                "published_at": "",
                "content_type": content_type,
                "is_featured": is_featured,
            })

        return items

    def _parse_news_page_fallback(self, soup: BeautifulSoup, featured_only: bool = False) -> List[Dict]:
        """Fallback: 当页面结构变化时，用原始 link 解析"""
        if featured_only:
            return []  # 无法区分精选，返回空

        items = []
        links = soup.find_all("a", href=re.compile(r"/article/\d+"))
        seen_urls = set()
        for link in links:
            href = link.get("href", "")
            if not href or href in seen_urls:
                continue
            full_url = f"{CC_BASE}{href}" if href.startswith("/") else href
            seen_urls.add(href)
            title = self._clean_title(link.get_text(strip=True))
            if not title or len(title) < 5:
                continue
            if any(skip in title for skip in ["下载", "关于", "招聘", "隐私", "免责"]):
                continue
            items.append({
                "source": self.source_name,
                "title": title[:200],
                "url": full_url,
                "content": "",
                "published_at": "",
                "content_type": "快讯",
                "is_featured": False,
            })
        return items

    def _parse_article_page(self, soup: BeautifulSoup) -> List[Dict]:
        """解析文章列表页"""
        items = []

        # Article listing — look for article cards/items
        links = soup.find_all("a", href=re.compile(r"/article/\d+"))

        seen_urls = set()
        for link in links:
            href = link.get("href", "")
            if not href or href in seen_urls:
                continue

            full_url = f"{CC_BASE}{href}" if href.startswith("/") else href
            seen_urls.add(href)

            title = self._clean_title(link.get_text(strip=True))
            if not title or len(title) < 10:
                continue

            # Skip navigation links
            if any(skip in title for skip in ["下载", "关于", "招聘", "隐私", "免责", "更多快讯"]):
                continue

            items.append({
                "source": self.source_name,
                "title": title[:200],
                "url": full_url,
                "content": "",
                "published_at": "",
                "content_type": "长文",
            })

        return items

    def fetch_article_detail(self, url: str) -> Dict:
        """
        获取单篇文章的详情 (正文 + 发布时间)
        """
        soup = self._get_page(url)
        if not soup:
            return {}

        result = {}

        # Extract published time
        time_el = (
            soup.find("time") or
            soup.find("span", class_=re.compile(r"time|date", re.I)) or
            soup.find("div", class_=re.compile(r"time|date", re.I))
        )
        if time_el:
            time_text = time_el.get("datetime") or time_el.get_text(strip=True)
            result["published_at"] = self._parse_time(time_text)

        # Extract content
        content_el = (
            soup.select_one(".article-content") or
            soup.select_one(".news-content") or
            soup.select_one(".content-body") or
            soup.select_one("article .content") or
            soup.select_one("article")
        )

        if content_el:
            for tag in content_el.find_all(["script", "style", "nav", "footer", "aside"]):
                tag.decompose()
            result["content"] = content_el.get_text(separator="\n", strip=True)[:5000]

        return result

    def enrich_with_details(self, items: List[Dict], max_items: int = None) -> List[Dict]:
        """
        批量获取文章详情，补充 content 和 published_at
        """
        total = min(len(items), max_items) if max_items else len(items)
        enriched = []

        for i, item in enumerate(items[:total]):
            if item.get("content"):
                enriched.append(item)
                continue

            logger.info(f"[ChainCatcher] 获取详情 {i + 1}/{total}: {item['title'][:40]}...")
            detail = self.fetch_article_detail(item["url"])

            if detail:
                item["content"] = detail.get("content", "")
                item["published_at"] = detail.get("published_at", item.get("published_at", ""))

            enriched.append(item)
            time.sleep(random.uniform(0.5, 1.5))

        # Append remaining non-enriched items
        if max_items and max_items < len(items):
            enriched.extend(items[max_items:])

        return enriched

    def _parse_time(self, time_str: str) -> str:
        """尝试解析各种时间格式"""
        if not time_str:
            return ""

        # Already ISO format
        if re.match(r"\d{4}-\d{2}-\d{2}T", time_str):
            return time_str

        # Common Chinese formats
        patterns = [
            (r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", "%Y-%m-%d %H:%M"),
            (r"(\d{4})年(\d{1,2})月(\d{1,2})日", "%Y年%m月%d日"),
            (r"(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", None),  # MM-DD HH:MM
        ]

        for pattern, fmt in patterns:
            if re.search(pattern, time_str):
                try:
                    if fmt:
                        dt = datetime.strptime(time_str.strip(), fmt)
                        return dt.isoformat()
                except ValueError:
                    pass

        # Relative time: "2h前", "5分钟前" etc.
        rel_match = re.search(r"(\d+)\s*(分钟|小时|天|h|m|min)", time_str)
        if rel_match:
            num = int(rel_match.group(1))
            unit = rel_match.group(2)
            from datetime import timedelta
            now = datetime.now()
            if unit in ("小时", "h"):
                return (now - timedelta(hours=num)).isoformat()
            elif unit in ("分钟", "m", "min"):
                return (now - timedelta(minutes=num)).isoformat()
            elif unit in ("天",):
                return (now - timedelta(days=num)).isoformat()

        return time_str

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """获取页面并解析为 BeautifulSoup"""
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    return BeautifulSoup(resp.text, "html.parser")
                elif resp.status_code == 429:
                    wait = 2 ** attempt + random.uniform(1, 3)
                    logger.info(f"[ChainCatcher] Rate limited, waiting {wait:.1f}s...")
                    time.sleep(wait)
                else:
                    logger.info(f"[ChainCatcher] HTTP {resp.status_code} for {url}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"[ChainCatcher] Request error (attempt {attempt + 1}): {e}")
                time.sleep(1)

        return None
