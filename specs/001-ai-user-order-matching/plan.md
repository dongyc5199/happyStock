# Implementation Plan: AI-Enhanced Trading Simulation with User Integration

**Branch**: `001-ai-user-order-matching` | **Date**: 2025-11-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-user-order-matching/spec.md`

## Summary

增强 sim 模块，使其支持 AI 交易代理自主下单并与真实用户订单进行统一撮合，实现以下核心能力：
1. 三类差异化 AI 代理（机构、游资、散户）具备不同行为目标
2. 50 档订单簿深度
3. 公平的价格-时间优先撮合机制

技术方法：扩展现有 `backend/sim/` 模块，增强代理策略系统实现行为差异化，改造订单簿数据结构支持深度扩展，集成用户订单与 AI 订单的统一撮合流程。

## Technical Context

**Language/Version**: Python 3.13 (已确认，项目使用 Pipenv)
**Primary Dependencies**:
- FastAPI (异步 Web 框架)
- asyncpg (PostgreSQL 异步驱动)
- redis (缓存层)
- TimescaleDB (时间序列数据)
- Pipenv (依赖管理)

**Storage**:
- PostgreSQL/TimescaleDB (订单、成交、市场快照时间序列)
- Redis (实时缓存、排行榜、会话状态)

**Testing**: pytest (现有测试框架，已有 `backend/tests/unit/` 和 `backend/tests/integration/`)

**Target Platform**: Linux/Windows 服务器（开发环境 Windows MSYS，生产部署 Linux）

**Project Type**: Web 应用（FastAPI 后端 + Next.js 前端，本功能聚焦后端）

**Performance Goals**:
- 每秒处理 ≥1,000 笔订单（AI + 用户混合）
- 95% 市价单在 1 秒内成交
- 订单簿更新延迟 <500ms

**Constraints**:
- 兼容现有 sim 模块架构（tick 驱动、异步工作器）
- 保持与前端 WebSocket 推送的兼容性
- 避免引入机器学习依赖（使用规则策略）

**Scale/Scope**:
- 支持单个会话中 100+ AI 代理并发交易
- 50 档双边订单簿（100 个价格档位）
- 8 小时连续运行无性能下降

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**状态**: ⚠️ **项目宪章未定义** - 使用 CLAUDE.md 中的指导原则进行评估

基于 CLAUDE.md 的开发原则检查：

### 1. 架构一致性 ✅
- **原则**: 优先编辑现有文件，避免创建新文件
- **本功能**: 主要增强现有 `backend/sim/agents/` 和 `backend/sim/engine.py`
- **评估**: ✅ 通过 - 在现有模块基础上扩展

### 2. MVP 聚焦 ✅
- **原则**: 避免功能蔓延，专注核心特性
- **本功能**: 已明确 Out of Scope（机器学习、多资产、高级订单类型）
- **评估**: ✅ 通过 - 范围边界清晰

### 3. 数据驱动 ✅
- **原则**: 建立监控，基于指标决策
- **本功能**: 定义了 10 项可衡量成功标准（SC-001 ~ SC-010）
- **评估**: ✅ 通过 - 成功标准明确可测

### 4. 技术栈一致性 ✅
- **原则**: 使用已有技术栈（Python 3.13, FastAPI, PostgreSQL, Redis）
- **本功能**: 完全基于现有技术栈，无新增外部依赖
- **评估**: ✅ 通过 - 无新技术引入

### 5. 性能考量 ⚠️ 需关注
- **原则**: API 响应 <500ms，系统可用性 >99%
- **本功能**: 目标 1,000 orders/sec，可能触及现有性能瓶颈
- **评估**: ⚠️ 需验证 - 参考 `doc/sim/pending_tasks.md` 中的性能债务

### 总体评估
✅ **通过宪章检查** - 无重大违规，符合项目开发原则

**需要关注的点**：
- 性能优化需参考 pending_tasks.md 中的已知瓶颈（Participants 注册延迟、update_tick 慢查询）
- 50 档订单簿深度需验证 MatchingEngine 数据结构容量

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-user-order-matching/
├── plan.md              # 本文件（实施计划）
├── spec.md              # 功能规格（已完成）
├── research.md          # Phase 0 研究文档（待生成）
├── data-model.md        # Phase 1 数据模型（待生成）
├── quickstart.md        # Phase 1 快速入门（待生成）
├── contracts/           # Phase 1 API 合约（待生成）
│   ├── user-orders.yaml
│   └── agent-management.yaml
├── checklists/
│   └── requirements.md  # 规格质量检查清单（已完成）
└── tasks.md             # Phase 2 任务分解（通过 /speckit.tasks 生成）
```

### Source Code (repository root)

