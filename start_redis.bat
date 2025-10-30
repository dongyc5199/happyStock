@echo off
REM ===================================================
REM Redis 快速启动脚本 (Docker 方式)
REM ===================================================

echo.
echo ====================================
echo   Redis 快速启动 (Docker)
echo ====================================
echo.

REM 检查 Docker 是否安装
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker 未安装
    echo.
    echo 请先安装 Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo 或参考 REDIS_SETUP.md 安装 Redis
    pause
    exit /b 1
)

echo [INFO] Docker 已安装
echo.

REM 检查是否已有 Redis 容器
docker ps -a --filter "name=happystock-redis" --format "{{.Names}}" | findstr "happystock-redis" >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] 发现已存在的 Redis 容器
    
    REM 检查容器是否运行中
    docker ps --filter "name=happystock-redis" --format "{{.Names}}" | findstr "happystock-redis" >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo [OK] Redis 容器已在运行
    ) else (
        echo [INFO] 启动已存在的容器...
        docker start happystock-redis
        if %ERRORLEVEL% neq 0 (
            echo [ERROR] 启动失败
            pause
            exit /b 1
        )
        echo [OK] Redis 容器已启动
    )
) else (
    echo [INFO] 创建新的 Redis 容器...
    docker run -d --name happystock-redis -p 6379:6379 redis
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] 创建容器失败
        pause
        exit /b 1
    )
    echo [OK] Redis 容器创建成功
)

echo.
echo [INFO] 等待 Redis 启动...
timeout /t 2 /nobreak >nul

REM 验证连接
echo [INFO] 验证 Redis 连接...
docker exec happystock-redis redis-cli ping >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Redis 连接失败
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
echo   停止: docker stop happystock-redis
echo   启动: docker start happystock-redis
echo   删除: docker rm -f happystock-redis
echo   日志: docker logs happystock-redis
echo.
echo 测试连接:
echo   docker exec happystock-redis redis-cli ping
echo.
pause
