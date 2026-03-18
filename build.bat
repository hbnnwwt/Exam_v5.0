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
    echo [Info] Node.js not found.
    echo [Downloading] Node.js LTS...
    echo.

    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile '%~dp0node.msi' -UseBasicParsing }" 2>nul
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
    timeout /t 15 /nobreak >nul

    REM Refresh environment variables
    where node >nul 2>&1
    if errorlevel 1 (
        echo [Warning] Node.js requires a new terminal session.
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
