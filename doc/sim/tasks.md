# 仿真后端任务板

## Sprint 1：架构与环境
- [x] 编写 PostgreSQL/TimescaleDB 部署脚本，提供本地与云端两套方案
- [x] 配置 Redis 实例（AOF、监控告警、连接池参数）
- [x] 更新后端 `.env` 模板与配置加载逻辑，支持多环境切换
- [x] 提供 Docker Compose 样例，覆盖 API、Sim 引擎、数据库、缓存

## Sprint 2：数据模型与访问层
- [x] 产出 SimulationSession、MarketState、Order、Trade、AgentProfile 等表结构 SQL
- [x] 完成 Timescale hypertable、索引、分区策略，并写入迁移脚本
- [x] 设计 Redis key 命名与 TTL 策略，输出文档与封装函数
- [x] 编写 Repository/Service 层，覆盖 PostgreSQL 与 Redis 访问，附单元测试

## Sprint 3：引擎集成
- [x] 实现内存订单簿、冲击函数、情绪模型，完成核心单元测试
- [x] 打通异步持久化流水（channel/worker），确保不阻塞撮合主线程，并加入重试/限流
- [x] 输出 AI 教练日志（统一 JSON schema），对接消费方需求
- [x] 暴露接口 `/api/sim/start|step|player/order|state`，返回 202 + trace id 并编写集成测试

## Sprint 4：验证与交付
- [x] 编写压测脚本（Locust/JMeter），验证 ≥500 并发、≤50ms 延迟目标
- [ ] 完成回放一致性比对工具，抽样核验历史数据
- [ ] 整理接口文档、运行手册、回滚方案并入库 `doc/sim`
- [ ] 与前端/AI 教练团队完成一次端到端联调演示

## 运维与监控（进行中）
- [x] SimulationWorker 队列限流（默认 256）与失败重试（3 次，500ms 间隔）落地，并在代码中打印失败日志
- [x] 撰写 Runbook：包括 Redis trace 存档、队列长度监控、限流告警阈值；补充 Grafana/Kibana 接入步骤（见 `doc/sim/worker_runbook.md`）
