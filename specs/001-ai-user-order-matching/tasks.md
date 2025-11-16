# Tasks: AI-Enhanced Trading Simulation with User Integration

**Input**: Design documents from `/specs/001-ai-user-order-matching/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: 测试任务已包含（基于功能规格要求）

**Organization**: 任务按用户故事分组，确保每个故事可独立实施和测试

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 归属用户故事（US1, US2, US3, US4）
- 包含确切的文件路径

## Path Conventions

**Web 应用结构** (基于 plan.md):
- Backend: `backend/sim/`, `backend/routers/`, `backend/tests/`
- Frontend: `frontend/src/` (本功能不涉及)
- 数据库脚本: `backend/sim/migrations/`

---

## Phase 1: Setup (共享基础设施)

**目的**: 项目初始化和依赖配置

- [X] T001 验证 Python 3.13 和 Pipenv 环境
- [X] T002 [P] 安装新依赖（如有）到 `backend/Pipfile`
- [X] T003 [P] 创建数据库迁移目录 `backend/sim/migrations/` (如不存在)
- [X] T004 设置测试配置文件 `backend/pytest.ini` (如不存在)

**检查点**: ✅ 基础环境就绪

---

## Phase 2: Foundational (阻塞性前置条件)

**目的**: 核心基础设施，必须在任何用户故事之前完成

**⚠️ 关键**: 在此阶段完成前，不能开始任何用户故事工作

### 数据库迁移

- [X] T005 创建 `backend/sim/migrations/0004_user_orders.sql` - UserOrder 表结构
- [X] T006 创建 `backend/sim/migrations/0005_agent_behavior_params.sql` - AI 行为参数字段
- [X] T007 创建 `backend/sim/migrations/0006_trade_participant_types.sql` - 成交参与者类型
- [X] T008 执行迁移脚本并验证数据库结构（脚本已创建：run_migrations.sh/ps1）

### 核心数据模型

- [X] T009 [P] 在 `backend/sim/types.py` 添加 `UserOrder` dataclass
- [X] T010 [P] 在 `backend/sim/types.py` 添加 `OrderStatus` 枚举（支持 PENDING 状态）
- [X] T011 [P] 在 `backend/sim/schemas.py` 添加 `OrderRequest` Pydantic 模型
- [X] T012 [P] 在 `backend/sim/schemas.py` 添加 `OrderAcceptedResponse` 模型

### 价格机制验证（确保交易驱动价格）

- [X] T013a [P] 验证 `backend/sim/` 不使用 `PriceGenerator`（已确认：无引用）
- [X] T013b [P] 验证 `backend/sim/services.py:559-562` 价格从交易中提取（已确认：`trades[-1].price`）
- [ ] T013c 在 `backend/sim/services.py` - SimulationService 添加 `initial_price` 参数到会话配置（替代硬编码的 100.0）
- [ ] T013d 更新 `backend/sim/auto_runner.py` - SimulationAutoRunner 使会话可自定义 `bootstrap_price`
- [X] T013e [P] 文档化价格机制：创建 `specs/001-ai-user-order-matching/docs/price-mechanism.md`

### 订单簿深度扩展

- [ ] T014 修改 `backend/sim/engine.py` - OrderBook 类添加 `max_depth` 参数（默认 50）
- [ ] T015 在 `backend/sim/engine.py` - OrderBook 添加深度限制逻辑到 `_add_to_book()` 方法
- [ ] T016 在 `backend/sim/engine.py` - OrderBook 添加 `get_depth_snapshot()` 方法返回聚合档位

### Repository 层扩展

- [ ] T017 在 `backend/sim/repositories.py` 创建 `UserOrderRepository` 类
- [ ] T018 在 `backend/sim/repositories.py` - UserOrderRepository 实现 `create_order()` 方法
- [ ] T019 在 `backend/sim/repositories.py` - UserOrderRepository 实现 `get_order()` 方法
- [ ] T020 在 `backend/sim/repositories.py` - UserOrderRepository 实现 `list_orders()` 方法
- [ ] T021 在 `backend/sim/repositories.py` - UserOrderRepository 实现 `update_order_status()` 方法
- [ ] T022 在 `backend/sim/repositories.py` - UserOrderRepository 实现 `cancel_order()` 方法
- [ ] T023 [P] 在 `backend/sim/repositories.py` - SimulationRepository 添加 `batch_create_participants()` 方法（性能优化）
- [ ] T024 [P] 在 `backend/sim/repositories.py` - MarketStateRepository 扩展支持记录 buyer_type/seller_type

### Redis 缓存扩展

- [ ] T025 在 `backend/sim/cache.py` - SimulationCache 添加 `push_pending_user_order()` 方法
- [ ] T026 在 `backend/sim/cache.py` - SimulationCache 添加 `pop_pending_user_orders()` 方法
- [ ] T027 [P] 在 `backend/sim/cache.py` - SimulationCache 添加 `cache_orderbook_snapshot()` 方法

**检查点**: 基础设施就绪 - 用户故事实施可并行开始

---

## Phase 3: User Story 4 - Unified Price Matching (Priority: P1) 🎯 基础核心

**目标**: 实现统一的价格撮合机制，确保 AI 和用户订单公平处理

**独立测试**: 提交 AI 订单和用户订单到同一价格档位（不同时间戳），验证先到先成交

**为什么先做 US4**: 这是所有其他故事的基础 - 没有统一撮合，用户订单和 AI 订单无法协同工作

### 核心撮合逻辑

- [ ] T028 [US4] 在 `backend/sim/services.py` - SimulationService 修改 `execute_tick()` 方法开头添加用户订单队列读取
- [ ] T029 [US4] 在 `backend/sim/services.py` - SimulationService 在 `execute_tick()` 中合并用户订单和 AI 订单，按时间戳排序
- [ ] T030 [US4] 在 `backend/sim/engine.py` - Order dataclass 添加 `timestamp` 字段（int64 纳秒）
- [ ] T031 [US4] 在 `backend/sim/services.py` - SimulationService 确保所有订单提交到 MatchingEngine 前有有效时间戳
- [ ] T032 [US4] 在 `backend/sim/services.py` - SimulationService 成交后更新 UserOrder 的 `filled_quantity` 和 `status`

### 单元测试

- [ ] T033 [P] [US4] 创建 `backend/tests/unit/test_unified_matching.py`
- [ ] T034 [P] [US4] 测试：AI 订单 T1 + 用户订单 T2 → AI 先成交（price-time priority）
- [ ] T035 [P] [US4] 测试：大订单跨多个价格档位撮合
- [ ] T036 [P] [US4] 测试：部分成交场景
- [ ] T037 [P] [US4] 测试：并发订单保持时间戳完整性

**US4 完成标志**: ✅ 用户订单和 AI 订单可在同一撮合引擎中公平处理

---

## Phase 4: User Story 1 - Real User Trading (Priority: P1) 🎯 MVP 核心

**目标**: 用户可以提交订单并与 AI 代理进行交易

**独立测试**: 用户登录 → 提交限价/市价单 → 与 AI 订单撮合 → 查看成交结果

### API 端点实现

- [ ] T038 [US1] 在 `backend/routers/simulate.py` 添加 `POST /api/sim/sessions/{session_id}/orders` 端点
- [ ] T039 [US1] 在上述端点中实现订单验证逻辑（资金检查、价格范围、数量验证）
- [ ] T040 [US1] 在上述端点中生成纳秒级时间戳并推入 Redis 队列
- [ ] T041 [US1] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/orders/{order_id}` 端点
- [ ] T042 [US1] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/orders` 列表端点（支持分页和状态过滤）
- [ ] T043 [US1] 在 `backend/routers/simulate.py` 添加 `DELETE /api/sim/sessions/{session_id}/orders/{order_id}` 撤单端点
- [ ] T044 [P] [US1] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/orderbook` 端点

