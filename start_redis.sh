#!/bin/bash
# ===================================================
# Redis 快速启动脚本 (Docker 方式)
# ===================================================

echo ""
echo "===================================="
echo "   Redis 快速启动 (Docker)"
echo "===================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker 未安装"
    echo ""
    echo "请先安装 Docker:"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo "  Mac: https://docs.docker.com/desktop/mac/install/"
    echo ""
    echo "或参考 REDIS_SETUP.md 安装 Redis"
    exit 1
fi

echo "[INFO] Docker 已安装"
echo ""

# 检查是否已有 Redis 容器
if docker ps -a --filter "name=happystock-redis" --format "{{.Names}}" | grep -q "happystock-redis"; then
    echo "[INFO] 发现已存在的 Redis 容器"
    
    # 检查容器是否运行中
    if docker ps --filter "name=happystock-redis" --format "{{.Names}}" | grep -q "happystock-redis"; then
        echo "[OK] Redis 容器已在运行"
    else
        echo "[INFO] 启动已存在的容器..."
        docker start happystock-redis
        if [ $? -ne 0 ]; then
            echo "[ERROR] 启动失败"
            exit 1
        fi
        echo "[OK] Redis 容器已启动"
    fi
else
    echo "[INFO] 创建新的 Redis 容器..."
    docker run -d --name happystock-redis -p 6379:6379 redis
    if [ $? -ne 0 ]; then
        echo "[ERROR] 创建容器失败"
        exit 1
    fi
    echo "[OK] Redis 容器创建成功"
fi

echo ""
echo "[INFO] 等待 Redis 启动..."
sleep 2

# 验证连接
echo "[INFO] 验证 Redis 连接..."
if ! docker exec happystock-redis redis-cli ping &> /dev/null; then
    echo "[ERROR] Redis 连接失败"
    exit 1
fi

echo ""
echo "===================================="
echo "   Redis 启动成功！"
echo "===================================="
echo ""
echo "连接信息:"
echo "  Host: localhost"
echo "  Port: 6379"
echo "  URL:  redis://localhost:6379/0"
echo ""
echo "管理命令:"
echo "  停止: docker stop happystock-redis"
echo "  启动: docker start happystock-redis"
echo "  删除: docker rm -f happystock-redis"
echo "  日志: docker logs happystock-redis"
echo ""
echo "测试连接:"
echo "  docker exec happystock-redis redis-cli ping"
echo ""
