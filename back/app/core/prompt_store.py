import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PROMPT_FILE = DATA_DIR / "prompt_nhieutailieu.json"
PROMPT_NAME = "prompt_nhieutailieu"

DEFAULT_MULTI_DOC_PROMPT = """Bạn là trợ lý kiểm tra lỗi trên nhiều tài liệu.

Hãy đọc toàn bộ nội dung được cung cấp, so sánh các tài liệu với nhau và trả về:
1. Các lỗi nội dung, lỗi logic hoặc mâu thuẫn giữa các tài liệu.
2. Các đoạn thiếu căn cứ, thiếu dữ liệu hoặc cần xác minh lại.
3. Gợi ý chỉnh sửa rõ ràng, ưu tiên theo mức độ ảnh hưởng.
4. Kết luận ngắn gọn cho người dùng không chuyên.

Giữ giọng văn khách quan, dễ hiểu và nêu rõ tài liệu hoặc đoạn liên quan khi có thể."""

_lock = Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_payload() -> dict[str, Any]:
    return {
        "name": PROMPT_NAME,
        "file_name": PROMPT_FILE.name,
        "prompt": DEFAULT_MULTI_DOC_PROMPT,
        "updated_at": "",
    }


def get_multi_doc_prompt() -> dict[str, Any]:
    with _lock:
        if PROMPT_FILE.exists():
            try:
                with PROMPT_FILE.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                if isinstance(data, dict) and isinstance(data.get("prompt"), str):
                    return {
                        "name": data.get("name") or PROMPT_NAME,
                        "file_name": data.get("file_name") or PROMPT_FILE.name,
                        "prompt": data["prompt"],
                        "updated_at": data.get("updated_at") or "",
                    }
            except (OSError, json.JSONDecodeError):
                pass
    return _default_payload()


def save_multi_doc_prompt(prompt: str) -> dict[str, Any]:
    clean_prompt = (prompt or "").strip() or DEFAULT_MULTI_DOC_PROMPT
    payload = {
        "name": PROMPT_NAME,
        "file_name": PROMPT_FILE.name,
        "prompt": clean_prompt,
        "updated_at": _now_iso(),
    }
    with _lock:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temp_file = PROMPT_FILE.with_suffix(".tmp")
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        temp_file.replace(PROMPT_FILE)
    return payload
