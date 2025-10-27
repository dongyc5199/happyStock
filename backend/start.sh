#!/bin/bash
# ===================================================
# happyStock 后端服务启动脚本 (Linux/Mac)
# ===================================================

echo ""
echo "===================================="
echo "   happyStock Backend Server"
echo "===================================="
echo ""

# 检查是否安装了 pipenv
if ! command -v pipenv &> /dev/null; then
    echo "[ERROR] pipenv 未安装，请先安装 pipenv"
    echo ""
    echo "安装命令: pip install pipenv"
    echo ""
    exit 1
fi

# 检查虚拟环境是否存在
if ! pipenv --venv &> /dev/null; then
    echo "[INFO] 未找到虚拟环境，正在创建..."
    pipenv install
    if [ $? -ne 0 ]; then
        echo "[ERROR] 虚拟环境创建失败"
        exit 1
    fi
fi

# 检查数据库文件
if [ ! -f "db.sqlite3" ]; then
    echo "[INFO] 数据库文件不存在，首次启动会自动创建"
fi

echo ""
echo "[INFO] 启动后端服务..."
echo "[INFO] API 文档: http://localhost:8000/docs"
echo "[INFO] 按 Ctrl+C 停止服务"
echo ""

# 启动 FastAPI 服务
pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 如果服务异常退出
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] 服务启动失败"
    echo ""
    exit 1
fi
