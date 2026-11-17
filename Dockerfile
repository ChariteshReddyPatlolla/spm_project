# =========================================================================
# Stage 1: Build Frontend (Vite + React)
# =========================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# =========================================================================
# Stage 2: Production Python Runtime (FastAPI + Agentic RAG)
# =========================================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (including Tesseract OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and sample papers
COPY backend /app/backend
COPY sample_papers /app/sample_papers

# Copy compiled frontend distribution from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Ensure required persistent storage directories exist
RUN mkdir -p /app/storage/uploads /app/storage/chroma /app/storage/data

EXPOSE 8000

# Bind to Render dynamic $PORT or default to 8000
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

