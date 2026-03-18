@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Python Environment Setup
echo ========================================
echo.

set "PYTHON_DIR=%~dp0python_portable"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "USE_PORTABLE=1"

REM Check if portable Python already exists
if exist "%PYTHON_EXE%" (
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
    set "USE_PORTABLE=0"
    goto :install_deps
)

REM No Python found - download portable version automatically
echo [Info] Python not found on this system.
echo [Downloading] Python 3.12 portable...
echo.

set "PYTHON_VERSION=3.12.4"
set "PYTHON_ZIP=python-%PYTHON_VERSION%-embed-amd64.zip"
set "DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_ZIP%"

powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%~dp0%PYTHON_ZIP%' -UseBasicParsing }" 2>nul
if %errorlevel% neq 0 (
    echo [Error] Download failed. Please check your internet connection.
    pause
    exit /b 1
)

echo [Extracting] Python...
if exist "%PYTHON_DIR%" rmdir /s /q "%PYTHON_DIR%"
mkdir "%PYTHON_DIR%"
powershell -Command "Expand-Archive -Path '%~dp0%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
del "%~dp0%PYTHON_ZIP%" 2>nul

if not exist "%PYTHON_EXE%" (
    echo [Error] Failed to extract Python.
    pause
    exit /b 1
)

REM Enable site-packages for embed version
echo [Configuring] Python environment...
set PTH_FILE=%PYTHON_DIR%\python312._pth
if exist "%PTH_FILE%" (
    echo import site>> "%PTH_FILE%"
)

echo [Installing] pip...
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py' -UseBasicParsing }" 2>nul
if exist "%PYTHON_DIR%\get-pip.py" (
    "%PYTHON_EXE%" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    del "%PYTHON_DIR%\get-pip.py" 2>nul
)

if not exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo [Error] Failed to install pip.
    pause
    exit /b 1
)

echo [Success] Python installed.
echo.

:install_deps
echo [Installing] Dependencies...

REM Set environment variables only for portable Python
if "%USE_PORTABLE%"=="1" (
    set "PYTHONPATH=%~dp0backend"
    set "PYTHONHOME=%PYTHON_DIR%"
) else (
    set "PYTHONPATH="
    set "PYTHONHOME="
)

REM Use python -m pip instead of pip.exe
"%PYTHON_EXE%" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn >nul 2>&1
"%PYTHON_EXE%" -m pip install -r "%~dp0backend\requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% neq 0 (
    echo [Error] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [Creating] directories...
if not exist "%~dp0backend\assets\data" mkdir "%~dp0backend\assets\data"
if not exist "%~dp0backend\assets\images" mkdir "%~dp0backend\assets\images"
if not exist "%~dp0backend\assets\logos" mkdir "%~dp0backend\assets\logos"
if not exist "%~dp0backend\assets\uploads" mkdir "%~dp0backend\assets\uploads"
if not exist "%~dp0backend\logs" mkdir "%~dp0backend\logs"

echo [Initializing] database...
"%PYTHON_EXE%" "%~dp0backend\init_db.py"
if errorlevel 1 (
    echo [Error] Database initialization failed.
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
