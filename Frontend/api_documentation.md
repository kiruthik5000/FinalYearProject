# RAG Application - API Documentation

This API documentation serves as the exact specification contract for frontend integration and UI development for the Retrieval-Augmented Generation (RAG) backend service.

---

## 1. Overview & Setup

- **Backend Framework:** FastAPI (Python)
- **Base URL:** `http://localhost:8000` (default)
- **Content Types:** `application/json`, `multipart/form-data`
- **CORS:** Enabled for all origins (`*`)

---

## 2. API Endpoints

### 2.1 System Health Check
Check whether the backend API service and database connections are active.

- **Method:** `GET`
- **Endpoint:** `/`
- **Headers:** None

#### Response `200 OK`
```json
{
  "status": "healthy",
  "message": "Service is running"
}
```

---

### 2.2 Get Ingested Files List
Retrieves all unique source files and web links currently stored in the ChromaDB vector database.

- **Method:** `GET`
- **Endpoint:** `/api/files`
- **Headers:** None

#### Response `200 OK`
```json
{
  "status": "success",
  "files": [
    "research_paper.pdf",
    "project_notes.txt",
    "https://docs.python.org/3/"
  ]
}
```

---

### 2.3 RAG Chat / Query
Submits a user query, retrieves relevant document chunks from ChromaDB, and generates a context-aware answer via LLM.

- **Method:** `POST`
- **Endpoint:** `/api/chat`
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "query": "What are the main findings in the uploaded document?"
}
```
*Note: Payload supports fallback fields (`prompt`, `message`, `text`) if `query` is omitted.*

#### Response `200 OK` (Answer Found)
```json
{
  "status": "success",
  "file_name": "research_paper.pdf",
  "page_number": "3",
  "chunk_id": 12,
  "message": "The document concludes that LLM augmentation improves accuracy by 40%."
}
```

#### Response `200 OK` (No Relevant Context Found)
```json
{
  "status": "failed",
  "message": "Cannot answer the question because the provided content is irrelevant."
}
```

---

### 2.4 Upload Document File
Uploads a document file to the backend, saves it to disk, and triggers asynchronous background ingestion into vector storage.

- **Method:** `POST`
- **Endpoint:** `/api/upload` *(Alias: `/api/files/upload`)*
- **Headers:** `Content-Type: multipart/form-data`
- **Allowed Extensions:** `.pdf`, `.doc`, `.docx`, `.md`, `.txt`, `.text`

#### Request Body (Form Data)
| Key | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | Document file to be ingested |

#### Response `200 OK`
```json
{
  "status": "success",
  "message": "File 'research_paper.pdf' uploaded successfully. Async ingestion process started.",
  "filename": "research_paper.pdf"
}
```

#### Response `400 Bad Request` (Invalid Extension)
```json
{
  "detail": "Invalid file extension '.png'. Allowed file types are: [doc, md, text, pdf]."
}
```

---

### 2.5 Ingest Website URL
Submits a web URL for web scraping and asynchronous background vector ingestion.

- **Method:** `POST`
- **Endpoint:** `/api/url` *(Alias: `/api/url/upload`)*
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
}
```
*Note: Payload supports fallback fields (`link`, `website`) if `url` is omitted.*

#### Response `200 OK`
```json
{
  "status": "success",
  "message": "URL 'https://en.wikipedia.org/wiki/Artificial_intelligence' submitted successfully. Async ingestion process started.",
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
}
```

#### Response `400 Bad Request` (Invalid URL Format)
```json
{
  "detail": "Invalid URL format. Must start with http:// or https://"
}
```

---

## 3. UI Component Architecture Specification

To build a comprehensive UI for this application, structure the frontend with the following components:

```
┌──────────────────────────────────────────────────────────────────────��─┐
│                        RAG Application Header                          │
│  [ Title ]                                  [ Status: Healthy ● ]     │
├──────────────────────────────┬─────────────────────────────────────────┤
│    Knowledge Base Panel      │             Chat Interface              │
│                              │                                         │
│ ┌──────────────────────────┐ │ ┌─────────────────────────────────────┐ │
│ │ File Upload Dropzone     │ │ │ Chat History                        │ │
│ └──────────────────────────┘ │ │                                     │ │
│ ┌──────────────────────────┐ │ │  User: What is the main topic?      │ │
│ │ URL Ingestion Bar        │ │ │  AI: The main topic is...           │ │
│ └──────────────────────────┘ │ │      [Source: doc.pdf, Page 3]      │ │
│ ┌──────────────────────────┐ │ └─────────────────────────────────────┘ │
│ │ Ingested Files List      │ │ ┌─────────────────────────────────────┐ │
│ │ - paper.pdf              │ │ │ Input: Type your question... [Send] │ │
│ │ - https://site.com       │ │ └─────────────────────────────────────┘ │
│ └──────────────────────────┘ │                                         │
└──────────────────────────────┴─────────────────────────────────────────┘
```

### Key UI Features:
1. **Source Management Drawer / Sidebar:**
   - Drag-and-drop file uploader (`.pdf`, `.docx`, `.md`, `.txt`).
   - URL input with submit button for web ingestion.
   - Live list of ingested files/links fetched from `GET /api/files`.
2. **Interactive RAG Chat Console:**
   - Message stream view with distinct User and Assistant bubbles.
   - Citation badge on AI answers displaying source `file_name` and `page_number`.
   - Loading indicator for async LLM query processing.
3. **Backend Status Indicator:**
   - Header badge displaying health status polling `GET /`.
