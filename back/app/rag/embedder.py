from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
import os


def _embedding_client():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        dimensions=512,
    )


embeddings = _embedding_client()


def embedders(text):
    return embeddings.embed_query(text)


def embed_documents(texts):
    return embeddings.embed_documents(texts)
