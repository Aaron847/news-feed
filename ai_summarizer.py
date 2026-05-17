import json
import logging

from google import genai

from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """你是一位专业的中文新闻编辑。你的任务是对提供的新闻条目进行精炼摘要和翻译。

要求：
1. 所有输出必须是中文
2. 英文标题必须翻译成中文作为 title，原英文标题保留在 title_original 字段
3. 如果原标题已经是中文，title_original 留空字符串
4. 每条新闻用一句话概括核心信息作为 summary（不超过60字）
5. 保留重要的人名、公司名、数据和关键事件
6. 客观中立，不添加个人观点
7. 严格按JSON数组格式输出

输出格式：
[
  {"title": "中文标题", "title_original": "原始英文标题（中文源则留空）", "summary": "一句话中文摘要"},
  ...
]"""


def _call_gemini(prompt: str) -> list[dict]:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.3,
            "max_output_tokens": 3000,
        },
    )
    raw = response.text.strip()
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(raw[start:end])
    return json.loads(raw)


def summarize_category(category: str, news_items: list) -> list[dict]:
    if not GEMINI_API_KEY or not news_items:
        logger.warning("Gemini API Key未配置，返回原始标题")
        return [{"title": item.title, "title_original": "", "summary": item.summary or item.title,
                 "link": item.link, "source": item.source} for item in news_items]

    news_text = ""
    for i, item in enumerate(news_items, 1):
        news_text += f"{i}. 标题: {item.title}\n"
        if item.summary:
            news_text += f"   摘要: {item.summary}\n"
        news_text += f"   链接: {item.link}\n\n"

    prompt = f"请对以下【{category}】类别的新闻进行中文摘要和翻译：\n\n{news_text}"

    try:
        summaries = _call_gemini(prompt)
        for i, s in enumerate(summaries):
            if i < len(news_items):
                s["link"] = news_items[i].link
                s["source"] = news_items[i].source
                # 确保中文标题存在
                if "title" not in s or not s["title"]:
                    s["title"] = news_items[i].title
        logger.info(f"Gemini摘要完成 [{category}]: {len(summaries)} 条")
        return summaries
    except Exception as e:
        logger.error(f"Gemini调用失败 [{category}]: {e}")
        return [{"title": item.title, "title_original": "", "summary": item.summary or item.title,
                 "link": item.link, "source": item.source} for item in news_items]


def summarize_all(grouped_news: dict[str, list]) -> dict[str, list[dict]]:
    result = {}
    for category, items in grouped_news.items():
        result[category] = summarize_category(category, items)
    return result
