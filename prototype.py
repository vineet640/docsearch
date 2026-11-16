import re
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

pages = []
for pdf in Path("sample_pdfs").glob("*.pdf"):
    for doc in PyPDFLoader(str(pdf)).load():
        doc.page_content = " ".join(doc.page_content.split())
        doc.metadata = {"source": pdf.name, "page": doc.metadata["page"] + 1}
        pages.append(doc)

splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
chunks = splitter.split_documents(pages)

print(len(pages), "pages ->", len(chunks), "chunks")
print(chunks[0].metadata)
print(chunks[0].page_content[:150])

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

emb = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
bm25 = BM25Retriever.from_documents(chunks, k = 3, preprocess_func = lambda t: re.findall(r"\w+", t.lower()))
dense = InMemoryVectorStore.from_documents(chunks, emb).as_retriever(search_kwargs = {"k": 3})
hybrid = EnsembleRetriever(retrievers = [bm25, dense], weights = [.5, .5])

questions = [
    "Does the building need a new roof?",
    "How much does rent go up each year?",
    "Who pays for HVAC repairs?",
    "When does the lease end?",
    "Are pets allowed?",
    "What is the inspector's license number?",
]

for q in questions:
    print("\nQ:", q)
    for name, r in [("bm25", bm25), ("dense", dense), ("hybrid", hybrid)]:
        top = r.invoke(q)[0]
        print(f"  {name:6} -> {top.metadata['source']} p{top.metadata['page']}")