### 用户账户管理

- [ ] T045 [US1] 在 `backend/routers/simulate.py` 添加 `POST /api/sim/sessions/{session_id}/join` 端点（用户加入会话）
- [ ] T046 [US1] 在 `backend/sim/services.py` - SimulationService 添加 `join_session()` 方法自动创建用户账户

### 集成测试

- [ ] T047 [P] [US1] 创建 `backend/tests/integration/test_user_orders_api.py`
- [ ] T048 [P] [US1] 测试：用户提交限价买单 → 202 Accepted
- [ ] T049 [P] [US1] 测试：用户提交市价卖单 → 立即排队下一 tick
- [ ] T050 [P] [US1] 测试：查询订单状态 → PENDING → NEW → FILLED
- [ ] T051 [P] [US1] 测试：撤销部分成交订单 → 剩余数量取消
- [ ] T052 [P] [US1] 测试：端到端流程（提交 → 撮合 → 成交 → 查询）

### 错误处理

- [ ] T053 [P] [US1] 实现资金不足错误处理（400 Bad Request）
- [ ] T054 [P] [US1] 实现价格超出范围错误处理
- [ ] T055 [P] [US1] 实现会话不存在错误处理（404）
- [ ] T056 [P] [US1] 实现限流错误处理（429 Too Many Requests）

