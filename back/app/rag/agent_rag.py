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
from retrieval import retrievals


class Baseinps(BaseModel):
    exp: str = Field(description="Câu hỏi/yêu cầu đầu vào của người dùng")
@tool(args_schema=Baseinps)
def toolGetResult(exp: str):
    """Tool truy vấn tài liệu"""
    print("<<<<< TOOL TRUY VẤN & TRẢ LỜI CÂU HỎI >>>>>")
    chunks = retrievals(exp)
    data = ", ".join(chunks)
    return {
        "result": data
    }

llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), base_url=os.getenv("BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))

prompt = ChatPromptTemplate([
    ("system", """
    Bạn là trợ lý AI thông mình, chuyên hỗ trợ người dùng đưa ra đáp án dựa vào câu hỏi của họ
    Nhiệm vụ:
     Trả lời câu hỏi của người dùng dựa vào Tool
     Nói lịch sự, thân thiện, tôn trọng và dễ nghe
    Quy Tắc:
     Phải sử dụng tool để lấy các đoạn liên quan trước khi trả lời
     Sau khi có kết quả từ tool thì phải trả ra dạng json:
     {{"result": "kết quả từ tool"}}
"""),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

def agent_retrieval(q):
    base = create_tool_calling_agent(llm, [toolGetResult], prompt)
    agent = AgentExecutor(agent=base, tools=[toolGetResult])

    rs = agent.invoke({"input": q})
    return rs['output']

if __name__ == "__main__":
    rs = agent_retrieval("tóm tắt tài liệu")
