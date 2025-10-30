#!/bin/bash
# ===================================================
# happyStock 项目停止脚本 (Linux/Mac)
# ===================================================

echo ""
echo "============================================"
echo "   停止 happyStock 服务"
echo "============================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 读取 PID 文件
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

# 停止后端服务
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "[INFO] 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "[OK] 后端服务已停止"
    else
        echo "[INFO] 后端服务未运行"
    fi
    rm "$BACKEND_PID_FILE"
else
    echo "[INFO] 未找到后端服务 PID"
fi

# 停止前端服务
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "[INFO] 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "[OK] 前端服务已停止"
    else
        echo "[INFO] 前端服务未运行"
    fi
    rm "$FRONTEND_PID_FILE"
else
    echo "[INFO] 未找到前端服务 PID"
fi

# 清理日志文件（可选）
if [ -f "$SCRIPT_DIR/backend/backend.log" ]; then
    echo "[INFO] 清理后端日志..."
    rm "$SCRIPT_DIR/backend/backend.log"
fi

if [ -f "$SCRIPT_DIR/frontend/frontend.log" ]; then
    echo "[INFO] 清理前端日志..."
    rm "$SCRIPT_DIR/frontend/frontend.log"
fi

echo ""
echo "[OK] 所有服务已停止"
echo ""
