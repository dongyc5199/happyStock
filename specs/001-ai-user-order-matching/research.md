# Research & Technical Decisions

**Feature**: AI-Enhanced Trading Simulation with User Integration
**Date**: 2025-11-11
**Status**: Phase 0 Complete

## Overview

本文档记录了功能实施前的关键技术决策和研究结果，解决了实施计划中识别的 5 个核心技术问题。

---

## 决策 1: 订单簿数据结构扩展方案

### 研究目标
确定如何将 `backend/sim/engine.py` 中的订单簿从当前架构扩展到支持 50 档深度。

### 现状分析

通过代码审查（`engine.py:61-146`），现有 `OrderBook` 类使用以下结构：

```python
class OrderBook:
    bids: Dict[float, Deque[Order]]  # 价格 → 订单队列
    asks: Dict[float, Deque[Order]]
    bid_prices: List[float]           # 排序的价格列表（买方降序）
    ask_prices: List[float]           # 排序的价格列表（卖方升序）
```

**核心机制**:
- 使用 `bisect` 模块维护排序的价格列表
- 每个价格档位用 `Deque[Order]` 实现时间优先
- `pop_best()` 从最优价格档位取出订单

**现有性能**:
- 插入价格档位: O(log N + N) - bisect 查找 O(log N) + list.insert O(N)
- 获取最优价格: O(1) - 访问 price_levels[0]
- 添加订单到档位: O(1) - deque.append

### 问题识别

当前设计的**限制**:
1. **无深度限制** - 价格档位数量可以无限增长
2. **插入性能** - `list.insert()` 在 50 档规模下可接受，但不是最优解
3. **无聚合视图** - 没有提供档位聚合数量的快速查询

### 方案评估

#### 方案 A: 保持现有结构 + 添加深度限制（推荐）✅

**实现**:
```python
class OrderBook:
    def __init__(self, max_depth: int = 50):
        self.max_depth = max_depth
        # ... 现有字段

    def _add_to_book(self, order, book, price_levels, *, reverse):
        # 添加订单前检查深度
        if order.price not in book and len(price_levels) >= self.max_depth:
            # 移除最差价格档位
            worst_price = price_levels[-1]
            if self._is_price_better_than_worst(order.price, worst_price, reverse):
                self._remove_price(worst_price, book, price_levels)
            else:
                return  # 拒绝订单
        # ... 原有逻辑
```

**优点**:
- ✅ 最小改动，兼容性好
- ✅ 现有算法复杂度在 50 档规模下完全可接受
- ✅ 代码可读性高

**缺点**:
- ⚠️ `list.insert()` 在最坏情况下 O(50) 仍然不是最优

**性能测试**:
- 1,000 orders/sec 目标下，每个订单插入耗时 <50μs 是可接受的
- Python list 操作在此规模下经过 CPython 优化，性能充足

#### 方案 B: 使用 SortedList (sortedcontainers)

**实现**: 引入 `sortedcontainers.SortedList` 替代 `List[float]`

**优点**:
- ✅ 插入 O(log N)，理论上更优

**缺点**:
- ❌ 引入外部依赖（违反技术栈一致性原则）
- ❌ 在 50 档规模下收益微小（<50μs → <10μs）
- ❌ 增加团队学习成本

**结论**: 不采纳，性价比低

#### 方案 C: 使用 heapq (最小堆)

**实现**: 用 `heapq` 替代排序列表

**优点**:
- ✅ Python 标准库，无外部依赖
- ✅ 插入 O(log N)

**缺点**:
- ❌ 堆只保证根节点最优，无法高效支持"移除最差档位"
- ❌ 不支持有序遍历（获取 Level 2 数据需要额外排序）
- ❌ 代码复杂度显著增加

**结论**: 不采纳，不适合订单簿场景

### 最终决策

**选择方案 A: 保持现有结构 + 添加深度限制**

**理由**:
1. **充分性**: 在 50 档和 1,000 orders/sec 目标下，性能完全满足
2. **简单性**: 符合 CLAUDE.md 中的简单性原则（YAGNI）
3. **兼容性**: 最小化对现有代码的影响
4. **可测试性**: 逻辑清晰，易于单元测试

