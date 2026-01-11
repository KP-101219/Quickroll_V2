@echo off
echo ======================================
echo   QUICKROLL V2 - Backend API Server
echo ======================================
echo.
echo Starting backend on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
