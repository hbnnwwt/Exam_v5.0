@echo off
chcp 65001 >nul
setlocal

echo ========================================
echo Python Environment Setup
echo ========================================
echo.

REM Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Create virtual environment
echo [1/3] Creating virtual environment...
if exist "python_portable\Scripts\activate.bat" (
    echo Virtual environment already exists.
) else (
    python -m venv python_portable
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Install dependencies
echo [2/3] Installing dependencies...
call python_portable\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)
deactivate

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo You can now run:
echo   run.bat    - Start the system
echo   dev.bat    - Start in development mode
echo.

pause
