import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.connection import init_db, get_db
from backend.app.database.models import Document, DocumentChunk
from backend.app.api.v1 import api_router
from backend.app.services.llm_service import llm_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database initialized successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Paper Research Assistant – Production Agentic RAG System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads for PDF previews and viewing
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/storage/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API v1 Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

@app.get("/api/v1/status")
async def system_status(db: Session = Depends(get_db)):
    doc_count = db.query(Document).count()
    chunk_count = db.query(DocumentChunk).count()
    ollama_ready = await llm_service.is_ollama_available()

    return {
        "status": "healthy",
        "documents_indexed": doc_count,
        "chunks_indexed": chunk_count,
        "ollama_connected": ollama_ready,
        "ollama_model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "reranker_model": settings.RERANKER_MODEL_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