**实施细节**:
- 在 `OrderBook.__init__()` 添加 `max_depth` 参数（默认 50）
- 在 `_add_to_book()` 中添加深度检查逻辑
- 超出深度的订单根据价格优先原则拒绝或替换最差档位
- 添加 `get_depth_snapshot()` 方法返回聚合档位数据

**性能验证**:
- 编写 benchmark 测试 1,000 orders/sec 场景
- 目标：单订单处理 <1ms（包含撮合和数据库写入）

---

## 决策 2: AI 代理行为建模策略

### 研究目标
基于行为金融学设计规则策略，实现三类代理的差异化行为。

### 现有行为分析

#### 散户代理 (RetailSentimentAgent - retail.py)

**当前行为**:
- 基于情绪分数 (sentiment) 和价格漂移 (drift) 决定方向
- 阈值触发: `abs(impulse) < threshold` 时大概率不交易
- 跟风概率: `follow_chance = 0.35`（35% 概率无视阈值跟随）
- 订单类型: 市价单（MARKET）
- 订单量: 小额（base_quantity = 5.0，随机波动 0.5-1.6x）

**问题**:
- ⚠️ 跟风行为不够明显 - 仅 35% 概率，且无延迟模拟
- ⚠️ 未考虑"追涨杀跌"心理 - 应在趋势强化时加大订单量

#### 游资代理 (PropMomentumAgent - prop.py)

**当前行为**:
- 基于波动率 (volatility) 和趋势 (trend) 触发
- 动量追踪: `direction_score = sentiment * 0.35 + trend * 0.6`
- 突发交易: 每 60-160 tick 触发一次大额订单（3.5x multiplier）
- 订单量: 大额（base_quantity = 120.0）

**问题**:
- ⚠️ 盈利目标不明确 - 未实现"获利了结"逻辑
- ⚠️ 风险控制缺失 - 没有止损机制

#### 机构代理 (InstitutionalRebalanceAgent - institutional.py)

需要阅读完整代码以评估。

### 行为金融学原理应用

根据研究文献和真实市场观察：

1. **散户特征**:
   - **损失厌恶**: 亏损时倾向持有，盈利时急于落袋
   - **羊群效应**: 观察到大额成交后跟随（延迟 1-3 tick）
   - **过度交易**: 频繁小额交易
   - **追涨杀跌**: 趋势越强，参与度越高

2. **游资特征**:
   - **动量策略**: 识别短期趋势，快进快出
   - **盈利目标**: 一般 2-5% 获利了结
   - **止损纪律**: 严格止损 1-2%
   - **大单冲击**: 集中力量打板或砸盘

3. **机构特征**:
   - **均值回归**: 价格偏离合理值时介入
   - **大单拆分**: TWAP/VWAP 算法执行
   - **长期持有**: 不频繁交易
   - **流动性敏感**: 避免过大冲击成本

### 增强方案

#### 散户增强参数

```python
class RetailSentimentAgent:
    # 新增参数
    herd_delay_ticks: int = 2           # 跟风延迟 2 tick
    herd_trigger_volume: float = 500.0  # 观察到大额交易后触发
    panic_multiplier: float = 2.5       # 恐慌时订单量倍数
    follow_chance: float = 0.70         # 提升至 70%
```

**行为逻辑**:
1. 监听上一 tick 的成交量，若 >500 则提升跟风概率至 0.9
2. 趋势强化时（drift > 3%），订单量 * panic_multiplier
3. 延迟 2 tick 后才对趋势做出反应

#### 游资增强参数

```python
class PropMomentumAgent:
    # 新增参数
    profit_target: float = 0.03        # 3% 获利目标
    stop_loss: float = 0.015           # 1.5% 止损
    position_tracking: Dict[int, float] = {}  # session_id → avg_price
```

**行为逻辑**:
1. 追踪每个 session 的平均持仓成本
2. 当前价格 > avg_price * (1 + profit_target) → 平仓卖出
3. 当前价格 < avg_price * (1 - stop_loss) → 止损卖出
4. 无持仓时按现有动量逻辑开仓

#### 机构增强参数

