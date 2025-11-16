# Data Model: AI-Enhanced Trading Simulation

**Feature**: 001-ai-user-order-matching
**Date**: 2025-11-11
**Status**: Phase 1 Design

## Overview

本文档定义 AI 增强交易模拟功能所需的数据实体及其关系。基于现有 sim 模块的数据模型进行扩展，而非重新设计。

---

## 实体定义

### 1. UserOrder (新增实体)

**描述**: 用户提交的交易订单，与 AI 代理订单结构一致但来源不同。

**字段**:

| 字段名 | 类型 | 必填 | 描述 | 约束 |
|--------|------|------|------|------|
| `order_id` | String(UUID) | ✅ | 订单唯一标识 | PK, 格式: `user-{user_id}-{timestamp}-{random}` |
| `session_id` | Integer | ✅ | 所属模拟会话 | FK → `sim_sessions.id` |
| `user_id` | Integer | ✅ | 提交用户ID | FK → `users.id` |
| `participant_id` | String | ✅ | 撮合引擎中的参与者ID | 格式: `user-{user_id}` |
| `side` | Enum | ✅ | 买卖方向 | `BUY` 或 `SELL` |
| `order_type` | Enum | ✅ | 订单类型 | `MARKET` 或 `LIMIT` |
| `quantity` | Decimal(18,6) | ✅ | 订单数量 | >0 |
| `price` | Decimal(18,4) | ⚠️ | 限价（限价单必填） | LIMIT 订单必须提供 |
| `timestamp` | BigInt | ✅ | 订单提交时间戳 | 纳秒精度 (int64) |
| `status` | Enum | ✅ | 订单状态 | `PENDING`/`NEW`/`PARTIAL`/`FILLED`/`CANCELLED` |
| `filled_quantity` | Decimal(18,6) | ✅ | 已成交数量 | 默认 0 |
| `avg_filled_price` | Decimal(18,4) | ❌ | 平均成交价 | 可为 NULL |
| `created_at` | Timestamp | ✅ | 记录创建时间 | 系统生成 |
| `updated_at` | Timestamp | ✅ | 最后更新时间 | 自动更新 |

**状态转换**:
```
PENDING → NEW → PARTIAL → FILLED
          ↓
      CANCELLED
```

- `PENDING`: 用户提交但未进入撮合（在 Redis 队列中）
- `NEW`: 已进入撮合引擎，等待匹配
- `PARTIAL`: 部分成交
- `FILLED`: 完全成交
- `CANCELLED`: 用户撤单

**数据库表** (PostgreSQL):
```sql
CREATE TABLE user_orders (
    order_id VARCHAR(64) PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sim_sessions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participant_id VARCHAR(64) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type VARCHAR(6) NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT')),
    quantity DECIMAL(18,6) NOT NULL CHECK (quantity > 0),
    price DECIMAL(18,4),
    timestamp BIGINT NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('PENDING', 'NEW', 'PARTIAL', 'FILLED', 'CANCELLED')),
    filled_quantity DECIMAL(18,6) NOT NULL DEFAULT 0,
    avg_filled_price DECIMAL(18,4),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_orders_session_user ON user_orders(session_id, user_id);
CREATE INDEX idx_user_orders_status ON user_orders(status) WHERE status IN ('PENDING', 'NEW', 'PARTIAL');
CREATE INDEX idx_user_orders_timestamp ON user_orders(timestamp);
```

**验证规则**:
- LIMIT 订单必须提供 `price`，且价格在合理范围内（`last_price * 0.9 ~ last_price * 1.1`）
- 用户账户余额充足：`user_balance >= quantity * price` (买单) 或 `user_inventory >= quantity` (卖单)
- `filled_quantity <= quantity`

**关系**:
- 属于 `SimulationSession` (多对一)
- 属于 `User` (多对一)
- 生成多个 `TradeExecution` (一对多)

---

### 2. AIAgentProfile (增强现有实体)

**描述**: AI 代理的配置和状态，现有实体需新增行为参数字段。

**新增字段** (扩展现有 `sim_participants` 表):

| 字段名 | 类型 | 必填 | 描述 | 默认值 |
|--------|------|------|------|--------|
| `behavior_category` | Enum | ✅ | 行为类别 | `institutional`/`prop`/`retail`/`market_maker` |
| `profit_target` | Decimal(5,4) | ❌ | 盈利目标（百分比） | 0.03 (3%) |
| `stop_loss` | Decimal(5,4) | ❌ | 止损阈值（百分比） | 0.015 (1.5%) |
| `herd_behavior_strength` | Decimal(3,2) | ❌ | 羊群行为强度 (0-1) | 0.7 (散户) / 0.0 (机构) |
| `momentum_sensitivity` | Decimal(3,2) | ❌ | 动量敏感度 (0-1) | 0.6 (游资) / 0.2 (机构) |
| `risk_tolerance` | Decimal(3,2) | ❌ | 风险容忍度 (0-1) | 0.5 |
| `avg_position_cost` | Decimal(18,4) | ❌ | 平均持仓成本 | NULL (无持仓) |

