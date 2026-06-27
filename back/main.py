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
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from agent_one import agent_ones
from agent_two import agent_twos


class BaseInps(TypedDict):
    inp: str
    response_1: str
    response_2: str

def agent1_action(state: BaseInps):
    if state.get('response_2'):
        rs = agent_ones(state['response_2'])
        return {
            "inp": state['inp'],
            "response_1": rs,
            "response_2": state['response_2']
        }
    rs = agent_ones(state['inp'])
    return {
        "inp": state['inp'],
        "response_1": rs
    }
def agent2_action(state: BaseInps):
    rs = agent_twos(state['response_1'])
    return {
        "inp": state['inp'],
        "response_1": state['response_1'],
        "response_2": rs
    }

def routes(state: BaseInps):
    if state['response_2']:
        print("A1: ", state['response_1'])
        print("-------------------------------------------------------------------------------")
        print("A2: ", state['response_2'])
        print("===============================================================================")
        return 'a1'
    return 'a2'

graph = StateGraph(BaseInps)

graph.add_node('a1', agent1_action)
graph.add_node('a2', agent2_action)

graph.add_edge(START, 'a1')
graph.add_edge("a1", "a2")
graph.add_conditional_edges(
    "a2",
    routes,
    {
        "a1": 'a1',
        "a2": "a2"
    }
)

app = graph.compile()


def run_agent_cycle(topic: str, state: dict | None = None):
    current_state = state or {"inp": topic, "response_1": "", "response_2": ""}
    after_a1 = agent1_action(current_state)
    after_a2 = agent2_action(after_a1)
    return after_a2, after_a1.get("response_1", ""), after_a2.get("response_2", "")
