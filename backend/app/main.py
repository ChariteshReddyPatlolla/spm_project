import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    status_info = llm_service.get_active_provider_info()
    gemini_ready = llm_service.is_gemini_available_sync()
    ollama_ready = llm_service.is_ollama_online_sync()

    return {
        "status": "healthy",
        "documents_indexed": doc_count,
        "chunks_indexed": chunk_count,
        "llm_provider": status_info["provider"],
        "llm_model": status_info["model"],
        "llm_connected": status_info["connected"],
        "gemini_connected": gemini_ready,
        "gemini_model": settings.GEMINI_MODEL,
        "ollama_connected": ollama_ready,
        "ollama_model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "reranker_model": settings.RERANKER_MODEL_NAME
    }

# Mount and serve compiled frontend if available (Unified full-stack deployment on Render)
frontend_dist = getattr(settings, "FRONTEND_DIST", "") or os.path.join(settings.BASE_DIR, "frontend", "dist")
if os.path.isdir(frontend_dist):
    logger.info(f"Serving production frontend from: {frontend_dist}")
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith(("api/", "health", "storage/", "docs", "openapi.json")):
            return {"error": "Not found"}
        target_file = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(target_file):
            return FileResponse(target_file)
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"status": "ok", "app": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", getattr(settings, "PORT", 8000) or 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)
