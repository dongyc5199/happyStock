# Sprint 2：数据模型与访问层推进记录

## 已完成成果
- `doc/sim/schema.sql` 定义 TimescaleDB 核心表（simulation_session、market_state、order_event 等）并附带 hypertable 策略；
- `doc/sim/redis_keys.md` 梳理缓存键命名、TTL 与运维要点；
- 新增 `backend/sim/` 包，包含独立的数据类 (`types.py`)、asyncpg 仓储 (`repositories.py`) 与 Unit of Work (`unit_of_work.py`)，避免影响现有 K 线 ORM；
- `backend/config.py` / `.env.example` 扩充 SIM_* 环境变量，提供仿真数据库与 Redis 配置。

## 待办事项
- [x] 根据 `schema.sql` 编写初始迁移脚本（支持 rollback），记录于 `backend/sim/migrations/`
- [ ] 在 CI 中增加 asyncpg 依赖并构建基础连通性测试脚本
- [ ] 为 `MarketStateRepository` 等仓储添加接口层适配（FastAPI 路由 `/simulate/state` 等）
- [ ] Redis 缓存策略落实到代码：实现 leaderboard / stream 写入封装

## 风险与关注点
- 仿真库与现有 SQLite/Tortoise 双线并存，需要明确哪个模块写入哪个库，防止数据混用。
- asyncpg 尚未安装，落地前需确认部署环境允许引入 Postgres 客户端依赖。
- Timescale hypertable 的 chunk 策略需在生产部署前与 DBA 评审。

## 推荐下一步
1. 使用 `scripts/sim/setup_timescale.*` 实机部署仿真数据库并执行 `schema.sql`；
2. 执行 `backend/sim/migrations/0001_initial.sql` 并在 README 中保留执行步骤（已完成，可用于部署核验）；
3. 抽象仿真用 Redis 客户端，封装成 `sim/cache.py`，为 Sprint 3 的撮合引擎做准备。


