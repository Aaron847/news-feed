import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule


def load_env():
    """从 .env 文件加载环境变量"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key and value and key not in __import__("os").environ:
                    __import__("os").environ[key] = value


load_env()

from config import SMTP_USER, EMAIL_TO
from news_fetcher import fetch_all
from ai_summarizer import summarize_all
from email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("news_feed.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run_once():
    """执行一次完整的 抓取→摘要→发送 流程"""
    logger.info("=" * 50)
    logger.info("开始执行新闻日报任务")

    # 1. 抓取新闻
    logger.info("[1/3] 正在抓取新闻...")
    grouped_news = fetch_all()
    total = sum(len(v) for v in grouped_news.values())
    if total == 0:
        logger.warning("未抓取到任何新闻，跳过本次发送")
        return False

    # 2. AI摘要
    logger.info("[2/3] 正在生成AI摘要...")
    summarized = summarize_all(grouped_news)

    # 3. 发送邮件
    logger.info("[3/3] 正在发送邮件...")
    success = send_email(summarized)
    if success:
        logger.info("[OK] 任务完成！新闻日报已发送")
    else:
        logger.error("[FAIL] 邮件发送失败")
    return success


def scheduled_job():
    """定时任务入口，带错误处理"""
    try:
        run_once()
    except Exception as e:
        logger.error(f"定时任务异常: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="AI新闻日报 - 每日自动推送")
    parser.add_argument("--now", action="store_true", help="立即执行一次（用于测试）")
    parser.add_argument("--time", default="08:00", help="定时执行时间，默认 08:00")
    args = parser.parse_args()

    # 检查必要配置
    missing = []
    if not SMTP_USER:
        missing.append("SMTP_USER")
    if not EMAIL_TO:
        missing.append("EMAIL_TO")
    if missing:
        logger.error(f"缺少必要配置: {', '.join(missing)}，请设置环境变量或在 .env 文件中配置")

    if args.now:
        # 立即执行模式
        run_once()
        return

    # 定时模式
    logger.info(f"[SCHEDULE] 定时模式已启动，每天 {args.time} 执行")
    schedule.every().day.at(args.time).do(scheduled_job)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
