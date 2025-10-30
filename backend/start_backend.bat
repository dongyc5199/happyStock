@echo off
cd /d E:\work\code\happyStock\backend
echo ========================================
echo 启动 happyStock 后端服务
echo ========================================
echo.
echo [1/3] 检查 Redis...
C:\Redis\redis-cli.exe ping
if %errorlevel% neq 0 (
    echo [错误] Redis 未运行! 请先启动 Redis
    pause
    exit /b 1
)
echo [✓] Redis 运行正常
echo.
echo [2/3] 激活虚拟环境并启动服务...
pipenv run python main.py
