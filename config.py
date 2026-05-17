import os

# ============ SMTP 邮件配置 ============
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# ============ API 密钥 ============
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ============ RSS 订阅源 ============
RSS_FEEDS = {
    "科技AI": [
        "https://36kr.com/feed",
        "https://www.jiqizhixin.com/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theverge.com/rss/index.xml",
        "https://technologyreview.com/feed/",
        "https://techcrunch.com/feed/",                      # TechCrunch
        "https://www.wired.com/feed/rss",                    # Wired
    ],
    "综合热点": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",       # BBC World
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",  # NYT
        "https://feeds.npr.org/1001/rss.xml",                # NPR
        "https://www.theguardian.com/world/rss",              # The Guardian
        "https://cn.nytimes.com/rss/",                        # 纽约时报中文
    ],
    "财经市场": [
        "https://wallstreetcn.com/rss",                      # 华尔街见闻
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",  # CNBC
        "https://www.cnbc.com/id/100727362/device/rss/rss.html",  # CNBC Tech
    ],
}

# ============ 网页爬取目标 ============
# link_selector: 在被 title_selector 选中的元素内查找链接
# 若不指定 link_selector，则直接取 title_selector 元素的 href 属性
WEB_SCRAPERS = [
    {
        "category": "科技AI",
        "url": "https://www.jiqizhixin.com/",
        "title_selector": "div.article-item__title",
        "link_selector": "a.article-item",
    },
    {
        "category": "综合热点",
        "url": "https://news.sina.com.cn/",
        "title_selector": "a[href*='/c/']",
    },
    {
        "category": "综合热点",
        "url": "https://www.zaobao.com.sg/",
        "title_selector": "a[href*='/news/']",
    },
]

# ============ NewsAPI 查询 ============
NEWSAPI_QUERIES = [
    {"category": "科技AI", "query": "AI artificial intelligence technology"},
    {"category": "财经市场", "query": "finance market stock economy"},
]

# ============ 输出配置 ============
NEWS_PER_CATEGORY = 8       # 每个类别最多抓取条数
SUMMARY_LANGUAGE = "中文"    # 摘要语言
