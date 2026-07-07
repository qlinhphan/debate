import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "conversations.json"
_lock = Lock()
_store_cache: dict[str, dict[str, Any]] | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_store() -> dict[str, dict[str, Any]]:
    if not DATA_FILE.exists():
        return {}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _write_store(data: dict[str, dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp_file.replace(DATA_FILE)


def _get_store() -> dict[str, dict[str, Any]]:
    global _store_cache
    if _store_cache is None:
        _store_cache = _read_store()
    return _store_cache


def list_conversations() -> list[dict[str, Any]]:
    with _lock:
        data = _get_store()
        items = []
        for conversation_id, conversation in data.items():
            messages = conversation.get("messages") or []
            items.append(
                {
                    "id": conversation_id,
                    "topic": conversation.get("topic", ""),
                    "summary": conversation.get("summary", ""),
                    "messages": messages,
                    "review": (conversation.get("state") or {}).get("review", ""),
                    "created_at": conversation.get("created_at", ""),
                    "updated_at": conversation.get("updated_at", ""),
                }
            )
        return sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)


def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    with _lock:
        conversation = _get_store().get(conversation_id)
        return deepcopy(conversation) if conversation else None


def upsert_conversation(
    conversation_id: str,
    topic: str,
    state: dict[str, Any],
    messages: list[dict[str, Any]],
    summary: str,
) -> dict[str, Any]:
    with _lock:
        data = _get_store()
        existing = data.get(conversation_id, {})
        conversation = {
            "id": conversation_id,
            "topic": topic,
            "summary": existing.get("summary") or summary,
            "state": state,
            "messages": messages,
            "created_at": existing.get("created_at") or _now(),
            "updated_at": _now(),
        }
        data[conversation_id] = conversation
        _write_store(data)
        return deepcopy(conversation)
