import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "Multi-Paper Research Assistant"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    CHROMA_DIR: str = str(BASE_DIR / "storage" / "chroma")
    DATA_DIR: str = str(BASE_DIR / "storage" / "data")
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/storage/data/research_assistant.db"
    FRONTEND_DIST: str = str(BASE_DIR / "frontend" / "dist")

    # LLM & Cloud Settings (Gemini & Ollama)
    LLM_PROVIDER: str = "gemini"  # "gemini" or "ollama"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    LIGHTWEIGHT_MODE: bool = True  # High-speed semantic engine optimized for cloud / Render (prevents OOM & CPU lag)

    # Server Port (Render sets $PORT dynamically)
    PORT: int = 8000

    # RAG Settings
    DEFAULT_CHUNK_SIZE: int = 800
    DEFAULT_CHUNK_OVERLAP: int = 150
    TOP_K_RETRIEVAL: int = 10
    TOP_K_RERANK: int = 5

    # OCR
    ENABLE_OCR: bool = True
    TESSERACT_CMD: str = ""


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
