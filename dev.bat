@echo off
chcp 65001 >nul
echo ====================================
echo Graduate Interview System - Development Mode
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

REM Start backend (background)
echo [Starting] Backend server (port 5000)...
cd backend
start "" "..\python_portable\Scripts\python.exe" app.py

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend dev server
echo [Starting] Frontend dev server (port 3000)...
cd ..\frontend

REM Check node_modules
if not exist "node_modules" (
    echo [Installing] Installing dependencies...
    call npm install
)

call npm run dev

pause
