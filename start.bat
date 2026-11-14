@echo off
title Multi-Paper Research Assistant Launcher
echo ====================================================
echo Starting Multi-Paper Research Assistant System
echo ====================================================

:: Start Backend
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "SPM Backend" cmd /k "backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Start Frontend
echo Starting React Frontend on http://localhost:5173 ...
cd frontend
start "SPM Frontend" cmd /k "npm run dev"
cd ..

:: Wait 3 seconds then open browser
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo ====================================================
echo System launched! 
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo ====================================================
pause