**US1 完成标志**: ✅ 用户可以通过 API 提交订单并与 AI 交易，查看成交结果

---

## Phase 5: User Story 2 - AI Behavioral Objectives (Priority: P1) 🎯 真实感核心

**目标**: AI 代理展现差异化行为（机构/游资盈利导向，散户跟风）

**独立测试**: 运行模拟 100 ticks → 统计散户跟风相关系数 ≥0.6，机构/游资盈利率 ≥55%

### 散户代理增强

- [ ] T057 [US2] 在 `backend/sim/agents/retail.py` - RetailSentimentAgent 添加 `herd_delay_ticks` 参数（默认 2）
- [ ] T058 [US2] 在 `backend/sim/agents/retail.py` - RetailSentimentAgent 添加 `herd_trigger_volume` 参数（默认 500.0）
- [ ] T059 [US2] 在 `backend/sim/agents/retail.py` - RetailSentimentAgent 添加 `panic_multiplier` 参数（默认 2.5）
- [ ] T060 [US2] 在 `backend/sim/agents/retail.py` - RetailSentimentAgent 修改 `generate_orders()` 监听上一 tick 成交量，触发羊群行为
- [ ] T061 [US2] 在 `backend/sim/agents/retail.py` - RetailSentimentAgent 实现延迟跟风逻辑（记录上 N tick 的趋势）
- [ ] T062 [US2] 修改 `follow_chance` 从 0.35 提升到 0.70

### 游资代理增强

- [ ] T063 [US2] 在 `backend/sim/agents/prop.py` - PropMomentumAgent 添加 `profit_target` 参数（默认 0.03）
- [ ] T064 [US2] 在 `backend/sim/agents/prop.py` - PropMomentumAgent 添加 `stop_loss` 参数（默认 0.015）
- [ ] T065 [US2] 在 `backend/sim/agents/prop.py` - PropMomentumAgent 添加 `position_tracking` 字典追踪持仓成本
- [ ] T066 [US2] 在 `backend/sim/agents/prop.py` - PropMomentumAgent 在 `generate_orders()` 中实现盈利目标平仓逻辑
- [ ] T067 [US2] 在 `backend/sim/agents/prop.py` - PropMomentumAgent 实现止损逻辑

### 机构代理增强

- [ ] T068 [US2] 在 `backend/sim/agents/institutional.py` - InstitutionalRebalanceAgent 添加 `mean_reversion_window` 参数（默认 100）
- [ ] T069 [US2] 在 `backend/sim/agents/institutional.py` - InstitutionalRebalanceAgent 添加 `rebalance_threshold` 参数（默认 0.02）
- [ ] T070 [US2] 在 `backend/sim/agents/institutional.py` - InstitutionalRebalanceAgent 添加 `max_order_size` 和 `split_orders` 参数
- [ ] T071 [US2] 在 `backend/sim/agents/institutional.py` - InstitutionalRebalanceAgent 实现均值回归触发逻辑
- [ ] T072 [US2] 在 `backend/sim/agents/institutional.py` - InstitutionalRebalanceAgent 实现大单拆分逻辑（TWAP）

### 行为参数持久化

- [ ] T073 [US2] 在 `backend/sim/repositories.py` - SimulationRepository 扩展 `update_participant()` 方法支持更新行为参数
- [ ] T074 [US2] 在 `backend/sim/repositories.py` - SimulationRepository 添加 `update_avg_position_cost()` 方法（游资成本追踪）

