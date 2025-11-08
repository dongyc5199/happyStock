## 仿真子系统上线检查清单

### 环境与依赖
- [ ] TimescaleDB 已部署并执行 `backend/sim/migrations/0001~0003`，`scripts/verify_sim_migrations.py` 输出全 `[OK]`
- [ ] Redis 启动，开启 AOF 或其他持久化策略，并确保 `SIM_REDIS_URL` 可连通
- [ ] `.env` / `.env.local` 中的仿真数据库、Redis、异步参数（队列上限/重试次数）均已配置
- [ ] Pipenv 环境安装完成（含 `httpx`、`pytest`、`redis`、`asyncpg` 等依赖）

### 数据层
- [ ] Timescale 表 `simulation_session`、`order_event`、`trade_event`、`market_state`、`session_participant` 结构校验通过
- [ ] Redis key 前缀统一为 `sim:{session_code}`，验证 leaderboard / stream / sentiment / trace 等读写
- [ ] `FeatureService`、`EmotionService` 可从 Timescale/Redis 获取数据，或回退至安全默认值

### 业务流程
- [ ] `SimulationService.process_tick` 能回写 `session_participant`，并在结果中返回 `trace_id`、`status`
- [ ] `SimulationWorker` 启动/停止会话正常，队列满时会返回 `429`，失败任务会自动重试并记录日志
- [ ] 默认策略（散户/游资/机构/做市）在新会话首次 tick 时自动注册，可生成订单
- [ ] `/api/sim/state` 返回结构包含行情、情绪、特征指标，payload 与 Timescale/Redis 对齐

### API 与异步流程
- [ ] `/api/sim/start`、`/api/sim/step`、`/api/sim/player/order` 返回 `202 + trace_id`，支持 `X-Trace-Id` 幂等
- [ ] `/api/sim/tick` 同步接口用于调试，响应中包含最新订单/成交/快照
- [ ] `SimulationWorker.submit` 出错时能抛出明确异常（队列溢出/会话未启动等）
- [ ] 文档 (`doc/sim/README.md`、`doc/sim/plan.md`) 已更新，说明异步流程与监控入口

### 测试与验证
- [ ] 单元测试覆盖 Service、Worker、默认策略（`pipenv run pytest backend/tests/unit/test_sim_services.py`）
- [ ] 集成测试覆盖 `/sim/start`、`/sim/step`、`/sim/state` （`pipenv run pytest backend/tests/integration`）
- [x] 如需压测，使用 `scripts/sim/locust_sim.py` 并记录 ≥500 并发、≤50ms 延迟结果
- [ ] `backend/TEST_SUMMARY.md` / `TEST_CHECKLIST.md` 更新执行记录与预期结果
