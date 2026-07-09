import redis
import json
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
from langchain.messages import HumanMessage, AIMessage, SystemMessage
import psycopg2


HOST_POSTGRE = "10.10.50.226"
# HOST_POSTGRE = "localhost"
PORT_POSTGRE = "5432"
# DATABASE_PORTGRE = "WikiDB"
DATABASE_PORTGRE = "postgres"
USER_POSTGRE = "admin"
PASSWORD_POSTGRE = "admin123"
def get_connection():
    try:
        return psycopg2.connect(
            database="postgres",
            user="admin",
            password="admin123",
            host="10.10.50.226",
            port=5432,
        )
    except:
        return False

# class BaseInp(BaseModel):
#     exp: str
# @tool(args_schema=BaseInp)
@tool
def toolGetSQL():
    """Tool lấy dữ liệu history"""
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM history;")
    data = curr.fetchall()
    conn.close()
    return {
        "result": data
    }
llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), base_url=os.getenv("BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))

prompt = ChatPromptTemplate([
    ("system", """
Bạn là AI Agent.

Nhiệm vụ của bạn:

- Ngay khi được kích hoạt, hãy gọi tool để lấy toàn bộ dữ liệu từ cơ sở dữ liệu.
- Không hỏi lại người dùng.
- Không cần giải thích.
- Không suy luận hay tự tạo dữ liệu.
- Chỉ sử dụng dữ liệu do tool trả về.
- Sau khi tool trả về kết quả, hãy in toàn bộ dữ liệu theo định dạng dễ đọc.
- Nếu không có dữ liệu, hãy trả lời: "Không có dữ liệu trong cơ sở dữ liệu."
"""),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

def agents():
    base = create_tool_calling_agent(llm, [toolGetSQL], prompt)
    agent = AgentExecutor(agent=base, tools=[toolGetSQL])

    rs = agent.invoke({"input": ""})

    return rs


if __name__ == "__main__":
    r = redis.Redis(host="10.10.50.226", port="6379", decode_responses=True, socket_timeout=36500)
    while True: 
        _, mess = r.blpop("chat_queue")
        rs = agents()
        print(rs)





# def CheckValid(data):
    
#     llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), base_url=os.getenv("BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))

#     conversation = [
#     SystemMessage(
#         content="""
# Bạn là AI kiểm tra dữ liệu.

# Chỉ được trả lời đúng một từ:

# - valid
# - invalid

# Không được giải thích.
# """
#     ),
#     HumanMessage(
#         content=f"""
# Dữ liệu:

# {data}

# Hãy kiểm tra và chỉ trả lời valid hoặc invalid.
# """
#     )
# ]

#     response = llm.invoke(conversation)
#     print(response)

# if __name__ == "__main__":
#     r = redis.Redis(host="localhost", port=6379, decode_responses=True, socket_timeout=36500)
#     while True: 
#         _, mess = r.blpop("user_queue")
#         dicts_data = json.loads(mess)
#         id = dicts_data['user_id']
#         name = dicts_data['user_name']
#         CheckValid(data = [id, name])
#         print("=====================================")