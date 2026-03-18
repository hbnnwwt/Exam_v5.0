@echo off
chcp 65001 >nul
echo ====================================
echo Graduate Interview System - Build
echo ====================================
echo.

cd /d "%~dp0"

REM Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [Error] Node.js not found.
    echo [Info] Please install Node.js first: https://nodejs.org/
    pause
    exit /b 1
)

echo [Info] Node.js version:
node --version
echo.

cd frontend

REM Check node_modules
if not exist "node_modules" (
    echo [Step 1] Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo [Error] Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
)

echo [Step 2] Building frontend...
call npm run build
if errorlevel 1 (
    echo [Error] Build failed
    pause
    exit /b 1
)

echo.
echo ====================================
echo [Success] Build completed!
echo [Output] backend/assets/frontend/
echo ====================================
echo.
echo Now you can run run.bat to start the system
pause
