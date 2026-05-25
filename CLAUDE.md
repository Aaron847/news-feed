# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Run once (test)**: `python main.py --now`
- **Run with scheduler**: `python main.py` (default 08:00) or `python main.py --time 09:00`
- **Install deps**: `pip install -r requirements.txt`
- **Trigger GitHub Actions**: `gh workflow run daily-news.yml --ref master`
- **View workflow logs**: `gh run view --job=<job-id> --log`

## Architecture

```
main.py              → Entry point. Loads .env, orchestrates fetch → summarize → send
config.py            → Settings: SMTP, API keys, RSS feeds, web scrapers, NewsAPI queries
news_fetcher.py      → Fetches news from RSS (feedparser), web scraping (BeautifulSoup), NewsAPI
ai_summarizer.py     → Calls DeepSeek API (OpenAI-compatible) for Chinese translation & summarization
email_sender.py      → Builds HTML email and sends via SMTP
.github/workflows/   → GitHub Actions scheduled job (daily at UTC 01:05 = Beijing 09:05)
```

### Flow

1. `fetch_all()` collects NewsItem objects from RSS feeds, web scraping, and NewsAPI, then deduplicates
2. `summarize_all()` sends all news to DeepSeek in one batch for translation + summarization
3. `summarize_hot_topics()` picks top 5 hot topics from summarized news via DeepSeek
4. `send_email()` builds a styled HTML email with category sections and hot topics, then sends via SMTP

## Key Configuration

- **Local `.env` file** (gitignored) — holds API keys and SMTP credentials
- **GitHub Secrets** — mirrors `.env` for CI: `SMTP_*`, `EMAIL_TO`, `NEWS_API_KEY`, `DEEPSEEK_API_KEY`
- **`config.py`** — RSS feed URLs, web scraper selectors, NewsAPI queries, limits per category
- RSS feeds timeout or return empty for some sources behind a firewall in China (e.g., Reuters, Bloomberg, wallstreetcn)

## Important Notes

- DeepSeek API is OpenAI-compatible (`openai` package), base URL is `https://api.deepseek.com`
- Model used: `deepseek-chat`, configured in `ai_summarizer.py` as `DEEPSEEK_MODEL`
- The `schedule` library polling loop (`main.py`) is only for local persistent runs; production uses GitHub Actions
- `.env` file must exist locally but is never committed
- Node.js 20 actions deprecation warning in CI — `actions/checkout@v4` and `actions/setup-python@v5` may need updates
