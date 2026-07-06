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

llm = ChatOpenAI(model=os.getenv("MODEL_CHAT"), api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))

class Baseinps(BaseModel):
    exp: str = Field(description="Câu đề nghị hoặc câu hỏi của người dùng")
@tool(args_schema=Baseinps)
def toolReview(exp: str):
    """Tool nhận xét trình độ tiếng anh"""
    print("===== tool review =====")
    if "good" in exp:
        return {
            "result": "Bạn nói tiếng anh rất tốt"
        }
    return {
        "result": "Bạn nói tiếng anh rất tệ"
    }

prompt = ChatPromptTemplate([
    ("system", """
    Bạn là trợ lý AI trong giáo dục, chuyên hỗ trợ mọi người nhận xét trình độ tiếng anh dựa vào câu đầu vào
    Nhiệm vụ:
     Nhận xét trình độ tiếng anh của người dùng
    QUY TẮC:
     Phải sử dụng tool
"""),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

base = create_tool_calling_agent(llm, [toolReview], prompt)
agent = AgentExecutor(agent=base, tools=[toolReview])

rs = agent.invoke({"input": "I am Link"})
print(rs['output'])