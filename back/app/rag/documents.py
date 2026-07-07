import os
import json
import re
from pathlib import Path

from app.rag.agent_rag import agent_retrieval
from app.rag.build_faiss import build_faissed
from app.rag.chunks import SUPPORTED_EXTENSIONS, chunks_from_file
from app.rag.connect_mg import connect_mgs
from app.rag.embedder import embedders
from app.rag.retrieval import retrievals


USER_ID = "user_123"
RAG_DIR = Path(__file__).resolve().parent
BACK_DIR = RAG_DIR.parents[1]
UPLOAD_DIR = BACK_DIR / "data" / "rag_uploads"
INDEX_PATH = RAG_DIR / f"{USER_ID}.index"


def _safe_filename(filename: str) -> str:
    clean_name = Path(filename or "document").name
    return re.sub(r"[^A-Za-z0-9_.-]", "_", clean_name)


def _collection():
    return connect_mgs(os.getenv("MONGO_URI"))


def validate_document_name(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Allowed: {allowed}")
    return suffix


def save_upload(content: bytes, filename: str) -> Path:
    validate_document_name(filename)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / f"{USER_ID}_{_safe_filename(filename)}"
    file_path.write_bytes(content)
    return file_path


def reset_user_documents() -> None:
    _collection().delete_many({"user_id": USER_ID})
    if INDEX_PATH.exists():
        INDEX_PATH.unlink()


def ingest_document(file_path: Path, original_filename: str) -> dict:
    chunks = [chunk for chunk in chunks_from_file(str(file_path)) if chunk.strip()]
    if not chunks:
        raise ValueError("Document has no readable content")

    documents = []
    for index, chunk in enumerate(chunks):
        documents.append(
            {
                "user_id": USER_ID,
                "source": original_filename,
                "chunk_index": index,
                "data": chunk,
                "vector": embedders(chunk),
            }
        )

    reset_user_documents()
    _collection().insert_many(documents)
    build_faissed(USER_ID)

    return {
        "user_id": USER_ID,
        "file_name": original_filename,
        "chunk_count": len(documents),
        "index_file": INDEX_PATH.name,
    }


def query_document(question: str) -> dict:
    clean_question = (question or "").strip()
    if not clean_question:
        raise ValueError("Question is required")

    sources = retrievals(clean_question, user_id=USER_ID, k=5, min_score=0.35, with_scores=True)
    if not sources:
        return {
            "answer": "Chưa có tài liệu phù hợp để trả lời. Hãy upload tài liệu trước hoặc hỏi sát nội dung tài liệu hơn.",
            "sources": [],
        }

    answer = agent_retrieval(clean_question)
    try:
        parsed_answer = json.loads(answer)
        if isinstance(parsed_answer, dict) and isinstance(parsed_answer.get("result"), str):
            answer = parsed_answer["result"]
    except (TypeError, json.JSONDecodeError):
        pass

    return {
        "answer": answer,
        "sources": sources,
    }