```python
class InstitutionalRebalanceAgent:
    # 新增参数
    mean_reversion_window: int = 100    # 均值回归周期
    rebalance_threshold: float = 0.02   # 2% 偏离触发
    max_order_size: float = 200.0       # 单笔最大订单
    split_orders: int = 5               # 大单拆分为 5 笔
```

**行为逻辑**:
1. 计算过去 100 tick 的价格均值
2. 当前价格偏离 >2% 时触发反向订单（低买高卖）
3. 大单拆分为多笔，每笔间隔 1-2 tick

### 最终决策

**采用增强行为模型**，参数如上设计。

**可配置性保证**:
- 所有参数通过 `AgentPoolConfig` 暴露
- 支持运行时通过 API 调整（`PUT /api/sim/sessions/{session_id}/agents/{agent_id}/config`）
- 提供"保守/激进"预设配置

**验证方法**:
- 测试散户跟风相关系数 ≥0.6（成功标准 SC-004）
- 测试游资盈利率 ≥55%（成功标准 SC-003）
- 观察 100 tick 后的行为分化统计指标

---

## 决策 3: 用户订单与 AI 订单集成模式

### 研究目标
设计用户订单进入撮合引擎的流程，确保公平性。

### 架构分析

现有 `SimulationService.execute_tick()` 流程（`services.py:887 行`）:

```
1. Tick 开始
2. 遍历 AgentPool，调用 agent.generate_orders()
3. 收集所有 AI 生成的订单
4. 调用 MatchingEngine.submit_order() 逐一撮合
5. 生成 MarketSnapshot
6. 持久化订单和成交记录
7. 更新缓存和排行榜
```

**问题**: 用户订单在哪个环节注入？

### 方案评估

#### 方案 A: Tick 开始时合并用户订单队列（推荐）✅

**流程**:
```python
async def execute_tick(self, session_id: int, tick: int):
    # 1. 从 Redis 读取用户挂起订单队列
    user_orders = await self._cache.pop_pending_user_orders(session_id)

    # 2. 生成 AI 订单
    ai_orders = await self._generate_ai_orders(session_id, tick)

    # 3. 合并并按时间戳排序
    all_orders = sorted(user_orders + ai_orders, key=lambda o: o.timestamp)

    # 4. 统一提交撮合
    for order in all_orders:
        trades = self._engine.submit_order(order)
        # ... 记录成交
```

**用户订单提交 API**:
```python
@router.post("/sessions/{session_id}/orders")
async def submit_user_order(session_id: int, order_req: OrderRequest):
    # 验证订单（资金、价格范围）
    validated_order = validate_order(order_req, user_balance)

    # 加上精确时间戳（纳秒级）
    validated_order.timestamp = time.time_ns()

    # 推入 Redis 队列
    await cache.push_pending_user_order(session_id, validated_order)

    # 返回 202 Accepted + order_id
    return {"status": "accepted", "order_id": validated_order.order_id}
```

**优点**:
- ✅ 时间戳统一由服务端生成，保证公平性
- ✅ 用户订单在下一个 tick 处理，与 AI 订单同等对待
- ✅ 异步处理，API 响应快

**缺点**:
- ⚠️ 市价单需等待下一 tick（最多延迟 tick_interval_ms）

#### 方案 B: 实时撮合用户订单

**流程**: 用户订单到达后立即调用 `MatchingEngine.submit_order()`

**优点**:
- ✅ 市价单立即成交

**缺点**:
- ❌ 破坏 tick 驱动架构
- ❌ 并发控制复杂（需要锁整个撮合引擎）
- ❌ 用户可能比 AI 更快获得信息（不公平）

**结论**: 不采纳

### 最终决策

**选择方案 A: Tick 开始时合并用户订单队列**

**公平性保证**:
1. **时间戳精度**: 使用 `time.time_ns()` 生成纳秒级时间戳
2. **排序规则**: 所有订单（AI + 用户）按时间戳严格排序后进入撮合
3. **信息对称**: AI 和用户在同一 tick 使用相同的市场数据（上一 tick 的 MarketSnapshot）

