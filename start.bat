@echo off
REM ===================================================
REM happyStock 项目统一启动脚本
REM 同时启动前端和后端服务
REM ===================================================

echo.
echo ============================================
echo       Welcome to happyStock
echo   Professional Trading Simulation Platform
echo ============================================
echo.

REM 设置控制台编码为 UTF-8
chcp 65001 >nul 2>nul

REM 检查必要的工具
echo [1/4] 检查运行环境...
echo.

REM 检查 Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js 未安装
    echo 请先安装 Node.js: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js 已安装:
node --version

REM 检查 pipenv
where pipenv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pipenv 未安装
    echo 请运行: pip install pipenv
    pause
    exit /b 1
)
echo [OK] pipenv 已安装

echo.
echo [2/4] 检查项目依赖...
echo.

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo [INFO] 正在安装前端依赖...
    cd frontend
    call npm install
    cd ..
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] 前端依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [OK] 前端依赖已安装
)

REM 检查后端虚拟环境
cd backend
pipenv --venv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] 正在创建后端虚拟环境...
    pipenv install
    if %ERRORLEVEL% neq 0 (
        cd ..
        echo [ERROR] 后端虚拟环境创建失败
        pause
        exit /b 1
    )
) else (
    echo [OK] 后端虚拟环境已创建
)
cd ..

echo.
echo [3/4] 启动服务...
echo.
echo [INFO] 后端服务: http://localhost:8000
echo [INFO] API 文档: http://localhost:8000/docs
echo [INFO] 前端服务: http://localhost:3000
echo.
echo [提示] 按 Ctrl+C 停止所有服务
echo.

REM 等待 2 秒
timeout /t 2 /nobreak >nul

echo [4/4] 正在启动...
echo.

REM 启动后端服务（新窗口）
start "happyStock Backend" cmd /k "cd /d %~dp0backend && pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM 等待后端启动
echo [INFO] 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端服务（新窗口）
start "happyStock Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo   服务启动完成！
echo ============================================
echo.
echo 后端服务: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 前端服务: http://localhost:3000
echo.
echo 请关闭此窗口不会影响服务运行
echo 要停止服务，请关闭对应的命令窗口
echo.
pause
