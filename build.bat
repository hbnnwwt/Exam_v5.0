@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ====================================
echo Graduate Interview System - Build
echo ====================================
echo.

cd /d "%~dp0"

REM Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [Error] Node.js not found.
    echo.
    echo Options:
    echo   1. Download and install Node.js (auto)
    echo   2. I will install Node.js manually
    echo.
    set /p choice="Choose (1 or 2): "

    if "!choice!"=="1" goto :download_node
    if "!choice!"=="2" (
        echo.
        echo [Info] Please install Node.js from: https://nodejs.org/
        echo [Tip] Use LTS version (18.x or 20.x)
        echo [Tip] After installation, run build.bat again.
        pause
        exit /b 0
    )

    echo [Error] Invalid choice.
    pause
    exit /b 1

    :download_node
    echo.
    echo [Downloading] Node.js LTS...
    echo [Info] Downloading Node.js installer...

    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile '%~dp0node.msi'" 2>nul
    if errorlevel 1 (
        echo [Error] Download failed. Please check your internet connection.
        pause
        exit /b 1
    )

    echo [Installing] Node.js...
    echo [Info] This may take a minute...
    msiexec /i "%~dp0node.msi" /qn /quiet
    del "%~dp0node.msi"

    REM Wait for installation to complete
    timeout /t 10 /nobreak >nul

    REM Refresh environment variables
    where node >nul 2>&1
    if errorlevel 1 (
        echo [Warning] Node.js may require a new terminal session.
        echo [Info] Please open a new terminal and run build.bat again.
        pause
        exit /b 1
    )
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
