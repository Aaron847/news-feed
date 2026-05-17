import logging

import anthropic

from config import ANTHROPIC_API_KEY, SUMMARY_LANGUAGE

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""你是一位专业的新闻编辑助手。你的任务是对用户提供的新闻条目进行精炼摘要。

要求：
1. 用{SUMMARY_LANGUAGE}撰写摘要
2. 每条新闻用一句话概括核心信息（不超过50字）
3. 保留重要的人名、公司名、数据和关键事件
4. 客观中立，不添加个人观点
5. 严格按JSON数组格式输出，每条包含 title 和 summary 字段

输出格式示例：
[
  {{"title": "原始标题", "summary": "一句话摘要"}},
  ...
]"""


def summarize_category(category: str, news_items: list) -> list[dict]:
    """对一个类别的新闻进行AI摘要"""
    if not ANTHROPIC_API_KEY:
        logger.warning("Anthropic API Key未配置，返回原始标题")
        return [{"title": item.title, "summary": item.summary or item.title}
                for item in news_items]

    # 构建新闻列表文本
    news_text = ""
    for i, item in enumerate(news_items, 1):
        news_text += f"{i}. 标题: {item.title}\n"
        if item.summary:
            news_text += f"   摘要: {item.summary}\n"
        news_text += f"   链接: {item.link}\n\n"

    if not news_text.strip():
        return []

    prompt = f"请对以下【{category}】类别的新闻进行摘要总结：\n\n{news_text}"

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()

        # 解析JSON
        import json
        # 尝试提取JSON数组
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            summaries = json.loads(raw[start:end])
        else:
            summaries = json.loads(raw)

        # 补充原文链接
        for i, s in enumerate(summaries):
            if i < len(news_items):
                s["link"] = news_items[i].link
                s["source"] = news_items[i].source

        logger.info(f"AI摘要完成 [{category}]: {len(summaries)} 条")
        return summaries

    except Exception as e:
        logger.error(f"AI摘要失败 [{category}]: {e}")
        # 降级：返回原始信息
        return [
            {"title": item.title, "summary": item.summary or item.title,
             "link": item.link, "source": item.source}
            for item in news_items
        ]


def summarize_all(grouped_news: dict[str, list]) -> dict[str, list[dict]]:
    """对所有类别的新闻进行AI摘要"""
    result = {}
    for category, items in grouped_news.items():
        result[category] = summarize_category(category, items)
    return result
