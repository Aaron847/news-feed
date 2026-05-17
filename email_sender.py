import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_TO

logger = logging.getLogger(__name__)

# 类别对应的图标和颜色
CATEGORY_STYLE = {
    "科技AI": {"icon": "🖥️", "color": "#6366f1", "bg": "#eef2ff"},
    "综合热点": {"icon": "🌍", "color": "#dc2626", "bg": "#fef2f2"},
    "财经市场": {"icon": "📈", "color": "#059669", "bg": "#ecfdf5"},
}


def _build_html(summarized_news: dict[str, list[dict]]) -> str:
    """构建邮件HTML内容"""
    today = datetime.now().strftime("%Y年%m月%d日")
    sections = []

    for category, items in summarized_news.items():
        style = CATEGORY_STYLE.get(category, {"icon": "📰", "color": "#374151", "bg": "#f9fafb"})
        icon = style["icon"]
        color = style["color"]
        bg = style["bg"]

        news_rows = ""
        for item in items:
            title = item.get("title", "")
            summary = item.get("summary", "")
            link = item.get("link", "#")
            source = item.get("source", "")

            source_tag = f'<span style="font-size:12px;color:#9ca3af;">{source}</span>' if source else ""
            news_rows += f"""
            <tr>
              <td style="padding:12px 16px;border-bottom:1px solid #f3f4f6;">
                <a href="{link}" style="color:{color};font-weight:600;font-size:15px;text-decoration:none;line-height:1.5;">
                  {title}
                </a>
                {source_tag}
                <p style="margin:6px 0 0;color:#6b7280;font-size:14px;line-height:1.6;">
                  {summary}
                </p>
              </td>
            </tr>"""

        sections.append(f"""
        <div style="margin-bottom:28px;">
          <div style="background:{bg};border-left:4px solid {color};padding:12px 16px;border-radius:0 8px 8px 0;">
            <h2 style="margin:0;font-size:18px;color:{color};">{icon} {category}</h2>
          </div>
          <table style="width:100%;border-collapse:collapse;background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
            {news_rows}
          </table>
        </div>""")

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;">
  <div style="max-width:680px;margin:0 auto;padding:24px 16px;">
    <!-- 头部 -->
    <div style="text-align:center;padding:32px 0 24px;">
      <h1 style="margin:0;font-size:26px;color:#1f2937;">📰 AI新闻日报</h1>
      <p style="margin:8px 0 0;color:#9ca3af;font-size:14px;">{today} · 由AI精选与摘要</p>
    </div>

    <!-- 新闻内容 -->
    {"".join(sections)}

    <!-- 底部 -->
    <div style="text-align:center;padding:20px 0;color:#9ca3af;font-size:12px;border-top:1px solid #e5e7eb;margin-top:16px;">
      本邮件由 AI 自动生成 · 数据来源: RSS / Web / NewsAPI
    </div>
  </div>
</body>
</html>"""
    return html


def send_email(summarized_news: dict[str, list[dict]]) -> bool:
    """发送新闻摘要邮件"""
    if not all([SMTP_USER, SMTP_PASSWORD, EMAIL_TO]):
        logger.error("SMTP配置不完整，请检查环境变量 SMTP_USER/SMTP_PASSWORD/EMAIL_TO")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"📰 AI新闻日报 - {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    html = _build_html(summarized_news)
    msg.attach(MIMEText(html, "html", "utf-8"))

    # 生成纯文本版本作为后备
    text_parts = []
    for category, items in summarized_news.items():
        text_parts.append(f"== {category} ==")
        for item in items:
            text_parts.append(f"- {item.get('title', '')}: {item.get('summary', '')}")
            text_parts.append(f"  {item.get('link', '')}")
        text_parts.append("")
    msg.attach(MIMEText("\n".join(text_parts), "plain", "utf-8"))

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            server.starttls()

        server.login(SMTP_USER, SMTP_PASSWORD)
        recipients = [addr.strip() for addr in EMAIL_TO.split(",")]
        server.sendmail(SMTP_USER, recipients, msg.as_string())
        server.quit()

        logger.info(f"邮件发送成功 → {recipients}")
        return True

    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return False
