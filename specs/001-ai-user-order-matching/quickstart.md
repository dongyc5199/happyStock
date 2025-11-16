# Quick Start Guide: AI-Enhanced Trading Simulation

**Feature**: 001-ai-user-order-matching
**目标用户**: 开发人员、测试人员
**预计时间**: 15 分钟

## 概述

本指南将帮助你在本地环境中启动 AI 增强的模拟交易系统，并通过 API 提交测试订单。

---

## 前置条件

### 1. 环境要求

- **Python**: 3.13+ (已安装 Pipenv)
- **PostgreSQL**: 14+ with TimescaleDB 扩展
- **Redis**: 7+
- **Node.js**: 18+ (如需测试前端)

### 2. 验证环境

```bash
python --version    # 应显示 3.13.x
psql --version      # 应显示 14.x 或更高
redis-cli --version # 应显示 7.x 或更高
```

---

## 步骤 1: 克隆代码并安装依赖

```bash
# 切换到项目目录
cd E:/work/code/happyStock

# 切换到功能分支
git checkout 001-ai-user-order-matching

# 安装后端依赖
cd backend
pipenv install

# 激活虚拟环境
pipenv shell
```

---

## 步骤 2: 配置数据库

### 2.1 创建数据库 (首次运行)

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库和用户
CREATE DATABASE happystock;
CREATE USER happystock_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE happystock TO happystock_user;

# 启用 TimescaleDB 扩展
\c happystock
CREATE EXTENSION IF NOT EXISTS timescaledb;

\q
```

### 2.2 运行迁移脚本

```bash
# 在 backend 目录下
cd E:/work/code/happyStock/backend

# 运行基础模式迁移
psql -U happystock_user -d happystock -f ../sql_scripts/create_user_table.sql

# 运行 sim 模块迁移
psql -U happystock_user -d happystock -f sim/migrations/0001_initial.sql
psql -U happystock_user -d happystock -f sim/migrations/0002_*.sql
psql -U happystock_user -d happystock -f sim/migrations/0003_*.sql

# 运行本功能的新迁移
psql -U happystock_user -d happystock -f sim/migrations/0004_user_orders.sql
psql -U happystock_user -d happystock -f sim/migrations/0005_agent_behavior_params.sql
psql -U happystock_user -d happystock -f sim/migrations/0006_trade_participant_types.sql
```

---

## 步骤 3: 配置环境变量

编辑 `backend/.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://happystock_user:your_password@localhost:5432/happystock

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 密钥（用于用户认证）
SECRET_KEY=your-secret-key-change-this-in-production

# 模拟交易配置
SIM_TICK_INTERVAL_MS=1000  # 每个 tick 间隔 1 秒
SIM_MAX_DEPTH_LEVELS=50    # 订单簿深度 50 档
```

---

## 步骤 4: 启动后端服务

### 4.1 启动 Redis

```bash
# Windows (如果使用 WSL)
redis-server

# Linux/Mac
sudo service redis-server start
```

### 4.2 启动 FastAPI 后端

```bash
cd backend

# 开发模式启动（带热重载）
pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**验证启动成功**:
访问 http://localhost:8000/docs，应该看到 Swagger API 文档。

---

## 步骤 5: 创建测试用户和会话

### 5.1 注册测试用户

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "Test123456"
  }'
```

**响应示例**:
```json
{
  "user_id": 1,
  "username": "test_user",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**保存 Token**: 后续请求需要在 Header 中携带此 Token。

### 5.2 创建模拟交易会话

```bash
curl -X POST http://localhost:8000/api/sim/sessions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "sandbox",
    "tick_interval_ms": 1000,
    "total_ticks": 1000
  }'
```

**响应示例**:
```json
{
  "session_id": 123,
  "session_code": "SIM-20251111-123",
  "status": "CREATED",
  "mode": "sandbox"
}
```

### 5.3 加入会话（创建用户账户）

```bash
curl -X POST http://localhost:8000/api/sim/sessions/123/join \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应示例**:
```json
{
  "participant_id": "user-1",
  "cash_balance": 100000.0,
  "inventory": 0.0,
  "message": "Successfully joined session"
}
```

---

## 步骤 6: 启动模拟交易

### 6.1 启动会话（开始 Tick）

```bash
curl -X POST http://localhost:8000/api/sim/sessions/123/start \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应**:
```json
{
  "status": "RUNNING",
  "current_tick": 1,
  "message": "Simulation started"
}
```

**此时后台会每秒执行一个 tick，AI 代理开始自动交易**。

---

## 步骤 7: 提交用户订单

### 7.1 查看当前订单簿

```bash
curl -X GET http://localhost:8000/api/sim/sessions/123/orderbook \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应示例**:
```json
{
  "session_id": 123,
  "tick": 15,
  "bids": [
    {"price": 50.25, "quantity": 500.0, "order_count": 12},
    {"price": 50.20, "quantity": 300.0, "order_count": 8}
  ],
  "asks": [
    {"price": 50.30, "quantity": 400.0, "order_count": 10},
    {"price": 50.35, "quantity": 600.0, "order_count": 15}
  ],
  "timestamp": "2025-11-11T10:30:05Z"
}
```

### 7.2 提交限价买单

```bash
curl -X POST http://localhost:8000/api/sim/sessions/123/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "side": "BUY",
    "order_type": "LIMIT",
    "quantity": 100.0,
    "price": 50.25
  }'