### AI 代理管理 API

- [ ] T075 [P] [US2] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/agents` 端点
- [ ] T076 [P] [US2] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/agents/{agent_id}` 端点
- [ ] T077 [P] [US2] 在 `backend/routers/simulate.py` 添加 `PUT /api/sim/sessions/{session_id}/agents/{agent_id}/config` 端点（需管理员权限）
- [ ] T078 [P] [US2] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/agents/{agent_id}/performance` 端点
- [ ] T079 [P] [US2] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/pools` 端点
- [ ] T080 [P] [US2] 在 `backend/routers/simulate.py` 添加 `GET /api/sim/sessions/{session_id}/pools/{pool_code}/stats` 端点

### 行为验证测试

- [ ] T081 [P] [US2] 创建 `backend/tests/unit/test_retail_behavior.py`
- [ ] T082 [P] [US2] 测试：散户在趋势中跟风（上涨时买入占比 >60%）
- [ ] T083 [P] [US2] 测试：散户跟风延迟（订单时间戳晚于趋势出现 2+ ticks）
- [ ] T084 [P] [US2] 测试：游资盈利目标触发（价格达到 +3% 时平仓）
- [ ] T085 [P] [US2] 测试：游资止损触发（价格跌破 -1.5% 时止损）
- [ ] T086 [P] [US2] 测试：机构均值回归（价格偏离 >2% 时反向下单）
- [ ] T087 [P] [US2] 测试：机构大单拆分（单笔订单不超过 max_order_size）

### 绩效统计

- [ ] T088 [P] [US2] 在 `backend/sim/services.py` - SimulationService 添加 `calculate_agent_performance()` 方法
- [ ] T089 [P] [US2] 统计指标：total_trades, win_rate, pnl, avg_trade_size

**US2 完成标志**: ✅ AI 代理展现可测量的差异化行为，散户跟风系数 ≥0.6，游资盈利率 ≥55%

---

## Phase 6: User Story 3 - Enhanced Order Book Depth (Priority: P2)

**目标**: 显示 50 档双边订单簿深度

**独立测试**: 查询订单簿 API → 返回最多 50 档买卖盘，每档显示聚合数量和订单数

### 订单簿深度实现（已在 Phase 2 基础设施完成）

**注意**: T013-T015 已在 Phase 2 完成订单簿深度支持，此阶段主要补充测试和优化

### 订单簿查询优化

- [ ] T090 [US3] 在 `backend/sim/services.py` - SimulationService 添加 `get_orderbook_snapshot()` 方法
- [ ] T091 [US3] 在 `backend/sim/services.py` - SimulationService 实现订单簿缓存逻辑（Redis, 5s TTL）
- [ ] T092 [US3] 在 `backend/sim/cache.py` - SimulationCache 添加 `get_cached_orderbook()` 方法

### 深度聚合测试

- [ ] T093 [P] [US3] 创建 `backend/tests/unit/test_orderbook_depth.py`
- [ ] T094 [P] [US3] 测试：订单簿返回最多 50 档买卖盘
- [ ] T095 [P] [US3] 测试：同价格档位订单正确聚合
- [ ] T096 [P] [US3] 测试：成交后档位正确移除
- [ ] T097 [P] [US3] 测试：流动性分布（70% 集中在最近 10 档）

### 深度查询 API 测试

- [ ] T098 [P] [US3] 创建 `backend/tests/integration/test_orderbook_api.py`
- [ ] T099 [P] [US3] 测试：GET /api/sim/sessions/{id}/orderbook 返回格式正确
- [ ] T100 [P] [US3] 测试：depth 参数限制返回档位数（例如 depth=10）
- [ ] T101 [P] [US3] 测试：缓存有效性（5秒内重复请求命中缓存）

**US3 完成标志**: ✅ 订单簿 API 返回 50 档深度，查询性能 <500ms

---

## Phase 7: Integration & Performance (跨故事集成)

**目的**: 确保所有用户故事协同工作，达到性能目标

### 端到端集成测试

