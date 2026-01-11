@echo off
echo ======================================
echo   QUICKROLL V2 - Desktop Application
echo ======================================
echo.
echo Checking backend connection...
echo.

REM Check if backend is running
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Backend server is not running!
    echo Please start the backend server first by running:
    echo   backend\run_server.bat
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

echo [OK] Backend server is running
echo.
echo Starting desktop application...
echo.

cd /d "%~dp0"
python ui\main_window.py
pause
