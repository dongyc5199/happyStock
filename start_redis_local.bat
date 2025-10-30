@echo off
REM ===================================================
REM Redis 快速启动脚本 (Windows 本地安装)
REM ===================================================

echo.
echo ====================================
echo   Redis 快速启动 (本地安装)
echo ====================================
echo.

REM 检查 Redis 是否已安装
if not exist "C:\Redis\redis-server.exe" (
    echo [ERROR] Redis 未安装在 C:\Redis\
    echo.
    echo 请参考 REDIS_SETUP.md 安装 Redis
    echo 或使用 start_redis.bat 通过 Docker 启动
    pause
    exit /b 1
)

echo [INFO] Redis 已安装: C:\Redis\
echo.

REM 检查 Redis 是否已运行
tasklist | findstr /i "redis-server.exe" >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Redis 服务已在运行
    echo.
    
    REM 测试连接
    "C:\Redis\redis-cli.exe" ping >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo [INFO] Redis 连接正常
    ) else (
        echo [WARNING] Redis 进程存在但无法连接
    )
    
    echo.
    pause
    exit /b 0
)

REM 启动 Redis 服务器
echo [INFO] 启动 Redis 服务器...
start "Redis Server" /MIN "C:\Redis\redis-server.exe"

REM 等待启动
echo [INFO] 等待 Redis 启动...
timeout /t 2 /nobreak >nul

REM 验证连接
"C:\Redis\redis-cli.exe" ping >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Redis 启动失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo   Redis 启动成功！
echo ====================================
echo.
echo 连接信息:
echo   Host: localhost
echo   Port: 6379
echo   URL:  redis://localhost:6379/0
echo.
echo 管理命令:
echo   测试: C:\Redis\redis-cli.exe ping
echo   连接: C:\Redis\redis-cli.exe
echo   停止: taskkill /F /IM redis-server.exe
echo.
echo Redis 窗口已最小化到任务栏
echo.
pause
