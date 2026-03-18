@echo off
chcp 65001 >nul
echo ====================================
echo 研究生复试系统 - 启动
echo ====================================
echo.

cd /d "%~dp0"

REM 检查是否需要安装前端依赖
if not exist "frontend\node_modules" (
    echo [提示] 检测到前端依赖未安装
    echo [提示] 请先运行 build.bat 构建前端
    echo.
)

REM 检查是否需要构建前端
if not exist "backend\assets\frontend\index.html" (
    echo [警告] 前端未构建！
    echo [提示] 请先运行: cd frontend ^&^& npm install ^&^& npm run build
    echo.
    echo [提示] 现在启动开发服务器...
    echo.
)

REM 设置环境变量
set PYTHONPATH=%CD%\backend
set FLASK_ENV=development

REM 启动后端服务器
cd backend
echo [启动] Flask 服务器...
echo [地址] http://localhost:5000
echo.

"..\python_portable\python.exe" app.py

pause
