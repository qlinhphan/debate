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
    exp: str = Field(description="Câu hỏi mà người dùng đưa ra")
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
    ("system", "Bạn là một trợ lý AI, chuyên đưa ra quan điểm của bạn về một chủ đề"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

base = create_tool_calling_agent(llm, [toolCommunicateOne], prompt)
agent = AgentExecutor(agent=base, tools=[toolCommunicateOne])


if __name__ == "__main__":
    rs = agent.invoke({"input": "Hãy thảo luận về chủ đề biến đổi khí hậu", "history": []})
    print(rs['output'])
