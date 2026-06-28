from typing import TypedDict

from agent_check_type import agent_check_types
from agent_one import agent_ones
from agent_review import agent_reviews
from agent_two import agent_twos


TYPE_SENTENCE = [
    "Cái gì",
    "Ai",
    "Ở đâu",
    "Khi nào",
    "Tại sao",
    "Như thế nào",
    "Có/không",
    "So sánh",
    "Liệt kê",
    "Lệnh/yêu cầu thực hiện",
    "Tính toán",
    "Sáng tạo",
    "Ý kiến/gợi ý",
]
MAX_DISCUSSION_PAIRS = 2


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
    for sentence_type in TYPE_SENTENCE:
        if sentence_type in result:
            return sentence_type
    return "Ý kiến/gợi ý"


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
    done = pair_count >= MAX_DISCUSSION_PAIRS
    review = current_state.get("review", "")

    if done and not review:
        review = agent_reviews(
            {"person1": person1, "person2": person2},
            current_state.get("inp") or topic,
            type_q,
        )

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
    return updated_state, response_1, response_2, done, review
