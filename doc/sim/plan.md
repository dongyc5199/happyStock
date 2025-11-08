## 仿真后端规划

### 目标
- 构建“内存撮合 + PostgreSQL/TimescaleDB + Redis”混合架构，支撑实时交易仿真和历史回放。
- 提供清晰的模块分层（core/agents/sim/utils/api）及可观测性接口，便于扩展 AI 教练和前端体验。

### 阶段划分
1. **架构与环境**：部署 PostgreSQL(含 Timescale 扩展) 与 Redis，完成连接配置和基础容器模板。
2. **数据模型实现**：落地 SQL 模式、Redis 缓存结构与 ORM/客户端封装，校验索引与分区策略。
3. **引擎集成**：撮合引擎 <-> Timescale <-> Redis 的闭环，外加情绪/特征计算与默认策略注册
   - `/api/sim/start` 统一返回 `202 + trace_id`，幂等校验依赖 Redis
   - `/api/sim/step` / `/api/sim/player/order` 通过 `SimulationWorker` 异步排队，并支持队列限流 + 重试
   - `SimulationService` 首次触发时自动注册散户/游资/机构/做市四类策略
   - `/api/sim/state` 返回结构增加 `features` 和 `emotion` 字段
4. **交付验证**：完善接口文档、构建性能压测脚本、整理上线/滚动升级手册。

### 依赖与风险
- TimescaleDB 如暂不可用，需回退至纯 PostgreSQL 并调整聚合策略。
- Redis 持久化与安全策略（AOF/主从）需提前规划，防止排行榜或会话状态丢失。
- 回放一致性校验需与前端/产品约定验收口径，避免重放结果与实时差异。
