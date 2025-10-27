@echo off
REM ===================================================
REM happyStock 后端服务启动脚本
REM ===================================================

echo.
echo ====================================
echo   happyStock Backend Server
echo ====================================
echo.

REM 检查是否安装了 pipenv
where pipenv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pipenv 未安装，请先安装 pipenv
    echo.
    echo 安装命令: pip install pipenv
    echo.
    pause
    exit /b 1
)

REM 检查虚拟环境是否存在
pipenv --venv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] 未找到虚拟环境，正在创建...
    pipenv install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

echo [INFO] 检查数据库文件...
if not exist "db.sqlite3" (
    echo [INFO] 数据库文件不存在，首次启动会自动创建
)

echo.
echo [INFO] 启动后端服务...
echo [INFO] API 文档: http://localhost:8000/docs
echo [INFO] 按 Ctrl+C 停止服务
echo.

REM 启动 FastAPI 服务
pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

REM 如果服务异常退出
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] 服务启动失败，错误码: %ERRORLEVEL%
    echo.
    pause
)
