@echo off
chcp 65001 >nul
echo ====================================
echo 研究生复试系统 - 开发模式
echo ====================================
echo.

cd /d "%~dp0"

REM 启动后端（后台）
echo [启动] 后端服务器 (端口 5000)...
cd backend
start "" "..\python_portable\python.exe" app.py

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端开发服务器
echo [启动] 前端开发服务器 (端口 3000)...
cd ..\frontend

REM 检查 node_modules
if not exist "node_modules" (
    echo [安装] 首次运行，安装依赖...
    call npm install
)

call npm run dev

pause
