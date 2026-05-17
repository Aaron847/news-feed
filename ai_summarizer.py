import json
import logging

from google import genai

from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """你是一位专业的中文新闻编辑。对提供的新闻进行精炼摘要和翻译。

要求：
1. 所有输出必须是中文
2. 英文标题必须翻译为中文作为 title，保留原标题在 title_original
3. 中文标题的 title_original 留空字符串
4. summary 用一句话概括核心信息（不超过60字）
5. 保留重要的人名、公司名、数据
6. 客观中立
7. 严格按JSON格式输出，按类别分组

输出格式：
{
  "科技AI": [{"title": "中文标题", "title_original": "英文原题", "summary": "摘要"}, ...],
  "综合热点": [...],
  "财经市场": [...]
}"""


def _call_gemini(prompt: str) -> dict:
    """一次API调用处理所有类别"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.3,
            "max_output_tokens": 6000,
        },
    )
    raw = response.text.strip()
    # 去除 markdown 代码块标记
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3]
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        raw = re.sub(r",\s*}", "}", raw)
        raw = re.sub(r",\s*]", "]", raw)
        raw = re.sub(r",\s*,\s*", ",", raw)
        raw = re.sub(r'"\s*\n\s*"', '" "', raw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}，内容前200字: {raw[:200]}")
            raise


def summarize_all(grouped_news: dict[str, list]) -> dict[str, list[dict]]:
    """一次调用Gemini对所有类别进行摘要"""
    if not GEMINI_API_KEY:
        logger.warning("Gemini API Key未配置，返回原始标题")
        return {
            cat: [{"title": item.title, "title_original": "",
                   "summary": item.summary or item.title,
                   "link": item.link, "source": item.source}
                  for item in items]
            for cat, items in grouped_news.items()
        }

    # 构建一个包含所有类别的大prompt
    prompt_parts = []
    for category, items in grouped_news.items():
        if not items:
            continue
        prompt_parts.append(f"\n### {category} ###\n")
        for i, item in enumerate(items, 1):
            prompt_parts.append(f"{i}. 标题: {item.title}")
            if item.summary:
                prompt_parts.append(f"   摘要: {item.summary}")
            prompt_parts.append(f"   链接: {item.link}\n")

    if not prompt_parts:
        return {}

    prompt = "请对以下所有类别的新闻进行中文摘要和翻译：\n" + "\n".join(prompt_parts)

    try:
        all_summaries = _call_gemini(prompt)
    except Exception as e:
        logger.error(f"Gemini调用失败: {e}，降级为原始标题")
        return {
            cat: [{"title": item.title, "title_original": "",
                   "summary": item.summary or item.title,
                   "link": item.link, "source": item.source}
                  for item in items]
            for cat, items in grouped_news.items()
        }

    # 将Gemini输出的摘要与原始链接和来源合并
    result = {}
    for category, items in grouped_news.items():
        summaries = all_summaries.get(category, [])
        merged = []
        for i, item in enumerate(items):
            if i < len(summaries):
                s = dict(summaries[i])
                s["link"] = item.link
                s["source"] = item.source
                if "title" not in s or not s["title"]:
                    s["title"] = item.title
                if "title_original" not in s:
                    s["title_original"] = ""
                merged.append(s)
            else:
                merged.append({
                    "title": item.title, "title_original": "",
                    "summary": item.summary or item.title,
                    "link": item.link, "source": item.source,
                })
        result[category] = merged

    logger.info(f"Gemini批量摘要完成，共 {sum(len(v) for v in result.values())} 条")
    return result
