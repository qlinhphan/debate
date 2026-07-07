from typing import TypedDict

from app.agents.check_type import QUESTION_TYPES, agent_check_types
from app.agents.one import agent_ones
from app.agents.review import agent_reviews
from app.agents.two import agent_twos


TYPE_SENTENCE = QUESTION_TYPES


class BaseInps(TypedDict, total=False):
    check: str
    inp: str
    r1: str
    r2: str
    call: int
    type_q: str
    person1: list[str]
    person2: list[str]
    agent_one_history: list[dict]
    agent_two_history: list[dict]
    review: str


def _detect_question_type(topic: str) -> str:
    result = agent_check_types(topic)
    return result if result in TYPE_SENTENCE else "Ý kiến/gợi ý"


def _initial_state(topic: str) -> BaseInps:
    return {
        "check": topic,
        "inp": topic,
        "r1": "",
        "r2": "",
        "call": 0,
        "type_q": _detect_question_type(topic),
        "person1": [],
        "person2": [],
        "agent_one_history": [],
        "agent_two_history": [],
        "review": "",
    }


def run_agent_cycle(topic: str, state: dict | None = None):
    current_state: BaseInps = state or _initial_state(topic)
    type_q = current_state.get("type_q") or _detect_question_type(topic)
    agent_one_history = current_state.get("agent_one_history", [])
    agent_two_history = current_state.get("agent_two_history", [])

    trump_input = current_state.get("r2") or current_state.get("inp") or topic
    response_1, updated_one_history = agent_ones(
        q=trump_input,
        type_sen=type_q,
        history=agent_one_history,
        return_history=True,
    )
    response_2, updated_two_history = agent_twos(
        q=response_1,
        history=agent_two_history,
        return_history=True,
    )

    person1 = [*current_state.get("person1", []), response_1]
    person2 = [*current_state.get("person2", []), response_2]
    pair_count = int(current_state.get("call", 0)) + 1
    review = current_state.get("review", "")

    updated_state: BaseInps = {
        "check": current_state.get("check", topic),
        "inp": current_state.get("inp", topic),
        "r1": response_1,
        "r2": response_2,
        "call": pair_count,
        "type_q": type_q,
        "person1": person1,
        "person2": person2,
        "agent_one_history": updated_one_history,
        "agent_two_history": updated_two_history,
        "review": review,
    }
    return updated_state, response_1, response_2, False, review


def run_agent_review(topic: str, state: dict | None = None):
    current_state: BaseInps = state or _initial_state(topic)
    review = current_state.get("review", "")
    if review:
        return current_state, review

    type_q = current_state.get("type_q") or _detect_question_type(topic)
    person1 = current_state.get("person1", [])
    person2 = current_state.get("person2", [])
    if not person1 or not person2:
        review = "Chưa có đủ dữ liệu thảo luận để kết luận."
    else:
        review = agent_reviews(
            {"person1": person1, "person2": person2},
            current_state.get("inp") or topic,
            type_q,
        )

    updated_state: BaseInps = {
        **current_state,
        "type_q": type_q,
        "review": review,
    }
    return updated_state, review
