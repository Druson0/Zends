# api.py
"""FastAPI wrapper exposing the RAG system.

Provides endpoints for user registration, login, and a POST endpoint `/ask`
that receives a JSON payload with a `question` field, runs the full RAG pipeline
(retrieval + Groq LLM), logs the query to the database, and returns the answer.
"""

import os
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, File, UploadFile
from typing import List
from pydantic import BaseModel

# Import the RAG response generator
from src.rag_system import app as rag_app, ingest_uploaded_file
# Import database helpers
from src.db import add_user, verify_user

app = FastAPI(title="Contract RAG API", version="0.1.0")

# Ensure data directory exists for uploads
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- Schemas ---

class UserAuth(BaseModel):
    """Schema for user registration and login."""
    username: str
    password: str

class QueryRequest(BaseModel):
    """Schema for incoming query payload."""
    question: str
    username: str = "anonymous"  # Default to anonymous if not provided

# --- Endpoints ---

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserAuth):
    """Register a new user in the database."""
    success = add_user(user.username, user.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    return {"message": "User registered successfully."}

@app.post("/login")
async def login_user(user: UserAuth):
    """Verify user credentials."""
    is_valid = verify_user(user.username, user.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    return {"message": "Login successful."}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a single document, save it, and ingest it into the RAG system."""
    try:
        file_path = UPLOAD_DIR / file.filename
        # Warn in response if overwriting an existing file
        already_existed = file_path.exists()
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ingest the file into the RAG system
        ingest_uploaded_file(file_path)

        msg = f"Successfully uploaded and indexed {file.filename}"
        if already_existed:
            msg += " (existing file overwritten)"
        return {"message": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/upload-batch")
async def upload_documents_batch(files: List[UploadFile] = File(...)):
    """Upload multiple documents at once and ingest each into the RAG system."""
    results = []
    for file in files:
        try:
            file_path = UPLOAD_DIR / file.filename
            already_existed = file_path.exists()
            contents = await file.read()
            with file_path.open("wb") as buffer:
                buffer.write(contents)

            ingest_uploaded_file(file_path)
            msg = f"Indexed {file.filename}"
            if already_existed:
                msg += " (overwritten)"
            results.append({"filename": file.filename, "status": "ok", "message": msg})
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "message": str(e)})
    return {"results": results}

@app.post("/ask")
async def ask_question(request: QueryRequest):
    """Answer a user's question using the RAG pipeline."""
    try:
        # Generate the answer using our LangGraph pipeline
        inputs = {"question": request.question, "username": request.username}
        final_state = {}
        for output in rag_app.stream(inputs):
            for key, value in output.items():
                final_state = value
        
        # The logging is done by the graph's log_transaction node
        answer = final_state.get("response", "No response generated.")
        confidence = final_state.get("confidence_score", 0)
        context = final_state.get("context", "No context retrieved.")
        
        return {"answer": answer, "confidence": confidence, "context": context, "status": "success"}
    except Exception as exc:
        # Propagate the error as a proper HTTP 500 response
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/documents")
async def list_documents():
    """List all custom uploaded documents."""
    files = []
    if UPLOAD_DIR.exists():
        for f in UPLOAD_DIR.iterdir():
            if f.is_file():
                size_kb = f.stat().st_size / 1024
                files.append({"filename": f.name, "size_kb": round(size_kb, 1)})
    return {"documents": files}

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and trigger index rebuild."""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        
        # Trigger index rebuild
        storage_dir = Path("./storage_v2")
        if storage_dir.exists():
            shutil.rmtree(storage_dir)
        
        # 1. Re-ingest default data
        from src.rag_system import startup_and_ingest
        startup_and_ingest({"question": ""})
        
        # 2. Re-ingest remaining uploaded files
        for f in UPLOAD_DIR.iterdir():
            if f.is_file():
                ingest_uploaded_file(f)
                
        return {"message": f"Successfully deleted {filename} and rebuilt index."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete/rebuild: {str(e)}")

# Optional health‑check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