```text
# Web 应用结构（FastAPI 后端 + Next.js 前端）
backend/
├── sim/                           # 模拟交易核心模块（本功能重点）
│   ├── agents/                    # AI 代理策略系统 ⭐ 增强重点
│   │   ├── __init__.py
│   │   ├── base.py                # 代理基类（需扩展上下文）
│   │   ├── registry.py            # 代理注册表
│   │   ├── retail.py              # 散户代理 ⭐ 增强跟风行为
│   │   ├── prop.py                # 游资代理 ⭐ 增强盈利策略
│   │   ├── institutional.py       # 机构代理 ⭐ 增强盈利策略
│   │   ├── market_maker.py        # 做市商代理
│   │   └── depth_quoter.py        # 深度报价代理
│   ├── engine.py                  # 撮合引擎 ⭐ 需支持 50 档深度
│   ├── services.py                # 核心服务层 ⭐ 集成用户订单
│   ├── repositories.py            # 数据持久化层
│   ├── agent_pools.py             # 代理池管理
│   ├── feature_service.py         # 特征工程服务
│   ├── emotion_service.py         # 情绪分析服务
│   ├── worker.py                  # 异步工作器
│   ├── types.py                   # 数据类型定义
│   ├── schemas.py                 # Pydantic 模式
│   ├── cache.py                   # Redis 缓存
│   └── tasks/                     # 后台任务
├── routers/
│   └── simulate.py                # API 路由 ⭐ 新增用户订单端点
├── main.py                        # FastAPI 入口
└── tests/
    ├── unit/
    │   ├── test_sim_engine.py     # 撮合引擎测试 ⭐ 需扩展
    │   ├── test_sim_services.py   # 服务层测试
    │   └── test_sim_agents.py     # 代理策略测试 ⭐ 新增
    └── integration/
        └── test_sim_endpoints.py  # 端到端测试 ⭐ 需扩展

frontend/                          # Next.js 前端（本功能暂不涉及）
├── src/
│   ├── app/
│   ├── components/
│   └── services/
└── tests/

sql_scripts/                       # 数据库脚本
└── sim_migrations/                # sim 模块迁移脚本（可能需新增）
```

**结构决策**:
本功能采用**Web 应用结构（Option 2）**，因为项目包含独立的 backend 和 frontend 目录。

