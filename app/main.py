from datetime import datetime, timezone
from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, UploadFile
from app import indexing

app = FastAPI(title = "DocSearch")
uploaded: dict[str, dict] = {}

@app.get("/health")
def health():
    return {"status": "ok", **indexing.stats()}

@app.post("/upload")
async def upload(files: list[UploadFile], background_tasks: BackgroundTasks):
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code = 400, detail = f"{f.filename} is not a PDF")
    pdfs = [(f.filename, await f.read()) for f in files]
    now = datetime.now(timezone.utc)
    for name, data in pdfs:
        uploaded[name] = {"name": name, "size_bytes": len(data), "uploaded_at": now}
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
    return list(uploaded.values())