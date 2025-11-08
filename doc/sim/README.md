# 仿真系统操作指南（更新版）

本文面向本地开发者，介绍如何启动仿真环境、执行数据库迁移、理解默认智能体策略，以及使用带 trace id 的异步接口。

## 环境准备
1. **启动 Redis**
   - Windows：`start_redis.bat`
   - macOS/Linux：`./start_redis.sh` 或 `scripts/sim/setup_redis.sh`
2. **初始化 TimescaleDB**
   - 运行 `scripts/sim/setup_timescale.ps1`（或 `.sh`）并配置 `SIM_DB_*`
3. **配置环境变量**
   - 在 `.env` / `.env.local` 中添加：
     ```dotenv
     SIM_DB_HOST=localhost
     SIM_DB_PORT=5432
     SIM_DB_USER=postgres
     SIM_DB_PASSWORD=ChangeMe123!
     SIM_DB_NAME=happystock_sim
     SIM_REDIS_URL=redis://default:SimRedisPass!@localhost:6379/1
     ```

## 数据库迁移
1. 执行初始脚本：
   ```bash
   psql postgresql://postgres:$SIM_DB_PASSWORD@localhost:5432/$SIM_DB_NAME \
     -f backend/sim/migrations/0001_initial.sql
   ```
2. 按顺序运行 `0002_order_trade_metadata.sql`、`0003_participant_code.sql`
3. 使用校验脚本确认结构：
   ```bash
   cd backend
   pipenv run python scripts/verify_sim_migrations.py
   ```
   若所有检查均为 `[OK]`，说明 Timescale 表与 hypertable 已就绪

## Redis 键约定
- 所有键使用 `sim:{session_code}` 前缀
- 榜单：`sim:{session}:leaderboard`
- 玩家快照：`sim:{session}:player:{participant}`
- 事件流：`sim:{session}:stream`
- 幂等 trace：`sim:{session}:trace:{trace_id}`（若需要持久化结果）

## 主要模块
- `backend/sim/types.py`：Timescale/Redis 数据结构
- `backend/sim/repositories.py`：基于 asyncpg 的 Timescale 读写
- `backend/sim/services.py`：撮合引擎 + Timescale + Redis 的协调层，负责生成 trace id
- `backend/sim/worker.py`：异步 Tick 队列，带队列上限与失败重试
- `backend/sim/agents/`：默认策略（散户/游资/机构/做市）及注册器

## 默认智能体策略
`SimulationService` 在每个新会话第一次处理 tick 时，会自动为该 session 注册四类策略：
- `RetailSentimentAgent`：根据 `EmotionService` 的情绪阈值追随行情
- `PropMomentumAgent`：基于波动率与平均成交量做动量交易
- `InstitutionalRebalanceAgent`：根据最大回撤进行持仓再平衡
- `MarketMakerAgent`：围绕最近成交价挂双边限价单

若 Timescale/Redis 暂不可用，策略将使用回退因子（随机或 0 值）继续生成订单。

## API 流程（HTTP 202 + Trace Id）
1. `POST /api/sim/start`
   - 创建会话，返回 `202 Accepted` 和 `trace_id`
   - 支持透传 `X-Trace-Id` 自定义幂等 key
2. `POST /api/sim/step` / `POST /api/sim/player/order`
   - 异步提交 tick，立即返回 `{ trace_id, status: "accepted" }`
   - 可通过 `X-Trace-Id` 防止重复提交，队列满时返回 `429 Too Many Requests`
3. `POST /api/sim/tick`
   - 同步执行单个 tick，返回最新订单、成交以及映射到 Timescale/Redis 的 trace id
4. `GET /api/sim/state`
   - 结果包含行情指标、实时情绪、特征快照以及原始 payload
5. `GET /api/sim/leaderboard`
   - 读取 Redis 榜单（自动落地 Timescale 时可再同步）

## 启动脚本
- `start.sh` / `start.bat`：顺序启动 Redis、后端、前端
- 调试后端可单独运行：`pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## 验证建议
1. 单元测试：`pipenv run pytest backend/tests/unit/test_sim_services.py`
2. 端到端测试：`pipenv run pytest backend/tests/integration`
3. 手动流程：
   ```bash
   curl -X POST http://localhost:8000/api/sim/start -H "Content-Type: application/json" -d '{"session_code":"demo","mode":"auto"}'
   curl -X POST http://localhost:8000/api/sim/step -H "Content-Type: application/json" -d '{"session_id":1,"session_code":"demo","tick":1,"orders":[...]}'
   curl http://localhost:8000/api/sim/state?session_id=1
   ```

若返回 503（仿真数据库不可用），请检查 Timescale 实例或在测试中跳过相关用例。

## 性能压测
- 压测脚本：`scripts/sim/locust_sim.py`（基于 Locust）。示例命令：
  ```bash
  LOCUST_LOCUSTFILE=scripts/sim/locust_sim.py \
  locust -f scripts/sim/locust_sim.py --headless \
         -u 500 -r 50 --run-time 10m \
         --host http://localhost:8000
  ```
- 通过环境变量调整行为：
  - `SIM_SESSION_PREFIX`：会话前缀，默认 `loadtest`
  - `SIM_TICK_INTERVAL_MS`：`/api/sim/start` 使用的 tick 间隔（默认 500ms）
  - `SIM_ORDERS_PER_TICK`：每个 tick 注入的订单数量（默认 2）
- Locust 会为每个用户自动启动会话、循环调用 `/api/sim/tick`、间歇性读取 `/api/sim/state`，统计吞吐与 50ms 内响应占比。

## AI 教练日志
- 每个 tick 完成后，`SimulationService` 会针对当期有成交的玩家/智能体产出教练日志，落地到 Timescale `agent_log` 表，并推送到 Redis `sim:coach:queue`（最近 1000 条）。
- 日志 JSON Schema 详见 `doc/sim/coach_schema.md`，字段包含 `headline`、`metrics`、`recommendations`，方便 AI Brooks 或前端实时消费。
- 消费方可监听 Redis 队列获取实时建议，也可直接查询 `agent_log.detail` 中的结构化信息生成历史报告。