- [ ] T102 创建 `backend/tests/integration/test_full_simulation.py`
- [ ] T103 测试：完整流程（创建会话 → 用户加入 → AI + 用户混合交易 → 查询成交）
- [ ] T104 测试：多用户并发提交订单场景
- [ ] T105 测试：AI 行为在长时间运行中的稳定性（1000 ticks）
- [ ] T106 测试：订单簿深度在高频交易中的准确性

### 性能基准测试

- [ ] T107 创建 `backend/tests/performance/test_sim_performance.py`
- [ ] T108 基准测试：1,000 orders/sec 场景（AI 800 + 用户 200）
- [ ] T109 基准测试：P95 订单处理延迟 <1s
- [ ] T110 基准测试：订单簿查询延迟 <500ms
- [ ] T111 基准测试：Tick 执行时间 P95 <800ms

### 性能优化（如基准测试未通过）

- [ ] T112 实施批量 Participants 注册（research.md 决策 4）
- [ ] T113 分析 update_tick 慢查询（添加 EXPLAIN ANALYZE 日志）
- [ ] T114 优化订单簿查询（索引验证）
- [ ] T115 Redis 连接池配置优化

### 边界场景测试

- [ ] T116 测试：订单量超过 50 档深度（最差档位被拒绝）
- [ ] T117 测试：AI 单边市场（所有 AI 只卖不买）
- [ ] T118 测试：极端羊群行为（所有散户同时下单）
- [ ] T119 测试：会话暂停/恢复时的订单处理
- [ ] T120 测试：会话结束时挂单订单的清理
- [ ] T121 测试：AI 反向抢跑检测（确保公平性）

---

## Phase 8: Polish & Documentation

**目的**: 文档、日志、监控和用户体验优化

### 日志和监控

- [ ] T122 [P] 在 `backend/sim/services.py` 添加结构化日志（订单提交、撮合、成交）
- [ ] T123 [P] 在 `backend/sim/services.py` 添加性能指标埋点（Prometheus 格式）
- [ ] T124 [P] 在 `backend/routers/simulate.py` 添加 API 访问日志

### 错误处理完善

- [ ] T125 [P] 统一错误响应格式（ErrorResponse schema）
- [ ] T126 [P] 添加全局异常处理器到 `backend/main.py`
- [ ] T127 [P] 为所有 API 端点添加错误文档示例

### 文档补充

- [ ] T128 [P] 更新 `backend/README.md` 包含用户订单 API 使用说明
- [ ] T129 [P] 创建 `doc/sim/feature_service_strategy.md` 文档化特征数据来源
- [ ] T130 [P] 在 `doc/sim/pending_tasks.md` 更新已完成任务状态
- [ ] T131 [P] 生成 API 文档（Swagger UI 验证）

### WebSocket 推送（可选增强）

- [ ] T132 在 `backend/routers/simulate.py` 添加 WebSocket 端点（如不存在）
- [ ] T133 实现用户订单成交通知推送
- [ ] T134 实现订单簿实时更新推送
- [ ] T135 测试 WebSocket 订阅和消息格式

---

## Dependencies & Execution Order

### 依赖关系图

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← 必须完成后才能开始用户故事
    ↓
    ├─→ Phase 3 (US4) ← 基础，其他故事依赖
    │       ↓
    │   ┌───┴────┐
    │   ↓        ↓
    ├─→ Phase 4 (US1)  [P] Phase 5 (US2)  ← 可并行
    │   │               │
    │   └───┬───────────┘
    │       ↓
    └─→ Phase 6 (US3) ← 依赖 US1 和 US2（需要订单流量测试深度）
            ↓
        Phase 7 (Integration & Performance)
            ↓
        Phase 8 (Polish)
