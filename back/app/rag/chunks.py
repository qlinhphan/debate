from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pprint import pprint
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def _split_documents(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    docs = text_splitter.split_documents(data)
    return [doc.page_content for doc in docs]

# handle pdf file
def chunks_data(path):
    loader = PyPDFLoader(path)
    data = loader.load()
    return _split_documents(data)

def chunks_data_docs(path):
    loader = Docx2txtLoader(path)
    docs = loader.load()
    return _split_documents(docs)

def chunks_data_txt(path):
    loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    return _split_documents(docs)


def chunks_from_file(path):
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return chunks_data(path)
    if suffix == ".docx":
        return chunks_data_docs(path)
    if suffix == ".txt":
        return chunks_data_txt(path)
    raise ValueError(f"Unsupported file type: {suffix}")

if __name__ == "__main__":
    data = chunks_data_txt("conan.txt")
    print(data)


