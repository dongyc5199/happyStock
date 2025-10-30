@echo off
echo ========================================
echo 启动 happyStock 虚拟市场
echo ========================================
echo.

REM 启动后端
echo [1/2] 启动后端服务器...
start "happyStock Backend" cmd /k "cd E:\work\code\happyStock\backend && pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

REM 启动前端
echo [2/2] 启动前端服务器...
start "happyStock Frontend" cmd /k "cd E:\work\code\happyStock\frontend && npm run dev"

echo.
echo ========================================
echo ✅ 服务启动中...
echo 后端: http://localhost:8000
echo 前端: http://localhost:3000
echo ========================================
echo.
echo 按任意键退出启动脚本...
pause >nul
