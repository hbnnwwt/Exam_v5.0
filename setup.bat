@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Python Environment Setup
echo ========================================
echo.

set "PYTHON_DIR=%~dp0python_portable"
set "VENV_ACTIVATE=%PYTHON_DIR%\Scripts\activate.bat"

REM Check if virtual environment already exists
if exist "%VENV_ACTIVATE%" (
    echo [Info] Virtual environment already exists.
    goto :install_deps
)

REM Check if system Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [Info] System Python found:
    python --version
    echo.
    goto :create_venv
)

REM No Python found - offer to download portable version
echo [Error] Python not found on this system.
echo.
echo Options:
echo   1. Download portable Python (auto-install)
echo   2. I will install Python manually
echo.
set /p choice="Choose (1 or 2): "

if "!choice!"=="1" goto :download_python
if "!choice!"=="2" (
    echo.
    echo [Info] Please install Python 3.8+ from https://www.python.org/downloads/
    echo [Tip] During installation, check "Add Python to PATH"
    echo [Tip] After installation, run this script again.
    pause
    exit /b 0
)

echo [Error] Invalid choice.
pause
exit /b 1

:download_python
echo.
echo [Downloading] Python 3.12 portable...
echo [Info] Downloading Python embeddable package (~8MB)...
echo.

set "PYTHON_ZIP=python-3.12.0-embed-amd64.zip"
set "DOWNLOAD_URL=https://www.python.org/ftp/python/3.12.0/%PYTHON_ZIP%"

powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%~dp0%PYTHON_ZIP%'" 2>nul
if %errorlevel% neq 0 (
    echo [Error] Download failed. Please check your internet connection.
    pause
    exit /b 1
)

echo [Extracting] Python to python_portable folder...
if exist "%PYTHON_DIR%" rmdir /s /q "%PYTHON_DIR%"
powershell -Command "Expand-Archive -Path '%~dp0%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
del "%~dp0%PYTHON_ZIP%" 2>nul
del "%~dp0%PYTHON_ZIP%" 2>nul

REM Check if python.exe exists
if not exist "%PYTHON_DIR%\python.exe" (
    echo [Error] Failed to extract Python.
    pause
    exit /b 1
)

echo [Installing] pip...
REM Download get-pip.py
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%~dp0get-pip.py'" 2>nul
if exist "%~dp0get-pip.py" (
    "%PYTHON_DIR%\python.exe" "%~dp0get-pip.py" --no-warn-script-location
    del "%~dp0get-pip.py" 2>nul
)

REM Check if pip is available now
if not exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo [Error] Failed to install pip.
    pause
    exit /b 1
)

echo [Success] Python and pip installed.

:create_venv
echo.
echo [Step 1/2] Creating virtual environment...
python -m venv "%PYTHON_DIR%" 2>nul
if %errorlevel% neq 0 (
    REM Try with portable Python if system Python not available
    "%PYTHON_DIR%\python.exe" -m venv "%PYTHON_DIR%" 2>nul
    if %errorlevel% neq 0 (
        echo [Error] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:install_deps
echo.
echo [Step 2/2] Installing dependencies...

REM Use pip from venv
if exist "%PYTHON_DIR%\Scripts\pip.exe" (
    call "%VENV_ACTIVATE%"
    pip install --upgrade pip >nul 2>&1
    pip install -r "%~dp0backend\requirements.txt"
    set "install_result=%errorlevel%"
    deactivate
) else (
    echo [Error] pip not found in virtual environment.
    pause
    exit /b 1
)

if %install_result% neq 0 (
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
