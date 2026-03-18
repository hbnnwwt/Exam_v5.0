@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ====================================
echo Graduate Interview System - Build
echo ====================================
echo.

cd /d "%~dp0"

REM Check Node.js (check common installation paths)
set "NODE_FOUND=0"
where node >nul 2>&1
if not errorlevel 1 set "NODE_FOUND=1"
if exist "C:\Program Files\nodejs\node.exe" set "NODE_FOUND=1"
if exist "C:\Program Files (x86)\nodejs\node.exe" set "NODE_FOUND=1"

if "%NODE_FOUND%"=="0" (
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
)

REM Find node.exe path
set "NODE_EXE="
where node >nul 2>&1
if not errorlevel 1 for /f "delims=" %%i in ('where node') do set "NODE_EXE=%%i"
if "%NODE_EXE%"=="" if exist "C:\Program Files\nodejs\node.exe" set "NODE_EXE=C:\Program Files\nodejs\node.exe"
if "%NODE_EXE%"=="" if exist "C:\Program Files (x86)\nodejs\node.exe" set "NODE_EXE=C:\Program Files (x86)\nodejs\node.exe"

if "%NODE_EXE%"=="" (
    echo [Error] Node.js installation failed.
    pause
    exit /b 1
)

echo [Info] Node.js found: %NODE_EXE%
"%NODE_EXE%" --version
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
