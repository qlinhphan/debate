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

class BaseInps(BaseModel):
    exp: dict = Field(description="Là dict chứa dự đoán của người thứ nhất và sự phản biện của người thứ hai")
@tool(args_schema=BaseInps)
def toolReviews(exp: dict):
    """Tool ra quyết định"""
    print("<<<<< Tool Reviews >>>>>")
    # print(exp)
    messages = [
        (
            "system",
            "Bạn là một trợ lý AI, Có nhiệm vụ đánh giá quan điểm của người thứ nhất và đọc những kiến nghị của người thứ 2 sau đó đưa ra kết luận nên làm gì"
        ),
        ("human", str(exp)),
    ]
    rs = llm.invoke(messages)
    return {
        "result": rs.content
    }

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Bạn Là trợ lý AI, chuyên review ý kiến của 2 người và đưa ra nhận xét đánh giá sau đó quyết định xem bây giờ nên làm gì thì tối ưu
    Nhiệm Vụ
     Đọc kĩ ý kiến 
     Phải sử dụng tool
     Nếu tool không có đáp án thì trả ra "Chưa đủ dữ kiện để quyết định"
     trả lời đúng loại câu hỏi/câu nói: {typew}
     câu hỏi/câu nói: {q}
     Khi tool đã có kết quả thì phải trả ra dạng JSON:
     {{
        "decide": "PHẢI quyết định làm gì bây giờ dựa vào loại câu câu hỏi và câu hỏi ví dụ hỏi khi nào thì trả lời là khi nào đó, hỏi thời gian thì nói thời điểm cụ thể. Phải tuân thủ như vậy, LƯU Ý: Bạn phải đưa ra quyết định, không nói chung chung",
        "reason": "tại sao quyết định như thế"
     }} 
    Quy tắc:
     Trước khi trả lời phải sử dụng tool
     Hỏi thời điểm thì bạn phải căn cứ vào những tài liệu là dữ liệu mà hai người trao đổi với nhau để ra quyết định, hỏi địa điểm, thời gian,.. cũng vậy
     Bạn phải ra đưa ra quyết định và không được nói chung chung
"""),
    ("user", "{aws}"),
    ("placeholder", "{agent_scratchpad}")
])

def agent_reviews(data, q, typew):
    base = create_tool_calling_agent(llm, [toolReviews], prompt)
    agent = AgentExecutor(agent=base, tools=[toolReviews])

    # n1 = ["Tôi thấy AI có thể kiểm soát thế giới", "con người tạo ra nhưng nó có thể tự suy nghĩ"]
    # n2 = ['Bạn chắc về điều đó không?, tôi thấy dù sao nó cũng do con người tạo tao', 'Thế thì trước khi tạo ra AI người ta chỉ cần gắn nốt tự hủy xong sau này nó xâm chiếm thế giới thì chỉ cần nhấn nốt là xong']
    # data = {"person1": n1, "person2": n2}

    rs = agent.invoke({"aws": data, 'q': q, "typew": typew})
    print(rs['output'])
    return rs['output']

if __name__ == '__main__':
    n1 = ["Tôi thấy AI có thể kiểm soát thế giới", "con người tạo ra nhưng nó có thể tự suy nghĩ"]
    n2 = ['Bạn chắc về điều đó không?, tôi thấy dù sao nó cũng do con người tạo tao', 'Thế thì trước khi tạo ra AI người ta chỉ cần gắn nốt tự hủy xong sau này nó xâm chiếm thế giới thì chỉ cần nhấn nốt là xong']
    data = {"person1": n1, "person2": n2}
    typw = "Có/không"
    rs = agent_reviews(data, 'AI có thể kiểm soát thế giới không?',typw)
    print(rs)


