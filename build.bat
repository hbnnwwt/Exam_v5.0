@echo off
chcp 65001 >nul
echo ====================================
echo 研究生复试系统 - 构建
echo ====================================
echo.

cd /d "%~dp0"

REM 检查 Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js
    echo [提示] 请先安装 Node.js: https://nodejs.org/
    pause
    exit /b 1
)

echo [信息] Node.js 版本:
node --version
echo.

cd frontend

REM 检查 node_modules
if not exist "node_modules" (
    echo [步骤 1] 安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo.
)

echo [步骤 2] 构建前端...
call npm run build
if errorlevel 1 (
    echo [错误] 构建失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo [成功] 构建完成！
echo [输出] backend/assets/frontend/
echo ====================================
echo.
echo 现在可以运行 run.bat 启动系统
pause
