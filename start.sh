#!/bin/bash
# ===================================================
# happyStock 项目统一启动脚本 (Linux/Mac)
# 同时启动前端和后端服务
# ===================================================

echo ""
echo "============================================"
echo "       Welcome to happyStock"
echo "   Professional Trading Simulation Platform"
echo "============================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查必要的工具
echo "[1/4] 检查运行环境..."
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 未安装"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi
echo "[OK] Node.js 已安装: $(node --version)"

# 检查 pipenv
if ! command -v pipenv &> /dev/null; then
    echo "[ERROR] pipenv 未安装"
    echo "请运行: pip install pipenv"
    exit 1
fi
echo "[OK] pipenv 已安装"

# 检查 Redis
echo "[INFO] 检查 Redis 服务..."
if ! redis-cli ping &> /dev/null; then
    echo "[WARNING] Redis 未启动或未安装"
    echo ""
    echo "WebSocket 实时推送功能需要 Redis 支持"
    echo "请先启动 Redis 服务:"
    echo "  - Linux: sudo systemctl start redis"
    echo "  - Mac: brew services start redis"
    echo "  - Docker: docker run -d -p 6379:6379 redis"
    echo ""
    echo "按 Enter 继续启动 (不使用实时推送)，或 Ctrl+C 取消"
    read -r
else
    echo "[OK] Redis 服务运行中"
fi

echo ""
echo "[2/4] 检查项目依赖..."
echo ""

# 检查前端依赖
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "[INFO] 正在安装前端依赖..."
    cd "$SCRIPT_DIR/frontend"
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] 前端依赖安装失败"
        exit 1
    fi
    cd "$SCRIPT_DIR"
else
    echo "[OK] 前端依赖已安装"
fi

# 检查后端虚拟环境
cd "$SCRIPT_DIR/backend"
if ! pipenv --venv &> /dev/null; then
    echo "[INFO] 正在创建后端虚拟环境..."
    pipenv install
    if [ $? -ne 0 ]; then
        cd "$SCRIPT_DIR"
        echo "[ERROR] 后端虚拟环境创建失败"
        exit 1
    fi
else
    echo "[OK] 后端虚拟环境已创建"
fi
cd "$SCRIPT_DIR"

echo ""
echo "[3/4] 启动服务..."
echo ""
echo "[INFO] 后端服务: http://localhost:8000"
echo "[INFO] API 文档: http://localhost:8000/docs"
echo "[INFO] 前端服务: http://localhost:3000"
echo ""
echo "[提示] 按 Ctrl+C 停止所有服务"
echo ""

# 等待 2 秒
sleep 2

echo "[4/4] 正在启动..."
echo ""

# 检测操作系统
OS="$(uname -s)"

# 启动后端服务（后台运行）
cd "$SCRIPT_DIR/backend"
echo "[INFO] 启动后端服务..."
pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "[INFO] 后端服务 PID: $BACKEND_PID"
cd "$SCRIPT_DIR"

# 等待后端启动
echo "[INFO] 等待后端服务启动..."
sleep 5

# 启动前端服务（后台运行）
cd "$SCRIPT_DIR/frontend"
echo "[INFO] 启动前端服务..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "[INFO] 前端服务 PID: $FRONTEND_PID"
cd "$SCRIPT_DIR"

# 等待前端启动
sleep 3

echo ""
echo "============================================"
echo "   服务启动完成！"
echo "============================================"
echo ""
echo "后端服务: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "前端服务: http://localhost:3000"
echo ""
echo "后端 PID: $BACKEND_PID (日志: backend/backend.log)"
echo "前端 PID: $FRONTEND_PID (日志: frontend/frontend.log)"
echo ""
echo "停止服务命令:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "或运行: ./stop.sh"
echo ""

# 保存 PID 到文件
echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"

# 等待用户输入或进程结束
echo "按 Enter 查看服务状态，按 Ctrl+C 停止所有服务"
read -r

# 检查进程是否还在运行
if ps -p $BACKEND_PID > /dev/null; then
    echo "[OK] 后端服务运行中"
else
    echo "[ERROR] 后端服务已停止"
fi

if ps -p $FRONTEND_PID > /dev/null; then
    echo "[OK] 前端服务运行中"
else
    echo "[ERROR] 前端服务已停止"
fi