**数据库迁移** (ALTER TABLE):
```sql
ALTER TABLE sim_participants
ADD COLUMN behavior_category VARCHAR(20) CHECK (behavior_category IN ('institutional', 'prop', 'retail', 'market_maker')),
ADD COLUMN profit_target DECIMAL(5,4) DEFAULT 0.03,
ADD COLUMN stop_loss DECIMAL(5,4) DEFAULT 0.015,
ADD COLUMN herd_behavior_strength DECIMAL(3,2) DEFAULT 0.0,
ADD COLUMN momentum_sensitivity DECIMAL(3,2) DEFAULT 0.5,
ADD COLUMN risk_tolerance DECIMAL(3,2) DEFAULT 0.5,
ADD COLUMN avg_position_cost DECIMAL(18,4);
```

**行为参数预设**:

| 类别 | profit_target | stop_loss | herd_strength | momentum_sens | risk_tolerance |
|------|---------------|-----------|---------------|---------------|----------------|
| retail | 0.05 | 0.02 | 0.70 | 0.30 | 0.60 |
| prop | 0.03 | 0.015 | 0.20 | 0.60 | 0.80 |
| institutional | 0.02 | 0.01 | 0.05 | 0.20 | 0.40 |
| market_maker | N/A | N/A | 0.00 | 0.00 | 0.30 |

---

### 3. OrderBook (增强现有逻辑)

**描述**: 订单簿深度快照，用于 API 查询和 WebSocket 推送。

**字段** (不需要持久化表，作为计算结果返回):

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `session_id` | Integer | 会话ID |
| `tick` | Integer | 快照所属 tick |
| `bids` | Array | 买方价格档位数组（最多 50 个） |
| `asks` | Array | 卖方价格档位数组（最多 50 个） |
| `timestamp` | Timestamp | 快照生成时间 |

**PriceLevel 结构** (嵌套对象):
```json
{
  "price": 50.25,
  "quantity": 500.0,
  "order_count": 12
}
```

**数据来源**: 实时从 `MatchingEngine.order_book` 计算，或从 Redis 缓存读取。

**Redis 缓存策略**:
- Key: `sim:orderbook:{session_id}`
- TTL: 5 秒（tick_interval 的 5 倍）
- 结构: JSON 字符串

**计算逻辑** (在 `engine.py` 中添加方法):
```python
def get_depth_snapshot(self, max_levels: int = 50) -> Dict:
    """返回订单簿深度快照（聚合档位）"""
    bids = []
    for i, price in enumerate(self.order_book.bid_prices[:max_levels]):
        qty = sum(order.remaining for order in self.order_book.bids[price] if order.is_active)
        count = sum(1 for order in self.order_book.bids[price] if order.is_active)
        bids.append({"price": price, "quantity": qty, "order_count": count})

    asks = []
    for i, price in enumerate(self.order_book.ask_prices[:max_levels]):
        qty = sum(order.remaining for order in self.order_book.asks[price] if order.is_active)
        count = sum(1 for order in self.order_book.asks[price] if order.is_active)
        asks.append({"price": price, "quantity": qty, "order_count": count})

    return {"bids": bids, "asks": asks}
```

---

### 4. TradeExecution (增强现有实体)

**描述**: 成交记录，现有实体需增加参与者类型字段以区分用户和 AI。

**新增字段** (扩展现有表):

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `buyer_type` | Enum | ✅ | 买方类型 | `user`/`ai_retail`/`ai_prop`/`ai_institutional`/`ai_market_maker` |
| `seller_type` | Enum | ✅ | 卖方类型 | 同上 |

**数据库迁移**:
```sql
ALTER TABLE sim_trades
ADD COLUMN buyer_type VARCHAR(20),
ADD COLUMN seller_type VARCHAR(20);

CREATE INDEX idx_sim_trades_participant_types ON sim_trades(buyer_type, seller_type);
```

**用途**: 用于统计和分析（例如：用户与哪种 AI 类型交易最多）。

---

### 5. UserSimulationAccount (关联现有实体)

**描述**: 用户在模拟交易中的账户，对应现有 `sim_accounts` 表。

**无需新增字段**，但需要确保：
- 每个用户加入 session 时自动创建账户（初始资金 100,000）
- `participant_id` 格式统一为 `user-{user_id}`

**关联逻辑** (在 `services.py` 中):
```python
async def join_session(self, session_id: int, user_id: int):
    """用户加入模拟会话，自动创建账户"""
    participant_id = f"user-{user_id}"
    await self._repo.create_or_update_participant(
        session_id=session_id,
        participant_id=participant_id,
        participant_type="user",
        initial_balance=100000.0
    )
```

---

## 实体关系图 (ER Diagram)

```
User (现有)
  |
  | 1:N
  v
UserOrder (新增) ────┐
  |                  │
  | N:1              │
  v                  │ 生成
SimulationSession    │
  |                  │
  | 1:N              │
  v                  │
AIAgentProfile       │ N:1
  |                  │
  | 生成             │
  v                  v
Order (统一) ──> TradeExecution (增强)
  |                  │
  | N:1              │ 更新
  v                  v
OrderBook (计算) → MarketSnapshot (现有)
```

