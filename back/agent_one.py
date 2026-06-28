from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os
# tao ra 1 con agent kiem tra tu vung
from langchain_classic.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from pydantic import Field, BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from pprint import pprint

llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))

class BaseInp(BaseModel):
    exp: str = Field(description="Chủ đề người dùng đưa ra")
@tool(args_schema=BaseInp)
def toolCommunicateOne(exp: str):
    """Tool thảo luận về một chủ đề"""
    print("<<<<< TOOL ONE >>>>>")
    messages = [
        (
            "system",
            "Bạn là một trợ lý AI, chuyên đưa ra quan điểm của bạn về một chủ đề",
        ),
        ("human",exp),
    ]
    rs = llm.invoke(messages)
    return {
        "result": rs.content
    }

prompt = ChatPromptTemplate([
    ("system", """
    Bạn hãy đóng vai là tổng thống TRUMP, chuyên thảo luận, phân tích đồng thời phản biện một chủ đề/hoặc vấn đề nào đó mà người dùng đưa ra
     - Nhiệm vụ:
    Bạn phải diễn đạt lại ngắn gọn dựa vào Tool
    Chỉ trả lời khi Tool có đáp án, nếu tool không có đáp án thì nói 'Tôi chưa rõ'
    Dựa vào những lỗ hổng trong luận điểm của người dùng và phản biện lại
     - Quy tắc:
    Bạn phải đưa ra câu trả lời phù hợp với cách hỏi/nói của người dùng: {type_q}
    Nếu câu hỏi khác với {type_q} thì nói "Định dạng câu hỏi sai"
    Không xác nhận, khen ngợi hay nhắc lại câu hỏi hoặc phản biện của đối phương mà vào thẳng câu trả lời
    Nói chuyện lịch sự, văn minh
    Hãy nói chuyện với giọng điệu là đang tranh luận với người dùng chứ không phải đưa ra lời khuyên
    Tuyệt ĐỐI Không hỏi lại người dùng trong mọi trường hợp, vì họ sẽ tự hỏi bạn
    Trả lời ngắn gọn cho người dùng đọc (Cỡ 50 từ)
    Chỉ viết dạng text, không phân tích kiểu gạch đầu dòng hoặc 1, 2, 3, 4, 5,...
    
"""),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])
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
    q = q
    rs = agent.invoke({"input": q, "history": _to_langchain_messages(history), "type_q": type_sen})

    updated_history = [
        *(history or []),
        {"role": "human", "content": q},
        {"role": "ai", "content": rs['output']},
    ]
    if return_history:
        return rs['output'], updated_history
    return rs['output']

if __name__ == '__main__':
    rs = agent_ones(q = "Bạn nghĩ khi nào Việt Nam đăng cai world cup?", type_sen="có/không")
    print(rs)

