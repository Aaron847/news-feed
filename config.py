import os

# ============ SMTP 邮件配置 ============
# QQ邮箱: smtp.qq.com:465, Gmail: smtp.gmail.com:587, 163: smtp.163.com:465
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")          # 发件邮箱地址
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")   # 邮箱授权码（非登录密码）
EMAIL_TO = os.getenv("EMAIL_TO", "")             # 收件邮箱地址，多个用逗号分隔

# ============ API 密钥 ============
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")     # https://newsapi.org 注册获取
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Google Gemini API Key（免费）

# ============ RSS 订阅源 ============
RSS_FEEDS = {
    "科技AI": [
        "https://36kr.com/feed",                          # 36氪
        "https://www.jiqizhixin.com/rss",                 # 机器之心
        "https://feeds.arstechnica.com/arstechnica/index", # Ars Technica
        "https://www.theverge.com/rss/index.xml",          # The Verge
        "https://technologyreview.com/feed/",               # MIT Tech Review
    ],
    "综合热点": [
        "https://feeds.reuters.com/reuters/topNews",                    # Reuters
        "https://feeds.bbci.co.uk/news/world/rss.xml",                  # BBC World
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",       # NYT
    ],
    "财经市场": [
        "https://wallstreetcn.com/rss",                    # 华尔街见闻
        "https://www.ft.com/rss/home",                     # FT
        "https://feeds.bloomberg.com/bloomberg/news",      # Bloomberg
    ],
}

# ============ 网页爬取目标 ============
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
        "title_selector": "a.news-item",
        "link_selector": "a.news-item",
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
