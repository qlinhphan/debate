from dotenv import load_dotenv
load_dotenv()
import os
from pathlib import Path
import sys


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
import faiss

from app.rag.connect_mg import connect_mgs


RAG_DIR = Path(__file__).resolve().parent


def build_faissed(user_id):
    mycol = connect_mgs(os.getenv("MONGO_URI"))
    data_indb = list(mycol.find({"user_id": user_id}).sort("chunk_index", 1))
    if not data_indb:
        raise ValueError(f"No vectors found for user_id={user_id}")

    vector = np.array([di['vector'] for di in data_indb], dtype=np.float32)

    faiss.normalize_L2(vector)
    index = faiss.IndexFlatIP(512)
    index.add(vector)

    faiss.write_index(index, str(RAG_DIR / f'{user_id}.index'))
    

# if __name__ == "__main__":
#     build_faissed()
