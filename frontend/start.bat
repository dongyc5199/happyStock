@echo off
REM ===================================================
REM happyStock 前端服务启动脚本
REM ===================================================

echo.
echo ====================================
echo   happyStock Frontend Server
echo ====================================
echo.

REM 检查是否安装了 Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js 未安装，请先安装 Node.js
    echo.
    echo 下载地址: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM 检查 node_modules 是否存在
if not exist "node_modules" (
    echo [INFO] 未找到依赖包，正在安装...
    echo.
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查 .next 缓存
if exist ".next" (
    echo [INFO] 检测到构建缓存
)

echo.
echo [INFO] 启动前端开发服务器...
echo [INFO] 访问地址: http://localhost:3000
echo [INFO] 按 Ctrl+C 停止服务
echo.

REM 启动 Next.js 开发服务器（使用 Turbopack）
call npm run dev

REM 如果服务异常退出
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] 服务启动失败，错误码: %ERRORLEVEL%
    echo.
    pause
)