**实施细节**:
- 在 `types.py` 中的 `Order` dataclass 添加 `timestamp: int` 字段
- 在 `cache.py` 添加 `push_pending_user_order()` 和 `pop_pending_user_orders()` 方法
- 在 `services.py` 的 `execute_tick()` 开头合并队列

**限制说明**:
- 用户订单延迟最多 1 个 tick_interval（默认 1000ms）
- 通过前端明确告知用户：模拟交易非实时，订单在下一 tick 处理

---

## 决策 4: 性能优化策略

### 研究目标
应对 1,000 orders/sec 的性能目标，参考 `doc/sim/pending_tasks.md` 中的已知瓶颈。

### 已知瓶颈分析

从 `pending_tasks.md` 提取：

1. **Participants 注册延迟** (200-300ms 尾延)
   - 原因：每个 agent 单独调用 `create_or_update_participant()`
   - 影响：首次 tick 启动慢

2. **update_tick 慢查询** (偶发 600ms)
   - 原因：可能是锁竞争或索引缺失
   - 影响：高并发时性能抖动

3. **FeatureService 策略未文档化**
   - 原因：不清楚哪些特征走本地计算，哪些走外部服务
   - 影响：可能产生不必要的网络调用

### 优化方案

#### 优化 1: 批量 Participants 注册（高优先级）✅

**实施**:
```python
# repositories.py 添加批量方法
async def batch_create_participants(
    self,
    session_id: int,
    participants: List[ParticipantState]
) -> None:
    # 使用 PostgreSQL UNNEST 批量 upsert
    await self.conn.executemany("""
        INSERT INTO sim_participants (session_id, participant_id, ...)
        VALUES ($1, $2, ...)
        ON CONFLICT (session_id, participant_id) DO UPDATE ...
    """, [(session_id, p.participant_id, ...) for p in participants])
```

**预期收益**: 200-300ms → <50ms

#### 优化 2: update_tick 性能分析（中优先级）

**实施步骤**:
1. 添加 `EXPLAIN ANALYZE` 日志到 `update_tick()` 查询
2. 检查 `(session_id, current_tick)` 索引是否存在
3. 评估是否需要异步队列缓冲（如果单查询优化不足）

**如果需要异步化**:
```python
# 使用 asyncio.Queue 缓冲 tick 更新
self._tick_update_queue = asyncio.Queue()
asyncio.create_task(self._tick_update_worker())
```

**预期收益**: 600ms → <100ms

#### 优化 3: FeatureService 文档化（低优先级）

**实施**: 在 `doc/sim/feature_service_strategy.md` 中明确：

```markdown
## 本地计算特征
- best_bid, best_ask: 从 OrderBook 获取
- volume, imbalance: 从 trades 聚合

## 外部服务特征（如有）
- macro_sentiment: 调用情绪 API
- news_impact: 调用新闻 API
```

**预期收益**: 避免不必要的服务调用，降低延迟

### 性能测试计划

**Benchmark 场景**:
- 100 AI agents + 50 concurrent users
- 1000 orders/tick (AI 生成 800 + 用户提交 200)
- 持续 1000 ticks (约 16 分钟，假设 tick_interval=1000ms)

**监控指标**:
- P50/P95/P99 订单处理延迟
- Tick 执行时间分布
- 数据库连接池使用率
- Redis 命令延迟

**通过标准**:
- P95 订单延迟 <1s（SC-001）
- Tick 执行时间 P95 <800ms（留 200ms buffer）
- 无 OOM 或连接池耗尽错误

### 最终决策

**优先实施优化 1 和 2**，优化 3 作为文档任务在实施阶段完成。

**渐进式优化策略**:
1. 先实现功能，确保正确性
2. 运行 benchmark 获得 baseline
3. 根据 profiling 结果针对性优化
4. 重复 2-3 直到满足性能目标

---

## 决策 5: 用户订单 API 设计

### 研究目标
设计用户订单提交的 RESTful API 端点。

### API 端点设计

#### POST /api/sim/sessions/{session_id}/orders - 提交订单

**请求体**:
```json
{
  "side": "BUY",           // or "SELL"
  "order_type": "LIMIT",   // or "MARKET"
  "quantity": 100.0,
  "price": 50.25,          // optional, required for LIMIT
  "participant_id": "user-12345"  // 从 JWT token 提取
}
```

