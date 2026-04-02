@echo off
chcp 65001 >nul
echo ====================================
echo 研究生复试系统 - 多版本发布脚本
echo ====================================
echo.

set VERSION=Exam_v5.0
set OUTPUT_DIR=releases

:: 创建输出目录
if not exist "%~dp0%OUTPUT_DIR%" mkdir "%~dp0%OUTPUT_DIR%"
cd /d "%~dp0"

:: ============ 1. 源码版 (Source) ============
echo [1/3] 生成源码版 %VERSION%-Source.zip ...
git archive --format zip --prefix "%VERSION%-Source/" HEAD -o "%OUTPUT_DIR%/%VERSION%-Source.zip"
echo       完成: %OUTPUT_DIR%/%VERSION%-Source.zip

:: ============ 2. 发布版 (Release) ============
echo [2/3] 生成发布版 %VERSION%-release.zip ...
echo       正在构建前端...

:: 构建前端
cd frontend
call npm run build
cd ..

:: 复制构建产物到临时目录
if not exist "temp_release" mkdir temp_release
xcopy /E /Q "backend\assets\frontend" "temp_release\backend\assets\frontend\" >nul

:: 复制其他必要文件
xcopy /E /Q "backend" "temp_release\backend\" /exclude:exclude_list.txt >nul 2>&1
xcopy /E /Q "frontend\src" "temp_release\frontend\src\" >nul
xcopy /E /Q "docs" "temp_release\docs\" >nul
xcopy /Y "*.bat" "temp_release\" >nul
xcopy /Y "README.md" "temp_release\" >nul
xcopy /Y "env.example" "temp_release\" >nul

:: 打包
powershell -Command "Compress-Archive -Path 'temp_release\*' -DestinationPath '%OUTPUT_DIR%\%VERSION%-release.zip' -Force"

:: 清理临时目录
rmdir /S /Q temp_release
echo       完成: %OUTPUT_DIR%/%VERSION%-release.zip

:: ============ 3. 完全版 (Portable) ============
echo [3/3] 生成完全版 %VERSION%-portable.zip ...
echo       正在复制文件...

:: 检查 portable Python
if not exist "python_portable" (
    echo       [警告] python_portable 目录不存在！
    echo       [提示] 请先下载 Python 便携版到 python_portable 目录
    echo       跳过 Portable 版本...
) else (
    :: 复制完整项目到临时目录
    if not exist "temp_portable" mkdir temp_portable

    :: 复制所有文件
    xcopy /E /Q "backend" "temp_portable\backend\" /exclude:exclude_list.txt >nul 2>&1
    xcopy /E /Q "frontend" "temp_portable\frontend\" >nul
    xcopy /E /Q "docs" "temp_portable\docs\" >nul
    xcopy /Y "*.bat" "temp_portable\" >nul
    xcopy /Y "README.md" "temp_portable\" >nul
    xcopy /Y "env.example" "temp_portable\" >nul
    xcopy /E /Q "python_portable" "temp_portable\python_portable\" >nul

    :: 打包
    powershell -Command "Compress-Archive -Path 'temp_portable\*' -DestinationPath '%OUTPUT_DIR%\%VERSION%-portable.zip' -Force"

    :: 清理临时目录
    rmdir /S /Q temp_portable
    echo       完成: %OUTPUT_DIR%/%VERSION%-portable.zip
)

echo.
echo ====================================
echo 发布完成！
echo ====================================
echo.
dir "%~dp0%OUTPUT_DIR%"
echo.
pause
