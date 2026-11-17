import tempfile
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from app.config import get_settings

splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)

def parse_pdf(filename: str, data: bytes) -> list[Document]:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(data)
        tmp.flush()
        pages = PyPDFLoader(tmp.name).load()
    for doc in pages:
        doc.page_content = " ".join(doc.page_content.split())
        doc.metadata = {"source": filename, "page": doc.metadata["page"] + 1}
    return splitter.split_documents(pages)

embeddings = HuggingFaceEmbeddings(model_name = get_settings().embedding_model)

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())

def build_retriever(chunks: list[Document]) -> EnsembleRetriever:
    bm25 = BM25Retriever.from_documents(chunks, k = 20, preprocess_func=_tokenize)
    dense = InMemoryVectorStore.from_documents(chunks, embeddings).as_retriever(search_kwargs = {"k": 20})
    return EnsembleRetriever(retrievers=[bm25, dense], weights = [.5, .5])

_chunks: list[Document] = []
_retriever: EnsembleRetriever | None = None

def add_documents(files: list[tuple[str, bytes]]) -> None:
    global _chunks, _retriever
    names = {name for name, _ in files}
    new_chunks = [c for c in _chunks if c.metadata["source"] not in names]
    for name, data in files:
        new_chunks += parse_pdf(name, data)
    _retriever = build_retriever(new_chunks) if new_chunks else None
    _chunks = new_chunks

def search(query: str, k: int = 5) -> list[Document]:
    if _retriever is None:
        return []
    return _retriever.invoke(query)[:k]

def stats() -> dict:
    return {"documents": len({c.metadata["source"] for c in _chunks}), "chunks": len(_chunks)}