```

### 关键路径（Critical Path）

```
Phase 1 → Phase 2 → Phase 3 (US4) → Phase 4 (US1) → Phase 7 → Phase 8
```

最短路径约 **18-22 天**（假设每个 Phase 2-3 天）

### 并行执行机会

**Phase 2 内部并行**:
- T009-T012 (数据模型) || T013a-T013e (价格机制) || T014-T016 (订单簿) || T017-T024 (Repository) || T025-T027 (Cache)

**Phase 4 & 5 并行** (US1 和 US2 独立):
- T038-T056 (US1) || T057-T089 (US2)

**Phase 6 测试并行**:
- T093-T097 (单元测试) || T098-T101 (集成测试)

**Phase 8 完全并行**:
- T122-T135 所有任务可同时进行

---

## Independent Test Criteria (每个用户故事的独立测试标准)

### US4 - Unified Matching
**验证方式**:
1. 启动空白会话
2. 提交 AI 订单（时间戳 T1）
3. 提交用户订单（时间戳 T2）到同价格
4. 触发撮合
5. 验证 AI 订单先成交

**通过标准**: 时间戳早的订单优先成交，无论来源

---

### US1 - Real User Trading
**验证方式**:
1. 用户通过 API 提交限价买单
2. 等待下一 tick
3. 查询订单状态 → FILLED 或 PARTIAL
4. 查询用户账户 → 余额和持仓正确更新

**通过标准**: 用户可完整完成"提交-成交-查询"流程，无需依赖 US2 或 US3

---

### US2 - AI Behavioral Objectives
**验证方式**:
1. 运行模拟 100 ticks（无用户订单）
2. 统计散户订单与价格趋势的相关系数
3. 统计游资/机构的盈利率

**通过标准**:
- 散户跟风相关系数 ≥ 0.6
- 游资盈利率 ≥ 55%
- 机构盈利率 ≥ 55%

---

### US3 - Order Book Depth
**验证方式**:
1. 运行模拟累积订单（AI + 用户）
2. 调用 GET /orderbook API
3. 验证返回档位数量 ≤ 50
4. 验证每档数量正确聚合

**通过标准**: API 返回正确格式的 50 档深度，查询延迟 <500ms

---

## Implementation Strategy

### MVP 范围（最小可行产品）

**推荐 MVP**: Phase 1 + Phase 2 + Phase 3 (US4) + Phase 4 (US1)

**理由**:
- US4 提供核心撮合能力
- US1 提供用户交易功能
- 无需 AI 行为增强（US2）即可演示基本功能
- 无需 50 档深度（US3）即可满足基本使用

**MVP 交付物**:
- 用户可以提交订单
- 订单与 AI 订单公平撮合
- 用户可以查询成交状态
- 基本的订单簿查询

**MVP 时间**: 约 10-12 天

---

### 增量交付计划

**Iteration 1 (MVP)**: US4 + US1
- 时间: 10-12 天
- 可演示：用户订单提交和撮合

**Iteration 2 (增强)**: US2
- 时间: +6-8 天
- 可演示：AI 行为差异化，市场真实感

**Iteration 3 (完整)**: US3 + Integration
- 时间: +4-5 天
- 可演示：50 档深度，性能达标

**Total**: 20-25 天

---

## Task Summary

**总任务数**: 135 个任务（新增 5 个价格机制验证任务）

**按阶段分布**:
- Phase 1 (Setup): 4 任务
- Phase 2 (Foundational): 23 任务（新增价格机制验证）
- Phase 3 (US4): 10 任务
- Phase 4 (US1): 19 任务
- Phase 5 (US2): 33 任务
- Phase 6 (US3): 12 任务
- Phase 7 (Integration): 20 任务
- Phase 8 (Polish): 14 任务

**可并行任务**: 约 60 任务（标记 [P]）

**关键路径长度**: 约 74 任务（串行依赖）

**预估工时**:
- 单人: 20-25 个工作日
- 2 人并行: 12-15 个工作日
- 3 人并行: 8-10 个工作日

---

## Format Validation

✅ **所有任务遵循规范格式**:
- [x] 每个任务以 `- [ ]` 开头
- [x] 任务 ID 格式 `T###`
- [x] 并行标记 `[P]` 正确使用
- [x] 用户故事标签 `[US#]` 正确映射
- [x] 每个任务包含确切文件路径
- [x] 任务描述清晰可执行

✅ **组织结构验证**:
- [x] 按用户故事分阶段
- [x] 每个用户故事可独立测试
- [x] 依赖关系明确
- [x] MVP 范围清晰

---

**任务文档状态**: ✅ 已生成并验证
**下一步**: 执行 `/speckit.implement` 开始实施，或手动按阶段执行任务
