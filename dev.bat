@echo off
chcp 65001 >nul
echo ====================================
echo Graduate Interview System - Development Mode
echo ====================================
echo.

cd /d "%~dp0"

REM Check Python environment priority: portable > venv > system
set "PYTHON_EXE="

REM Check python_portable first
if exist "%~dp0python_portable\python.exe" (
    set "PYTHON_EXE=%~dp0python_portable\python.exe"
    goto :start_backend
)

REM Check venv
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
    goto :start_backend
)

REM Check system Python
where python >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where python') do set "PYTHON_EXE=%%i"
    goto :start_backend
)

echo [Error] Python not found.
echo [Info] Please run setup.bat first to create the environment.
echo.
pause
exit /b 1

:start_backend
REM Start backend (background)
echo [Starting] Backend server (port 5000)...
cd backend
start "" "%PYTHON_EXE%" app.py

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
