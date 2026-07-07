from dotenv import load_dotenv
load_dotenv()
import os
from pathlib import Path
import sys
from agent_rag import agent_retrieval


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import faiss
import numpy as np

from app.rag.build_faiss import build_faissed
from app.rag.chunks import chunks_data, chunks_data_docs, chunks_data_txt
from app.rag.connect_mg import connect_mgs
from app.rag.embedder import embedders


RAG_DIR = Path(__file__).resolve().parent


def main():
    mycol = connect_mgs(os.getenv("MONGO_URI"))
    user_id = "user_123"
    chunks = chunks_data_docs(str(RAG_DIR / "Detective Conan.docx"))

    data_indb = list(mycol.find({"user_id": user_id}))
    if len(data_indb) == 0:
        data_prepare = []
        for c in chunks:
            data = {}
            data['user_id'] = user_id
            data['data'] = c
            data['vector'] = embedders(c)
            data_prepare.append(data)
        mycol.insert_many(data_prepare)
        print("saved knowledge")
        build_faissed(user_id=user_id)
        data_indb = list(mycol.find({"user_id": user_id}))

    else:
        print("didn't save knowledge")

    rs = agent_retrieval("tóm tắt truyện conan")
    print(rs)

    

    

if __name__ == "__main__":
    main()
