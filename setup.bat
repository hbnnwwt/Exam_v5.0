@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Python Environment Setup
echo ========================================
echo.

set "PYTHON_DIR=%~dp0python_portable"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "VENV_DIR=%~dp0venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "USE_PORTABLE=0"

REM Check if portable Python already exists
if exist "%PYTHON_EXE%" (
    echo [Info] Portable Python found.
    set "USE_PORTABLE=1"
    goto :install_deps
)

REM Try to use py launcher (Python 3.12) - most reliable method
set "FOUND_PYTHON="
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3.12 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [Info] Python 3.12 found via py launcher.
        set "FOUND_PYTHON=py -3.12"
        goto :create_venv
    )
)

REM Search for Python 3.12 in standard locations
if exist "C:\Python312\python.exe" (
    echo [Info] Found Python 3.12 at C:\Python312.
    set "FOUND_PYTHON=C:\Python312\python.exe"
    goto :create_venv
)
if exist "C:\Program Files\Python312\python.exe" (
    echo [Info] Found Python 3.12 at Program Files.
    set "FOUND_PYTHON=C:\Program Files\Python312\python.exe"
    goto :create_venv
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    echo [Info] Found Python 3.12 in user profile.
    set "FOUND_PYTHON=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    goto :create_venv
)

REM Fallback: try system python if it's 3.12.x
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%v in ('python --version 2^>^&1') do set "VER=%%v"
    echo %VER% | findstr /C:"Python 3.12." >nul 2>&1
    if %errorlevel% equ 0 (
        echo [Info] Found Python 3.12 in PATH.
        set "FOUND_PYTHON=python"
        goto :create_venv
    )
)

REM No suitable Python found - download portable version
echo [Info] Python 3.12 not found.
echo [Downloading] Python 3.12.4 portable...
echo.

set "PYTHON_VERSION=3.12.4"
set "PYTHON_ZIP=python-%PYTHON_VERSION%-embed-amd64.zip"
set "DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_ZIP%"

powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%~dp0%PYTHON_ZIP%' -UseBasicParsing }"
if errorlevel 1 (
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
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py' -UseBasicParsing }"
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
set "USE_PORTABLE=1"
echo.
goto :install_deps

:create_venv
REM Use exact Python path with --python to create venv (not relying on PATH)
echo [Creating] Virtual environment with %FOUND_PYTHON%...
if exist "%VENV_PYTHON%" (
    echo [Info] Virtual environment already exists.
    set "PYTHON_EXE=%VENV_PYTHON%"
    goto :install_deps
)

if "%FOUND_PYTHON%"=="py -3.12" (
    py -3.12 -m venv "%VENV_DIR%"
) else (
    %FOUND_PYTHON% -m venv "%VENV_DIR%"
)
if errorlevel 1 (
    echo [Error] Failed to create virtual environment.
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_PYTHON%"
echo.

:install_deps
REM Safety check: verify Python version
for /f "delims=" %%v in ('"%PYTHON_EXE%" --version 2^>^&1') do set "ACTUAL_VERSION=%%v"
echo [Info] Using: %ACTUAL_VERSION%
echo %ACTUAL_VERSION% | findstr /C:"Python 3.12." >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python 3.12 is required but found: %ACTUAL_VERSION%
    if "%USE_PORTABLE%"=="1" (
        echo [Error] Please delete the python_portable folder, then run setup again.
    ) else (
        echo [Error] Please delete the venv folder, then run setup again.
    )
    pause
    exit /b 1
)
echo.
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
if errorlevel 1 (
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
