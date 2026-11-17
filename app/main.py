from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, UploadFile
from app import indexing, storage
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    files = [(p["name"], storage.read_pdf(p["name"])) for p in storage.list_pdfs()]
    indexing.add_documents(files)
    yield

app = FastAPI(title = "DocSearch", lifespan = lifespan)

@app.get("/health")
def health():
    return {"status": "ok", **indexing.stats()}

@app.post("/upload")
async def upload(files: list[UploadFile], background_tasks: BackgroundTasks):
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code = 400, detail = f"{f.filename} is not a PDF")
    pdfs = [(f.filename, await f.read()) for f in files]
    for name, data in pdfs:
        storage.save_pdf(name, data)
    background_tasks.add_task(indexing.add_documents, pdfs)
    return {"uploaded": [name for name, _ in pdfs], "status": "indexing"}

@app.get("/search")
def search(
    q: Annotated[str, Query(min_length = 2, max_length = 200)],
    k: Annotated[int, Query(ge = 1, le = 20)] = 5,
):
    results = indexing.search(q, k)
    return [
        {"document": d.metadata["source"], "page": d.metadata["page"], "snippet": d.page_content[:300], "rank": i + 1}
        for i, d in enumerate(results)
    ]

@app.get("/documents")
def documents():
    return list(storage.list_pdfs()) 

                                                                                                  