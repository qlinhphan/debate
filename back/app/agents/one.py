import os

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_CHAT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)


class BaseInp(BaseModel):
    exp: str = Field(description="Chủ đề hoặc luận điểm người dùng đưa ra")


@tool(args_schema=BaseInp)
def toolCommunicateOne(exp: str):
    """Tạo quan điểm phản biện ngắn về một chủ đề."""
    print("<<<<< TOOL ONE >>>>>")
    messages = [
        (
            "system",
            "Bạn là trợ lý AI chuyên phân tích và đưa ra một quan điểm phản biện ngắn, rõ ràng, lịch sự.",
        ),
        ("human", exp),
    ]
    rs = llm.invoke(messages)
    return {"result": rs.content}


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Bạn đóng vai Donald Trump trong một cuộc tranh luận giả lập.
Nhiệm vụ:
- Dựa vào tool để lấy ý chính.
- Trả lời phù hợp với loại câu hỏi/câu nói: {type_q}.
- Phản biện trực tiếp vào vấn đề, không hỏi lại người dùng.
- Không nói "định dạng câu hỏi sai".
- Giữ giọng lịch sự, văn minh, ngắn gọn khoảng 50 từ.
- Chỉ trả lời dạng văn bản thường, không dùng danh sách đánh số.
""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

base = create_tool_calling_agent(llm, [toolCommunicateOne], prompt)
agent = AgentExecutor(agent=base, tools=[toolCommunicateOne])


def _to_langchain_messages(history: list[dict] | None):
    messages = []
    for item in history or []:
        role = item.get("role")
        content = item.get("content", "")
        if role == "human":
            messages.append(HumanMessage(content=content))
        elif role == "ai":
            messages.append(AIMessage(content=content))
    return messages


def agent_ones(q, type_sen, history: list[dict] | None = None, return_history: bool = False):
    rs = agent.invoke({"input": q, "history": _to_langchain_messages(history), "type_q": type_sen})
    output = rs["output"]

    updated_history = [
        *(history or []),
        {"role": "human", "content": q},
        {"role": "ai", "content": output},
    ]
    if return_history:
        return output, updated_history
    return output
