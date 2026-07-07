from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
import os
def embedders(text):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",  # Your Azure deployment name
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        dimensions=512
    )

    # Use as normal
    vector = embeddings.embed_query(text)
    return vector