重点改动集中在 `backend/sim/` 模块：
1. **agents/** - 增强现有代理策略实现行为差异化
2. **engine.py** - 扩展订单簿支持 50 档深度
3. **services.py** - 集成用户订单提交和撮合逻辑
4. **routers/simulate.py** - 新增用户订单 API 端点

## Complexity Tracking

> **当前无需填写** - 宪章检查未发现需要特别证明的违规项

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Research & Technical Decisions

### Research Tasks

基于技术上下文中的未知项和依赖项，需要研究以下内容：

1. **订单簿数据结构扩展方案**
   - 研究目标：确定如何将 `engine.py` 中的订单簿从当前架构扩展到支持 50 档深度
   - 关键问题：现有 `MatchingEngine` 使用何种数据结构？是否需要重构？
   - 输出：数据结构选型建议（SortedList vs Heap vs RBTree）

2. **AI 代理行为建模最佳实践**
   - 研究目标：基于行为金融学设计规则策略，实现三类代理的差异化行为
   - 关键问题：
     - 散户羊群行为如何量化？（跟风延迟、订单量分布）
     - 机构/游资盈利策略如何建模？（均值回归、动量追踪）
   - 输出：行为策略参数设计文档

3. **用户订单与 AI 订单集成模式**
   - 研究目标：设计用户订单进入撮合引擎的流程，确保公平性
   - 关键问题：
     - 如何在 `SimulationService.execute_tick()` 中合并用户订单和 AI 订单？
     - 如何保证时间戳的准确性和唯一性？
   - 输出：订单处理流程图和伪代码

4. **性能优化策略**
   - 研究目标：应对 1,000 orders/sec 的性能目标，参考 pending_tasks.md 中的已知瓶颈
   - 关键问题：
     - 批量 upsert Participants 的实现方式
     - 订单簿更新是否需要异步化或缓冲队列
   - 输出：性能优化检查清单

5. **API 设计模式（用户订单提交）**
   - 研究目标：设计用户订单提交的 RESTful API 端点
   - 关键问题：
     - 同步返回 vs 异步处理（202 Accepted）
     - 订单验证规则（资金检查、限价合理性）
   - 输出：OpenAPI 3.0 规范草稿

### 研究文档结构

研究结果将输出到 `research.md`，包含以下决策：

- **决策 1**: 订单簿数据结构 → 选择 SortedList（性能 vs 复杂度权衡）
- **决策 2**: AI 行为参数 → 散户跟风系数 0.7，机构均值回归阈值 2%
- **决策 3**: 订单集成模式 → Tick 开始时合并用户队列和 AI 生成
- **决策 4**: 性能优化 → 优先实现批量 Participants 注册
- **决策 5**: API 模式 → 异步提交（202 + order_id），WebSocket 推送成交

*具体内容将在 Phase 0 执行时生成*

## Phase 1: Design Artifacts

### 数据模型扩展（data-model.md）

从功能规格中提取的关键实体：

1. **UserOrder (新增)**
   - 字段：order_id, user_id, session_id, side, order_type, quantity, price, timestamp
   - 关系：属于 SimulationSession，生成 TradeExecution
   - 验证规则：价格必须在涨跌停限制内，数量 >0

2. **AIAgentProfile (增强现有)**
   - 新增字段：behavior_category (institutional/prop/retail), profit_target, risk_tolerance
   - 策略参数：momentum_sensitivity, herd_behavior_strength

3. **OrderBook (增强现有)**
   - 扩展容量：max_depth_levels = 50
   - 聚合逻辑：price_level → aggregated_quantity

4. **TradeExecution (现有，无变更)**
   - 记录 participant_type (user/ai_agent_type)

### API 合约（contracts/）

将生成以下合约文件：

1. **user-orders.yaml** - 用户订单提交和查询
   ```
   POST /api/sim/sessions/{session_id}/orders
   GET  /api/sim/sessions/{session_id}/orders/{order_id}
   DELETE /api/sim/sessions/{session_id}/orders/{order_id}
   ```

2. **agent-management.yaml** - AI 代理配置管理
   ```
   GET /api/sim/sessions/{session_id}/agents
   PUT /api/sim/sessions/{session_id}/agents/{agent_id}/config
   ```

### 快速入门（quickstart.md）

包含：
1. 本地开发环境设置
2. 启动 sim 模块的步骤
3. 提交测试订单的 curl 示例
4. 查看订单簿的方法

## Phase 2: Task Breakdown

*此阶段由 `/speckit.tasks` 命令执行，不在本计划中生成*

任务将包括：
- 重构 MatchingEngine 支持 50 档
- 实现三类 AI 代理的行为策略
- 集成用户订单 API 端点
- 编写单元测试和集成测试
- 性能测试和优化
- 文档更新

## Implementation Notes

### 关键技术挑战

1. **订单簿性能** - 50 档深度可能导致查询和更新变慢，需要优化数据结构选择

2. **公平性保证** - 确保用户订单与 AI 订单的时间戳精度一致（纳秒级？）

3. **行为真实性** - AI 代理的行为参数需要经过调优才能达到"真实感"

4. **并发控制** - 多用户同时下单 + AI 代理生成订单，需要正确的锁机制

### 风险缓解策略

- **性能风险**: 先实现功能，后通过 profiling 定位瓶颈，参考 pending_tasks.md 的优化建议
- **行为调优风险**: 预留配置接口，允许运行时调整 AI 参数
- **测试复杂度**: 使用 pytest fixtures 构建可复用的测试场景（模拟用户 + AI 混合场景）

## Next Steps

1. ✅ Phase 0: 执行研究任务，生成 `research.md`
2. ✅ Phase 1: 基于研究结果生成 `data-model.md`, `contracts/`, `quickstart.md`
3. ⏭️ Phase 2: 执行 `/speckit.tasks` 生成任务分解（独立命令）
4. ⏭️ 实施: 执行 `/speckit.implement` 开始编码（独立命令）

**计划状态**: ✅ Phase 0 & Phase 1 已完成
**预计完成时间**: 2-3 周（基于 3,900 行现有代码基础上的增量开发）

---

## Phase 1 后宪章重新评估

*GATE: Re-check after Phase 1 design.*

**评估时间**: 2025-11-11 (Phase 1 完成后)
**评估状态**: ✅ **通过**

### 设计决策审查

#### 1. 架构一致性 ✅ 持续通过
- **决策**: 保持现有 `OrderBook` 数据结构，仅添加深度限制
- **理由**: 最小化侵入性，兼容现有代码
- **评估**: 符合"优先编辑现有文件"原则

#### 2. 复杂度控制 ✅ 通过
- **决策**: 拒绝引入 `sortedcontainers` 等外部依赖
- **理由**: 50 档规模下性能充足，避免不必要的复杂度
- **评估**: 符合 YAGNI 原则

#### 3. 数据模型设计 ✅ 通过
- **新增表**: `user_orders` (1个)
- **扩展字段**: `sim_participants` (7个), `sim_trades` (2个)
- **评估**: 数据模型扩展合理，避免重复设计

#### 4. API 设计 ✅ 通过
- **异步处理**: 用户订单提交返回 202 Accepted
- **WebSocket 推送**: 成交通知主动推送
- **评估**: 符合现代 Web API 最佳实践

#### 5. 性能目标可达性 ⚠️ 需验证
- **目标**: 1,000 orders/sec
- **当前状态**: 已识别两个优化点（批量注册、update_tick）
- **评估**: 需要在实施阶段通过 benchmark 验证

### 新增风险识别

1. **数据迁移风险** (低)
   - 3个新迁移脚本需要测试
   - 缓解：在测试环境先验证

2. **用户订单队列积压风险** (中)
   - 高并发时 Redis 队列可能积压
   - 缓解：添加队列长度监控和限流

3. **行为参数调优风险** (中)
   - AI 代理参数需要多次迭代才能达到真实感
   - 缓解：提供配置接口，支持A/B测试

### 总体结论

✅ **Phase 1 设计通过宪章检查**

所有设计决策符合项目开发原则，无需修正。已准备好进入 Phase 2 (任务分解) 和后续实施阶段。

---
