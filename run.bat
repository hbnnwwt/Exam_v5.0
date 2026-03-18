@echo off
chcp 65001 >nul
echo ====================================
echo Graduate Interview System - Startup
echo ====================================
echo.

cd /d "%~dp0"

REM Check Python environment
if not exist "python_portable\Scripts\python.exe" (
    echo [Error] Python environment not found.
    echo [Info] Please run setup.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo [Warning] Frontend dependencies not installed
    echo [Info] Please run build.bat to build the frontend
    echo.
)

REM Check if frontend is built
if not exist "backend\assets\frontend\index.html" (
    echo [Warning] Frontend not built!
    echo [Info] Please run: cd frontend ^&^& npm install ^&^& npm run build
    echo.
    echo [Info] Starting development server...
    echo.
)

REM Set environment variables
set PYTHONPATH=%CD%\backend
set FLASK_ENV=development

REM Start backend server
cd backend
echo [Starting] Flask server...
echo [URL] http://localhost:5000
echo.

"..\python_portable\Scripts\python.exe" app.py

pause
