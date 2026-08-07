import sys
from pathlib import Path
from typing import Dict, Any

# Ensure BASE_DIR is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas.queryRequest import QueryRequest
from schemas.urlRequest import UrlRequest
from controller.query_controller import QueryController
from config.Config import SOURCE_DIR
from ingestion.load_from_source import ingest_async

app = FastAPI(
    title="RAG API",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = QueryController()

ALLOWED_EXTENSIONS = {"doc", "docx", "md", "txt", "text", "pdf"}


@app.get("/")
def health_check():
    return {"status": "healthy", "message": "Service is running"}


@app.get("/api/files")
def get_files():
    files = conn.get_files()
    return {"status": "success", "files": list(files)}


@app.post("/api/chat")
def get_answer(request: QueryRequest) -> Dict[str, Any]:
    query_text = request.query or ""
    if not query_text.strip():
        return {
            "status": "failed",
            "message": "Query parameter cannot be empty."
        }
    return conn.get_answer(query_text)


@app.post("/api/upload")
@app.post("/api/files/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No file filename provided.")

    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '.{ext}'. Allowed file types are: [doc, md, text, pdf]."
        )

    # Save uploaded file to source directory
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    file_path = SOURCE_DIR / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Detach & trigger asynchronous ingestion in background
    background_tasks.add_task(ingest_async, file_path)

    return {
        "status": "success",
        "message": f"File '{filename}' uploaded successfully. Async ingestion process started.",
        "filename": filename
    }


@app.post("/api/url")
@app.post("/api/url/upload")
def process_url(request: UrlRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    url = request.url.strip() if request.url else ""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter cannot be empty.")

    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

    # Detach & trigger asynchronous ingestion in background
    background_tasks.add_task(ingest_async, url)

    return {
        "status": "success",
        "message": f"URL '{url}' submitted successfully. Async ingestion process started.",
        "url": url
    }
