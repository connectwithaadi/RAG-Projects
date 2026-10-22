"""
main.py
=======
FastAPI application exposing the Company Knowledge Assistant RAG pipeline.

Endpoints:
    POST /upload  - Upload one or more documents (PDF, DOCX, TXT) and index them.
    POST /chat    - Ask a question and receive a grounded answer with sources.
    POST /reset   - Clear conversation memory.
    GET  /health  - Health check.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_chain import RAGChain  # noqa: E402
from src.utils import setup_logging, settings  # noqa: E402

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Company Knowledge Assistant API",
    description="Enterprise Retrieval Augmented Generation (RAG) API powered by Groq.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_chain = RAGChain()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question.")


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]


class UploadResponse(BaseModel):
    message: str
    files_processed: int
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    vector_store_size: int


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Simple health check endpoint."""
    return HealthResponse(status="ok", vector_store_size=rag_chain.vector_store.count)


@app.post("/upload", response_model=UploadResponse)
async def upload(files: List[UploadFile] = File(...)) -> UploadResponse:
    """Upload and index one or more PDF/DOCX/TXT documents."""
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    os.makedirs(settings.upload_dir, exist_ok=True)
    saved_paths = []

    for uploaded_file in files:
        extension = os.path.splitext(uploaded_file.filename or "")[1].lower()
        if extension not in {".pdf", ".docx", ".txt"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{extension}'. Only PDF, DOCX, and TXT are allowed.",
            )

        destination = os.path.join(settings.upload_dir, uploaded_file.filename)
        try:
            contents = await uploaded_file.read()
            if not contents:
                raise HTTPException(status_code=400, detail=f"File '{uploaded_file.filename}' is empty.")
            with open(destination, "wb") as file_handle:
                file_handle.write(contents)
            saved_paths.append(destination)
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to save uploaded file: %s", uploaded_file.filename)
            raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}") from exc

    try:
        chunks_indexed = rag_chain.ingest(saved_paths)
        rag_chain.save_index()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ingestion failed.")
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {exc}") from exc

    return UploadResponse(
        message="Files uploaded and indexed successfully.",
        files_processed=len(saved_paths),
        chunks_indexed=chunks_indexed,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Ask a question grounded in the uploaded documents."""
    try:
        result = rag_chain.ask(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat request failed.")
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}") from exc

    return ChatResponse(answer=result["answer"], sources=result["sources"])


@app.post("/reset")
def reset() -> dict:
    """Clear conversation memory."""
    rag_chain.reset()
    return {"message": "Conversation memory has been reset."}
