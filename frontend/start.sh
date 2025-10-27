#!/bin/bash
# ===================================================
# happyStock 前端服务启动脚本 (Linux/Mac)
# ===================================================

echo ""
echo "===================================="
echo "   happyStock Frontend Server"
echo "===================================="
echo ""

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 未安装，请先安装 Node.js"
    echo ""
    echo "下载地址: https://nodejs.org/"
    echo ""
    exit 1
fi

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "[INFO] 未找到依赖包，正在安装..."
    echo ""
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] 依赖安装失败"
        exit 1
    fi
fi

# 检查 .next 缓存
if [ -d ".next" ]; then
    echo "[INFO] 检测到构建缓存"
fi

echo ""
echo "[INFO] 启动前端开发服务器..."
echo "[INFO] 访问地址: http://localhost:3000"
echo "[INFO] 按 Ctrl+C 停止服务"
echo ""

# 启动 Next.js 开发服务器（使用 Turbopack）
npm run dev

# 如果服务异常退出
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] 服务启动失败"
    echo ""
    exit 1
fi
