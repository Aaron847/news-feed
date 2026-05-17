import logging
from dataclasses import dataclass
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from config import (
    RSS_FEEDS,
    WEB_SCRAPERS,
    NEWSAPI_QUERIES,
    NEWS_API_KEY,
    NEWS_PER_CATEGORY,
)

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    link: str
    summary: str
    category: str
    source: str  # 来源标识：rss / web / newsapi


def fetch_rss(url: str, category: str) -> list[NewsItem]:
    """从RSS feed抓取新闻"""
    items = []
    try:
        feed = feedparser.parse(url)
        site_name = feed.feed.get("title", urlparse(url).netloc)
        for entry in feed.entries[:NEWS_PER_CATEGORY]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            if title and link:
                # 清理HTML标签
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text(separator=" ", strip=True)[:300]
                items.append(NewsItem(
                    title=title, link=link, summary=summary,
                    category=category, source=f"rss:{site_name}",
                ))
        logger.info(f"RSS [{site_name}] 获取 {len(items)} 条")
    except Exception as e:
        logger.error(f"RSS抓取失败 {url}: {e}")
    return items


def fetch_webpage(cfg: dict) -> list[NewsItem]:
    """从网页爬取新闻"""
    items = []
    url = cfg["url"]
    category = cfg["category"]
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        title_sel = cfg.get("title_selector", "a")
        elements = soup.select(title_sel)[:NEWS_PER_CATEGORY]
        site_name = urlparse(url).netloc

        for el in elements:
            title = el.get_text(strip=True)
            link = el.get("href", "")
            if link and not link.startswith("http"):
                link = f"{urlparse(url).scheme}://{urlparse(url).netloc}{link}"
            if title and link:
                items.append(NewsItem(
                    title=title, link=link, summary="",
                    category=category, source=f"web:{site_name}",
                ))
        logger.info(f"网页 [{site_name}] 获取 {len(items)} 条")
    except Exception as e:
        logger.error(f"网页爬取失败 {url}: {e}")
    return items


def fetch_newsapi(query: str, category: str) -> list[NewsItem]:
    """从NewsAPI获取新闻"""
    if not NEWS_API_KEY:
        logger.warning("NewsAPI Key未配置，跳过NewsAPI源")
        return []

    items = []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": NEWS_PER_CATEGORY,
            "apiKey": NEWS_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        for article in data.get("articles", []):
            title = (article.get("title") or "").strip()
            link = (article.get("url") or "").strip()
            summary = (article.get("description") or "").strip()[:300]
            if title and link and title != "[Removed]":
                items.append(NewsItem(
                    title=title, link=link, summary=summary,
                    category=category, source="newsapi",
                ))
        logger.info(f"NewsAPI [{query}] 获取 {len(items)} 条")
    except Exception as e:
        logger.error(f"NewsAPI查询失败 [{query}]: {e}")
    return items


def _deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    """按链接去重，同链接只保留第一条"""
    seen = set()
    result = []
    for item in items:
        # 标准化链接：去掉尾部斜杠和查询参数中的追踪参数
        clean_link = item.link.rstrip("/")
        if clean_link not in seen:
            seen.add(clean_link)
            result.append(item)
    return result


def fetch_all() -> dict[str, list[NewsItem]]:
    """聚合所有新闻源，返回按类别分组的新闻"""
    all_items: list[NewsItem] = []

    # RSS
    for category, urls in RSS_FEEDS.items():
        for url in urls:
            all_items.extend(fetch_rss(url, category))

    # 网页爬取
    for cfg in WEB_SCRAPERS:
        all_items.extend(fetch_webpage(cfg))

    # NewsAPI
    for q in NEWSAPI_QUERIES:
        all_items.extend(fetch_newsapi(q["query"], q["category"]))

    # 去重
    all_items = _deduplicate(all_items)

    # 按类别分组
    grouped: dict[str, list[NewsItem]] = {}
    for item in all_items:
        grouped.setdefault(item.category, []).append(item)

    # 每个类别截取上限
    for cat in grouped:
        grouped[cat] = grouped[cat][:NEWS_PER_CATEGORY]

    logger.info(f"聚合完成，共 {sum(len(v) for v in grouped.values())} 条新闻，"
                f"类别: {list(grouped.keys())}")
    return grouped