```

**响应**:
```json
{
  "status": "accepted",
  "order_id": "user-1-1699876543000-abc123",
  "message": "Order queued for next tick",
  "estimated_execution_tick": 16
}
```

### 7.3 提交市价卖单

```bash
curl -X POST http://localhost:8000/api/sim/sessions/123/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "side": "SELL",
    "order_type": "MARKET",
    "quantity": 50.0
  }'
```

---

## 步骤 8: 查询订单状态

### 8.1 查询订单详情

```bash
curl -X GET http://localhost:8000/api/sim/sessions/123/orders/user-1-1699876543000-abc123 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应示例**:
```json
{
  "order_id": "user-1-1699876543000-abc123",
  "status": "PARTIAL",
  "filled_quantity": 60.0,
  "avg_filled_price": 50.28,
  "trades": [
    {
      "trade_id": "trade-001",
      "price": 50.30,
      "quantity": 40.0,
      "counterparty_type": "ai_prop",
      "executed_at": "2025-11-11T10:30:16Z"
    },
    {
      "trade_id": "trade-002",
      "price": 50.25,
      "quantity": 20.0,
      "counterparty_type": "ai_retail",
      "executed_at": "2025-11-11T10:30:17Z"
    }
  ]
}
```

### 8.2 查询所有订单

```bash
curl -X GET "http://localhost:8000/api/sim/sessions/123/orders?status=FILLED&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 步骤 9: 撤销订单

```bash
curl -X DELETE http://localhost:8000/api/sim/sessions/123/orders/user-1-1699876543000-abc123 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应**:
```json
{
  "status": "cancelled",
  "order_id": "user-1-1699876543000-abc123",
  "cancelled_quantity": 40.0,
  "message": "Order cancelled, remaining 40.0 units will not be executed"
}
```

---

## 步骤 10: 查看 AI 代理状态

### 10.1 列出所有 AI 代理

```bash
curl -X GET http://localhost:8000/api/sim/sessions/123/agents \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应**（部分）:
```json
{
  "agents": [
    {
      "agent_id": "retail-agent-001",
      "behavior_category": "retail",
      "performance": {
        "total_trades": 45,
        "win_rate": 0.48,
        "pnl": -1500.0
      },
      "config": {
        "profit_target": 0.05,
        "herd_behavior_strength": 0.70
      }
    }
  ],
  "total": 12
}
```

### 10.2 调整 AI 代理行为（需管理员权限）

```bash
curl -X PUT http://localhost:8000/api/sim/sessions/123/agents/retail-agent-001/config \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "herd_behavior_strength": 0.85,
    "profit_target": 0.06
  }'
```

---

## 步骤 11: 停止会话

```bash
curl -X POST http://localhost:8000/api/sim/sessions/123/stop \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**响应**:
```json
{
  "status": "STOPPED",
  "total_ticks_executed": 150,
  "message": "Simulation stopped"
}
```

---

## WebSocket 实时推送（可选）

### 连接 WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/api/sim/ws');

// 订阅用户订单通知
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'user_orders',
  session_id: 123,
  token: 'YOUR_JWT_TOKEN'
}));

// 接收成交通知
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Order filled:', data);
  // {
  //   "type": "order_filled",
  //   "order_id": "user-1-...",
  //   "filled_quantity": 100.0,
  //   "avg_price": 50.30,
  //   "timestamp": "2025-11-11T10:30:20Z"
  // }
};
```

---

## 常见问题

### Q1: 订单提交后没有成交怎么办？

**A**: 检查以下几点：
1. 会话是否已启动（status=RUNNING）
2. 订单是否在合理价格范围内（查看当前订单簿）
3. 限价单需等待价格触达，市价单应立即成交

### Q2: 如何重置会话？

**A**: 停止会话后创建新会话，或使用管理员 API 清空数据：
```bash
curl -X DELETE http://localhost:8000/api/sim/sessions/123/reset \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Q3: 如何调整 AI 代理数量？

**A**: 编辑 `backend/sim/agent_pools.py` 中的 `DEFAULT_AGENT_POOLS` 配置，重启服务生效。

### Q4: 性能测试如何进行？

**A**: 使用 `backend/tests/integration/test_sim_performance.py` 中的 benchmark：
```bash
pytest backend/tests/integration/test_sim_performance.py -v
```

---

## 下一步

- 阅读 [data-model.md](./data-model.md) 了解数据结构
- 查看 [contracts/](./contracts/) 目录的完整 API 文档
- 查看 [plan.md](./plan.md) 了解实施计划
- 执行 `/speckit.tasks` 生成任务分解

---

## 故障排除

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
psql -U postgres -c "SELECT version();"

# 检查 TimescaleDB 扩展
psql -U happystock_user -d happystock -c "SELECT * FROM pg_extension WHERE extname='timescaledb';"
```

### Redis 连接失败

```bash
# 检查 Redis 是否运行
redis-cli ping  # 应返回 PONG

# 检查配置
redis-cli CONFIG GET bind
```

### API 返回 401 Unauthorized

- 确认 Token 未过期
- 检查 `backend/.env` 中的 `SECRET_KEY` 与生成 Token 时一致
- 重新登录获取新 Token

---

**文档版本**: 1.0
**最后更新**: 2025-11-11
**维护者**: happyStock 开发团队
