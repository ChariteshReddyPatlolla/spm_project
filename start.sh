#!/usr/bin/env bash
export PORT="${PORT:-8000}"
echo "Starting application on port $PORT..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT"

