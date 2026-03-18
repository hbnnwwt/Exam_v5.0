@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Python Environment Setup
echo ========================================
echo.

set "PYTHON_DIR=%~dp0python_portable"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"

REM Check if portable Python already exists
if exist "%PIP_EXE%" (
    echo [Info] Python environment already exists.
    goto :install_deps
)

REM Check if system Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [Info] System Python found:
    python --version
    echo.
    set "PYTHON_EXE=python"
    set "PIP_EXE=pip"
    goto :install_deps
)

REM No Python found - download portable version automatically
echo [Info] Python not found on this system.
echo [Downloading] Python 3.12 portable...
echo.

set "PYTHON_ZIP=python-3.10.11-embed-amd64.zip"
set "DOWNLOAD_URL=https://www.python.org/ftp/python/3.10.11/%PYTHON_ZIP%"

powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%~dp0%PYTHON_ZIP%'" 2>nul
if %errorlevel% neq 0 (
    echo [Error] Download failed. Please check your internet connection.
    pause
    exit /b 1
)

echo [Extracting] Python...
if exist "%PYTHON_DIR%" rmdir /s /q "%PYTHON_DIR%"
powershell -Command "Expand-Archive -Path '%~dp0%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
del "%~dp0%PYTHON_ZIP%" 2>nul

if not exist "%PYTHON_EXE%" (
    echo [Error] Failed to extract Python.
    pause
    exit /b 1
)

echo [Installing] pip...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%~dp0get-pip.py'" 2>nul
if exist "%~dp0get-pip.py" (
    "%PYTHON_EXE%" "%~dp0get-pip.py" --no-warn-script-location
    del "%~dp0get-pip.py" 2>nul
)

if not exist "%PIP_EXE%" (
    echo [Error] Failed to install pip.
    pause
    exit /b 1
)

echo [Success] Python installed.
echo.

:install_deps
echo [Installing] Dependencies...
"%PIP_EXE%" install --upgrade pip >nul 2>&1
"%PIP_EXE%" install -r "%~dp0backend\requirements.txt"
if %errorlevel% neq 0 (
    echo [Error] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo   build.bat  - Build frontend
echo   run.bat    - Start the system
echo.

pause
