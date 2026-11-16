from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from app import indexing

app = FastAPI(title = "DocSearch")

@app.get("/health")
def health():
    return {"status": "ok", **indexing.stats()}

@app.post("/upload")
async def upload(files: list[UploadFile], background_tasks: BackgroundTasks):
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code = 400, detail = f"{f.filename} is not a PDF")
    pdfs = [(f.filename, await f.read()) for f in files]
    background_tasks.add_task(indexing.add_documents, pdfs)
    return {"uploaded": [name for name, _ in pdfs], "status": "indexing"}
