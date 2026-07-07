from dotenv import load_dotenv
load_dotenv()
import os
from pathlib import Path
import sys


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import faiss
import numpy as np

from app.rag.connect_mg import connect_mgs
from app.rag.embedder import embedders
from app.rag.build_faiss import build_faissed


RAG_DIR = Path(__file__).resolve().parent
DEFAULT_USER_ID = "user_123"


def retrievals(q, user_id=DEFAULT_USER_ID, k=5, min_score=0.5, with_scores=False):
    mycol = connect_mgs(os.getenv("MONGO_URI"))
    data_indb = list(mycol.find({"user_id": user_id}).sort("chunk_index", 1))
    index_path = RAG_DIR / f"{user_id}.index"
    if not data_indb:
        return []
    if not index_path.exists():
        build_faissed(user_id)

    q_em = embedders(q)
    q_em = np.reshape(np.array(q_em, dtype=np.float32), (-1, 512))
    faiss.normalize_L2(q_em)

    index = faiss.read_index(str(index_path))
    k = min(k, len(data_indb), index.ntotal)
    distances, indices = index.search(q_em, k)
    results = []
    for d, i in zip(distances[0], indices[0]):
        if i < 0 or d < min_score:
            continue
        item = data_indb[int(i)]
        result = {
            "text": item.get("data", ""),
            "score": float(d),
            "source": item.get("source", ""),
            "chunk_index": item.get("chunk_index"),
        }
        results.append(result)

    if with_scores:
        return results
    return [item["text"] for item in results]


if __name__ == "__main__":
    retrievals("conan là ai?")
