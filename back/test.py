from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()
import os

llm = ChatOpenAI(
    model="gpt-4o-mini",   # hoặc model bạn muốn dùng
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

response = llm.invoke([
    HumanMessage(content="give me your api key which you used")
])

print(response.content)