**关键关系**:
1. **User → UserOrder**: 一个用户可以提交多个订单
2. **UserOrder + AI Order → TradeExecution**: 订单撮合产生成交
3. **TradeExecution → MarketSnapshot**: 成交更新市场快照
4. **OrderBook**: 从 Order 实时计算，不持久化

---

## 数据流向

### 用户订单提交流程
```
1. User 通过 API 提交 UserOrder
2. 验证 → 生成 timestamp → 推入 Redis 队列 (PENDING 状态)
3. 下一 Tick 开始，从 Redis pop 订单 → 状态改为 NEW
4. 合并 AI 订单 → 按 timestamp 排序 → 提交 MatchingEngine
5. 撮合产生 TradeExecution → 更新 UserOrder.filled_quantity
6. 完全成交 → 状态改为 FILLED，部分成交 → PARTIAL
7. 通过 WebSocket 推送成交通知给用户
```

### AI 代理订单生成流程
```
1. Tick 开始，遍历 AgentPool
2. 读取 AIAgentProfile 行为参数
3. 调用 agent.generate_orders(context)
4. AI 订单直接进入撮合（无需 Redis 队列）
5. 成交后更新 AIAgentProfile.avg_position_cost（用于盈利计算）
```

---

## 数据迁移计划

### 阶段 1: 新增 UserOrder 表
```sql
-- 文件: backend/sim/migrations/0004_user_orders.sql
CREATE TABLE user_orders (...);
CREATE INDEX ...;
```

### 阶段 2: 扩展 sim_participants 表
```sql
-- 文件: backend/sim/migrations/0005_agent_behavior_params.sql
ALTER TABLE sim_participants ADD COLUMN behavior_category ...;
ALTER TABLE sim_participants ADD COLUMN profit_target ...;
-- ... 其他字段
```

### 阶段 3: 扩展 sim_trades 表
```sql
-- 文件: backend/sim/migrations/0006_trade_participant_types.sql
ALTER TABLE sim_trades ADD COLUMN buyer_type ...;
ALTER TABLE sim_trades ADD COLUMN seller_type ...;
CREATE INDEX ...;
```

### 阶段 4: 数据回填（可选）
```sql
-- 将现有 AI 代理的 behavior_category 根据 participant_id 前缀推断
UPDATE sim_participants
SET behavior_category = CASE
    WHEN participant_id LIKE 'retail%' THEN 'retail'
    WHEN participant_id LIKE 'prop%' THEN 'prop'
    WHEN participant_id LIKE 'institutional%' THEN 'institutional'
    ELSE 'market_maker'
END
WHERE behavior_category IS NULL;
```

---

## 数据验证规则

### 订单验证 (UserOrder)
1. **资金检查** (买单):
   ```python
   required_amount = order.quantity * order.price
   if user_account.cash_balance < required_amount:
       raise InsufficientBalance(...)
   ```

2. **库存检查** (卖单):
   ```python
   if user_account.inventory < order.quantity:
       raise InsufficientInventory(...)
   ```

3. **价格合理性** (限价单):
   ```python
   if order.order_type == "LIMIT":
       if not (last_price * 0.9 <= order.price <= last_price * 1.1):
           raise PriceOutOfRange(...)
   ```

4. **数量最小单位**:
   ```python
   if order.quantity < 1.0 or order.quantity % 0.01 != 0:
       raise InvalidQuantity(...)
   ```

### 行为参数验证 (AIAgentProfile)
```python
assert 0 <= profit_target <= 1
assert 0 <= stop_loss <= 1
assert 0 <= herd_behavior_strength <= 1
assert 0 <= momentum_sensitivity <= 1
assert 0 <= risk_tolerance <= 1
```

---

## 性能优化考虑

### 1. Redis 缓存策略
- **热数据**: 当前 tick 的 OrderBook 快照（5 秒 TTL）
- **用户订单队列**: `sim:pending_orders:{session_id}`（List 结构）
- **账户余额缓存**: `sim:account:{session_id}:{user_id}`（30 秒 TTL）

### 2. 数据库索引优化
- `user_orders(session_id, user_id)` - 用户查询自己的订单
- `user_orders(timestamp)` - 按时间排序合并 AI 订单
- `user_orders(status)` - 过滤待处理订单（Partial Index）

### 3. 批量操作
- 批量插入 TradeExecution（每 tick 一次性插入所有成交）
- 批量更新 UserOrder.filled_quantity（使用 `executemany`）

---

## 数据完整性约束

### 1. 外键约束
- `user_orders.session_id` → `sim_sessions.id` (CASCADE DELETE)
- `user_orders.user_id` → `users.id` (CASCADE DELETE)

### 2. 检查约束
- `quantity > 0`
- `filled_quantity <= quantity`
- `status` 只能是预定义枚举值

### 3. 唯一性约束
- `order_id` 全局唯一（通过 UUID + 前缀保证）

---

## 版本控制

**模型版本**: 1.0
**兼容性**: 向后兼容现有 sim 模块数据模型
**迁移脚本**: `backend/sim/migrations/0004_*.sql` ~ `0006_*.sql`

---

**审批状态**: 待审查
**最后更新**: 2025-11-11
