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

# 1. What (Cái gì)
# 2. Who (Ai)
# 3. Where (Ở đâu)
# 4. When (Khi nào)
# 5. Why (Tại sao)
# 6. How (Như thế nào)
# 7. Yes/No (Có/Không)
# 8. Comparison (So sánh)
# 9. Choice (Lựa chọn)
# 10. List (Liệt kê)
# 11. Command (Lệnh/Yêu cầu thực hiện)
# 12. Calculation (Tính toán)
# 13. Creative (Sáng tạo)
# 14. Opinion/Recommendation (Ý kiến/Gợi ý)

llm = ChatOpenAI(model= os.getenv("MODEL_CHAT"), api_key= os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))

type_sentence = ["Cái gì", "Ai", "Ở đâu", "Khi nào", "Tại sao", "Như thế nào", "Có/không", "So sánh", "Liệt kê", "Lệnh/yêu cầu thực hiện", "Tính toán", "Sáng tạo", "Ý kiến/gợi ý"]

class BaseInp(BaseModel):
    exp: str = Field(description="Câu đầu vào của người dùng")
@tool(args_schema=BaseInp)
def toolCheckType(exp: str):
    """Tool dùng để kiểm tra loại câu hỏi/câu nói của người dùng"""
    print("<<<<< TOOL CHECKTYPE >>>>>")
    messages = [
        (
            "system",
            f"""Bạn là một trợ lý AI, chuyên phân tích loại câu hỏi/câu nói của người dùng
            Nhiệm vụ:
            Trả ra loại câu hỏi/câu nói mà người dùng đưa vào
            Quy tắc:
            Phải đọc kĩ câu hỏi và trả ra một trong các giá trị của {type_sentence}
            """,
        ),
        ("human", exp),
    ]
    rs = llm.invoke(messages)
    return {
        "result": rs.content
    }

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Bạn là trợ lý AI thông minh chuyên trích xuất, phân tích loại câu hỏi/câu nói của người dùng
    Nhiệm vụ:
     trích xuất loại câu hỏi câu nói
    Quy tắc
     Phải sử dụng Tool
     Nếu tool không có đáp án thì nói "Tôi không biết"
"""),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

base = create_tool_calling_agent(llm, [toolCheckType], prompt)
agents = AgentExecutor(agent=base, tools=[toolCheckType])

rs = agents.invoke({"input": "Tôi có nên đầu tư cổ phiếu vào FPT"})
print(rs['output'])