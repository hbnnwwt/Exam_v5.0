@echo off
REM 运行测试脚本
cd /d "%~dp0backend"

echo ========================================
echo 运行单元测试
echo ========================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python未找到，请先安装Python
    exit /b 1
)

REM 运行测试
python -m pytest tests/ -v --tb=short

echo.
echo ========================================
echo 测试完成
echo ========================================

pause
