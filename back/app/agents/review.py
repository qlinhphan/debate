import os

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_CHAT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)


class BaseInps(BaseModel):
    exp: dict = Field(description="Dữ liệu gồm quan điểm của agent 1 và phản biện của agent 2")


@tool(args_schema=BaseInps)
def toolReviews(exp: dict):
    """Tổng hợp và đánh giá cuộc tranh luận."""
    print("<<<<< Tool Reviews >>>>>")
    messages = [
        (
            "system",
            "Bạn là trợ lý AI chuyên tổng hợp tranh luận và đưa ra kết luận hành động rõ ràng.",
        ),
        ("human", str(exp)),
    ]
    rs = llm.invoke(messages)
    return {"result": rs.content}


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Bạn là trợ lý AI chuyên review ý kiến của hai agent và đưa ra kết luận cuối.
Nhiệm vụ:
- Đọc kỹ toàn bộ trao đổi.
- Sử dụng tool trước khi kết luận.
- Trả lời đúng trọng tâm câu hỏi ban đầu: {q}
- Loại câu hỏi/câu nói đã nhận diện: {typew}
- Kết luận phải cụ thể, không nói chung chung.
- Trả về JSON hợp lệ theo dạng:
{{
  "decide": "quyết định hoặc câu trả lời cuối cùng",
  "reason": "lý do ngắn gọn"
}}
""",
        ),
        ("user", "{aws}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


def agent_reviews(data, q, typew):
    base = create_tool_calling_agent(llm, [toolReviews], prompt)
    agent = AgentExecutor(agent=base, tools=[toolReviews])
    rs = agent.invoke({"aws": data, "q": q, "typew": typew})
    print(rs["output"])
    return rs["output"]
