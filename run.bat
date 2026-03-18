@echo off
chcp 65001 >nul
echo ====================================
echo Graduate Interview System - Startup
echo ====================================
echo.

cd /d "%~dp0"

set "PYTHON_DIR=%~dp0python_portable"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "VENV_DIR=%~dp0venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

REM Check Python environment priority: portable > venv > system
set "PYTHON_EXE="
if exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=%PYTHON_EXE%"
    goto :check_frontend
)

if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
    goto :check_frontend
)

where python >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where python') do set "PYTHON_EXE=%%i"
    goto :check_frontend
)

echo [Error] Python not found.
echo [Info] Please run setup.bat first to create the environment.
echo.
pause
exit /b 1

:check_frontend
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

REM Open browser
start http://localhost:5000

"%PYTHON_EXE%" app.py

pause
