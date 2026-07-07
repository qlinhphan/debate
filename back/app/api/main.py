from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, TypedDict
from uuid import uuid4

from app.core.prompt_store import get_multi_doc_prompt, save_multi_doc_prompt
from app.core.storage import get_conversation, list_conversations, upsert_conversation
from app.rag.documents import ingest_document, query_document, save_upload
from app.services.discussion import run_agent_cycle, run_agent_review


class DiscussionRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề mà người dùng muốn hai agent thảo luận")


class DiscussionResponse(BaseModel):
    topic: str
    response_1: str
    response_2: str


class ChatStepRequest(BaseModel):
    topic: str
    step: int = 0
    session_id: Optional[str] = None


class ChatStepResponse(BaseModel):
    session_id: str
    messages: list[dict]
    step: int
    done: bool
    review: Optional[str] = None


class ChatReviewRequest(BaseModel):
    topic: str
    session_id: str


class ChatReviewResponse(BaseModel):
    session_id: str
    review: str


class PromptResponse(BaseModel):
    name: str
    file_name: str
    prompt: str
    updated_at: str = ""


class PromptUpdateRequest(BaseModel):
    prompt: str


class RagQueryRequest(BaseModel):
    question: str


class RagUploadResponse(BaseModel):
    user_id: str
    file_name: str
    chunk_count: int
    index_file: str


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    source_count: int = 0
    total_chunks: int = 0


class BaseInps(TypedDict, total=False):
    inp: str
    response_1: Optional[str]
    response_2: Optional[str]


conversation_states: dict[str, dict] = {}


def summarize_topic(topic: str) -> str:
    words = topic.split()
    return " ".join(words[:5]) if words else "Cuộc trò chuyện"


def run_discussion(topic: str) -> DiscussionResponse:
    result = None
    response_1 = ""
    response_2 = ""
    for _ in range(2):
        result, response_1, response_2, _, _ = run_agent_cycle(topic, result)
    return DiscussionResponse(
        topic=topic,
        response_1=response_1,
        response_2=response_2,
    )


app = FastAPI(title="Agent Discussion API")


@app.post("/discuss", response_model=DiscussionResponse)
def discuss(request: DiscussionRequest):
    resp = run_discussion(request.topic)
    # print to console for debugging
    print(f"[discuss] topic={resp.topic}")
    print("response_1:", resp.response_1)
    print("response_2:", resp.response_2)
    return resp


@app.post('/api/chat')
def api_chat(payload: dict):
    topic = payload.get('topic', '')
    resp = run_discussion(topic)
    # print to console for debugging
    print(f"[api/chat] topic={topic}")
    print('response_1:', resp.response_1)
    print('response_2:', resp.response_2)

    # convert into messages array expected by frontend
    messages = []
    if resp.response_1:
        messages.append({"agent": 1, "text": resp.response_1})
    if resp.response_2:
        messages.append({"agent": 2, "text": resp.response_2})
    return {"messages": messages}


@app.post('/api/chat/step', response_model=ChatStepResponse)
def api_chat_step(request: ChatStepRequest):
    topic = request.topic
    step = request.step
    session_id = request.session_id or str(uuid4())
    saved_conversation = get_conversation(session_id)
    current_state = (
        saved_conversation.get("state")
        if saved_conversation
        else conversation_states.get(session_id)
    )
    updated_state, response_1, response_2, done, review = run_agent_cycle(topic, current_state)
    conversation_states[session_id] = updated_state
    messages = [
        {"agent": 1, "text": response_1},
        {"agent": 2, "text": response_2},
    ]
    all_messages = (saved_conversation.get("messages", []) if saved_conversation else []) + messages
    upsert_conversation(
        conversation_id=session_id,
        topic=topic,
        state=updated_state,
        messages=all_messages,
        summary=summarize_topic(topic),
    )
    print(f"[api/chat/step] session_id={session_id} topic={topic} step={step}")
    print(messages)
    return ChatStepResponse(
        session_id=session_id,
        messages=messages,
        step=step + 1,
        done=False,
        review=None,
    )


@app.post('/api/chat/review', response_model=ChatReviewResponse)
def api_chat_review(request: ChatReviewRequest):
    saved_conversation = get_conversation(request.session_id)
    current_state = (
        saved_conversation.get("state")
        if saved_conversation
        else conversation_states.get(request.session_id)
    )
    updated_state, review = run_agent_review(request.topic, current_state)
    conversation_states[request.session_id] = updated_state
    messages = saved_conversation.get("messages", []) if saved_conversation else []
    upsert_conversation(
        conversation_id=request.session_id,
        topic=request.topic,
        state=updated_state,
        messages=messages,
        summary=summarize_topic(request.topic),
    )
    print(f"[api/chat/review] session_id={request.session_id} topic={request.topic}")
    return ChatReviewResponse(session_id=request.session_id, review=review)


@app.get('/api/conversations')
def api_conversations():
    return {"conversations": list_conversations()}


@app.get('/api/conversations/{conversation_id}')
def api_conversation(conversation_id: str):
    conversation = get_conversation(conversation_id)
    if not conversation:
        return {"conversation": None}
    return {"conversation": conversation}


@app.get('/api/prompts/nhieutailieu', response_model=PromptResponse)
def api_get_multi_doc_prompt():
    return get_multi_doc_prompt()


@app.put('/api/prompts/nhieutailieu', response_model=PromptResponse)
def api_save_multi_doc_prompt(request: PromptUpdateRequest):
    return save_multi_doc_prompt(request.prompt)


@app.post('/api/rag/upload', response_model=RagUploadResponse)
async def api_rag_upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty")
        file_path = save_upload(content, file.filename or "document")
        return ingest_document(file_path, file.filename or file_path.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Upload failed: {error}") from error


@app.post('/api/rag/query', response_model=RagQueryResponse)
def api_rag_query(request: RagQueryRequest):
    try:
        return query_document(request.question)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Query failed: {error}") from error


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app.api.main:app', host='0.0.0.0', port=8000, reload=True)