**响应** (202 Accepted):
```json
{
  "status": "accepted",
  "order_id": "ord-abc123",
  "message": "Order queued for next tick",
  "estimated_execution_tick": 1234
}
```

**验证规则**:
- 资金充足性检查（查询 sim_accounts 表）
- 限价单价格在合理范围内（last_price ± 10%）
- 数量 >0 且符合最小交易单位

**错误响应** (400 Bad Request):
```json
{
  "error": "insufficient_balance",
  "required": 5025.0,
  "available": 3000.0
}
```

#### GET /api/sim/sessions/{session_id}/orders/{order_id} - 查询订单状态

**响应** (200 OK):
```json
{
  "order_id": "ord-abc123",
  "status": "FILLED",      // NEW/PARTIAL/FILLED/CANCELLED
  "side": "BUY",
  "quantity": 100.0,
  "filled_quantity": 100.0,
  "avg_price": 50.30,
  "created_at": "2025-11-11T10:30:00Z",
  "filled_at": "2025-11-11T10:30:02Z"
}
```

#### DELETE /api/sim/sessions/{session_id}/orders/{order_id} - 撤单

**响应** (200 OK):
```json
{
  "status": "cancelled",
  "order_id": "ord-abc123",
  "cancelled_quantity": 50.0  // 未成交部分
}
```

**限制**: 只能撤销 NEW 或 PARTIAL 状态的订单

#### GET /api/sim/sessions/{session_id}/orderbook - 查询订单簿

**响应** (200 OK):
```json
{
  "bids": [
    {"price": 50.25, "quantity": 500.0, "orders": 12},
    {"price": 50.20, "quantity": 300.0, "orders": 8},
    // ... 最多 50 档
  ],
  "asks": [
    {"price": 50.30, "quantity": 400.0, "orders": 10},
    {"price": 50.35, "quantity": 600.0, "orders": 15},
    // ... 最多 50 档
  ],
  "last_update_tick": 1234
}
```

### WebSocket 推送设计

用户订单成交后通过 WebSocket 主动推送：

**消息格式**:
```json
{
  "type": "order_filled",
  "order_id": "ord-abc123",
  "filled_quantity": 100.0,
  "avg_price": 50.30,
  "timestamp": "2025-11-11T10:30:02Z"
}
```

**订阅方式**:
```javascript
ws.send(JSON.stringify({
  "action": "subscribe",
  "channel": "user_orders",
  "session_id": 123,
  "user_id": "user-12345"
}));
```

### 最终决策

**采用上述 RESTful API + WebSocket 推送的组合设计**。

**OpenAPI 3.0 规范**将在 Phase 1 生成到 `contracts/user-orders.yaml`。

**安全性考虑**:
- 所有端点需要 JWT 认证
- 订单只能由所属用户查询/撤销
- 防止恶意刷单：限流 10 orders/second/user

---

## 研究总结

### 关键决策汇总

| 决策项 | 选择方案 | 关键理由 |
|--------|---------|---------|
| 订单簿数据结构 | 保持现有 List + 深度限制 | 性能充足，简单性优先 |
| AI 行为建模 | 增强参数化规则策略 | 可配置，可验证，无ML依赖 |
| 订单集成模式 | Tick 开始时合并队列 | 保证公平性，架构一致 |
| 性能优化 | 批量注册 + 查询分析 | 针对已知瓶颈，渐进优化 |
| API 设计 | 异步REST + WebSocket推送 | 响应快，用户体验好 |

### 待解决问题

1. **机构代理详细设计** - 需要阅读完整 `institutional.py` 后补充
2. **数据库迁移脚本** - 需要在 Phase 1 设计数据模型后编写
3. **WebSocket 订阅管理** - 需要确认现有 WebSocket 架构支持用户级订阅

### 下一步行动

✅ Phase 0 研究完成
➡️ 进入 Phase 1: 生成数据模型和 API 合约文档

---

**批准**: 待项目负责人审查
**版本**: 1.0
**最后更新**: 2025-11-11
