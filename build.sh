#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=========================================="
echo " Building Multi-Paper Research Assistant  "
echo "=========================================="

echo "==> Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

echo "==> Building Vite React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "==> Initializing storage directories..."
mkdir -p storage/uploads storage/chroma storage/data

echo "==> Build complete!"

