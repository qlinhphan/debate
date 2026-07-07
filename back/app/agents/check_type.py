import os
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


QUESTION_TYPES = [
    "Cái gì",
    "Ai",
    "Ở đâu",
    "Khi nào",
    "Tại sao",
    "Như thế nào",
    "Có/không",
    "So sánh",
    "Liệt kê",
    "Lệnh/yêu cầu thực hiện",
    "Tính toán",
    "Sáng tạo",
    "Ý kiến/gợi ý",
]

DEFAULT_TYPE = "Ý kiến/gợi ý"

llm = ChatOpenAI(
    model=os.getenv("MODEL_CHAT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _detect_by_rules(question: str) -> str | None:
    text = _normalize(question)
    if not text:
        return DEFAULT_TYPE

    if re.search(r"\b(ai|người nào|nhân vật nào|tác giả nào|công ty nào|tổ chức nào)\b", text):
        return "Ai"
    if re.search(r"\b(ở đâu|nơi nào|chỗ nào|địa điểm nào|tại đâu)\b", text):
        return "Ở đâu"
    if re.search(r"\b(khi nào|bao giờ|lúc nào|thời điểm nào|năm nào|ngày nào|tháng nào)\b", text):
        return "Khi nào"
    if re.search(r"\b(tại sao|vì sao|do đâu|nguyên nhân|lý do)\b", text):
        return "Tại sao"
    if re.search(r"\b(như thế nào|thế nào|bằng cách nào|làm sao|ra sao|cách nào)\b", text):
        return "Như thế nào"
    if re.search(r"\b(có phải|có nên|đúng không|không\?|chưa\?|phải không|hay không)\b", text):
        return "Có/không"
    if re.search(r"\b(so sánh|khác nhau|giống nhau|hơn|kém|tốt hơn|xấu hơn)\b", text):
        return "So sánh"
    if re.search(r"\b(liệt kê|danh sách|những gì|các bước|các loại|bao nhiêu)\b", text):
        return "Liệt kê"
    if re.search(r"\b(tính|tính toán|bao nhiêu tiền|phần trăm|tổng|hiệu|tích|thương)\b", text):
        return "Tính toán"
    if re.search(r"\b(viết|tạo|sáng tác|soạn|lập kế hoạch|hãy|giúp tôi|làm cho tôi)\b", text):
        return "Lệnh/yêu cầu thực hiện"
    if re.search(r"\b(ý kiến|gợi ý|nên|đề xuất|khuyên|đánh giá|nhận xét)\b", text):
        return "Ý kiến/gợi ý"
    if re.search(r"\b(cái gì|là gì|gì|định nghĩa|khái niệm)\b", text):
        return "Cái gì"
    return None


def _detect_by_llm(question: str) -> str:
    labels = ", ".join(QUESTION_TYPES)
    messages = [
        (
            "system",
            (
                "Bạn là bộ phân loại loại câu hỏi tiếng Việt. "
                "Chỉ trả về đúng một nhãn trong danh sách sau, không giải thích: "
                f"{labels}."
            ),
        ),
        ("human", question),
    ]
    try:
        result = llm.invoke(messages).content.strip()
    except Exception:
        return DEFAULT_TYPE

    for question_type in QUESTION_TYPES:
        if question_type.lower() in result.lower():
            return question_type
    return DEFAULT_TYPE


def agent_check_types(q):
    return _detect_by_rules(q) or _detect_by_llm(q)
