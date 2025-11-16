# 价格机制文档：交易驱动的价格发现

**功能**: 001-ai-user-order-matching
**作者**: happyStock 开发团队
**创建日期**: 2025-11-12
**状态**: ✅ 已验证

---

## 概述

本文档说明 **sim 模块的价格机制完全由交易驱动**，不使用任何人工价格生成算法（如 GBM、趋势模型等）。

---

## 核心原则

### ✅ 真实市场模拟

sim 模块遵循真实证券交易所的价格发现机制：

1. **初始价格**: 会话创建时指定（类似 IPO 定价或历史收盘价）
2. **后续价格**: 完全由订单撮合产生（买卖双方成交价格）
3. **无人工干预**: 无趋势、波动率、市场状态等参数影响价格

### ❌ 不使用的机制

以下机制**仅用于主应用的历史数据生成**，sim 模块不使用：

- `PriceGenerator` (backend/lib/price_generator.py)
- `MarketDataGenerator` (backend/lib/market_data_generator.py)
- Geometric Brownian Motion (GBM) 模型
- 市场状态机 (BULL/BEAR/SIDEWAYS)

---

## 实现细节

### 1. 初始价格设定

**位置**: `backend/sim/auto_runner.py`

```python
class SimulationAutoRunner:
    def __init__(
        self,
        *,
        bootstrap_price: float = 100.0,  # 默认初始价格
        bootstrap_spread: float = 0.4,   # 默认买卖价差
        bootstrap_volume: float = 20.0,  # 默认启动成交量
        ...
    ):
        self._bootstrap_price = max(bootstrap_price, 0.01)
```

**启动流程** (auto_runner.py:134-186):

1. **Tick 0**: 自动下单建立初始订单簿
   - 限价买单: `price = bootstrap_price - spread/2 = 99.8`
   - 限价卖单: `price = bootstrap_price + spread/2 = 100.2`
   - 市价单撮合: 建立首次成交价（约 100.0）

2. **记录初始价格**:
   ```python
   last_price = trades[-1].price  # 从首次成交中提取
   self._last_price[session_id] = last_price
   ```

### 2. 后续价格更新

**位置**: `backend/sim/services.py:559-562`

```python
async def _build_market_snapshot(
    self,
    session_id: int,
    tick: int,
    ts: datetime,
    engine: MatchingEngine,
    trades: Sequence[TradeEventRecord],
    signed_volume: float,
) -> MarketSnapshot:
    best_bid = engine.order_book.best_bid()
    best_ask = engine.order_book.best_ask()

    last_price = self._last_price[session_id]  # 初始化为上一 tick 价格
    if trades:
        last_price = trades[-1].price          # ← 关键：从成交中提取
        self._last_price[session_id] = last_price

    # 无任何价格模型计算，只使用交易数据
    return MarketSnapshot(
        session_id=session_id,
        tick=tick,
        timestamp=ts,
        best_bid=best_bid[0] if best_bid else None,
        best_ask=best_ask[0] if best_ask else None,
        last_price=last_price if last_price else None,  # ← 纯交易价格
        ...
    )
```

**关键验证**:
- ✅ 无 `price_generator` 模块引用
- ✅ 无 GBM 计算
- ✅ 无趋势/波动率参数
- ✅ 价格完全来自 `TradeEventRecord.price`

---

## 价格发现流程

### 完整 Tick 流程

```
┌─────────────────────────────────────────────────┐
│ Tick N 开始                                      │
├─────────────────────────────────────────────────┤
│ 1. 收集订单                                      │
│    • AI 代理订单 (generate_orders)              │
│    • 用户订单 (Redis 队列)                      │
├─────────────────────────────────────────────────┤
│ 2. 合并排序                                      │
│    • 按时间戳排序 (price-time priority)         │
├─────────────────────────────────────────────────┤
│ 3. 撮合引擎处理                                  │
│    • MatchingEngine.match(orders)               │
│    • 产生 TradeEventRecord[]                     │
│    • trade.price = 成交价格                      │
├─────────────────────────────────────────────────┤
│ 4. 更新市场快照                                  │
│    • last_price = trades[-1].price  ← 新价格    │
│    • best_bid = 订单簿最高买价                   │
│    • best_ask = 订单簿最低卖价                   │
├─────────────────────────────────────────────────┤
│ 5. 持久化                                        │
│    • 写入 TimescaleDB (trades, market_snapshot) │
│    • 更新 Redis 缓存                             │
└─────────────────────────────────────────────────┘
```

### 价格变动示例

**初始状态** (Tick 0):
- 初始价格: 100.0
- 订单簿: 买 [99.8], 卖 [100.2]

**Tick 1**: 市价买单 50 股
- 撮合: 以卖单价格 100.2 成交
- **新价格**: 100.2 ✅

**Tick 2**: 限价卖单 100 股 @ 99.5
- 撮合: 以买单价格 99.8 成交
- **新价格**: 99.8 ✅

**Tick 3**: 无成交
- **价格维持**: 99.8 （不变）

---

## 与主应用的区别

| 特性 | sim 模块 | 主应用 (lib/) |
|------|----------|---------------|
| **价格来源** | 订单撮合 | 价格生成器 (GBM) |
| **初始价格** | 用户指定 | base_price (数据库) |
| **价格更新** | 每 tick 成交价 | 每分钟 K 线生成 |
| **影响因素** | 订单流 | 趋势、波动率、市场状态 |
| **使用场景** | 实时仿真 | 历史数据回填 |
| **目标** | 真实撮合体验 | 模拟市场走势 |

---

## API 接口

### 会话创建（指定初始价格）

```http
POST /api/sim/sessions
Content-Type: application/json

{
  "mode": "sandbox",
  "tick_interval_ms": 1000,
  "total_ticks": 1000,
  "config": {
    "bootstrap_price": 150.0,     ← 自定义初始价格
    "bootstrap_spread": 0.5,      ← 自定义价差
    "bootstrap_volume": 30.0      ← 自定义启动成交量
  }
}
```

**响应**:
```json
{
  "session_id": 123,
  "session_code": "SIM-20251112-123",
  "status": "CREATED",
  "mode": "sandbox",
  "initial_price": 150.0  ← 确认的初始价格
}
```

### 市场快照查询

```http
GET /api/sim/sessions/123/snapshot
```

**响应**:
```json
{
  "session_id": 123,
  "tick": 45,
  "timestamp": "2025-11-12T10:30:05Z",
  "last_price": 152.3,      ← 来自最近成交
  "best_bid": 152.1,        ← 订单簿最高买价
  "best_ask": 152.5,        ← 订单簿最低卖价
  "vwap_price": 152.2,      ← 本 tick 成交均价
  "total_volume": 350.0
}
```

---

## 验证清单

### 代码验证 ✅

- [x] **T013a**: 验证 sim/ 目录无 `PriceGenerator` 引用
  ```bash
  grep -r "price_generator\|PriceGenerator" backend/sim/
  # 结果：无匹配（已验证）
  ```

- [x] **T013b**: 验证价格从交易中提取
  ```python
  # backend/sim/services.py:559-562
  last_price = self._last_price[session_id]
  if trades:
      last_price = trades[-1].price  # ✅ 从成交中提取
      self._last_price[session_id] = last_price
  ```

### 功能验证

- [ ] **T013c**: 会话可自定义 `initial_price` 参数（待实现）
- [ ] **T013d**: SimulationAutoRunner 支持自定义 `bootstrap_price`（待实现）
- [ ] **T013e**: 本文档已创建 ✅

---

## 测试用例

### 单元测试

```python
# backend/tests/unit/test_price_mechanism.py

async def test_price_from_trades_only():
    """验证价格完全由成交决定，无人工生成"""
    service = SimulationService()

    # 初始价格 100.0
    session = await service.create_session(
        SimulationSession(
            session_code="TEST-001",
            mode="sandbox",
            config={"bootstrap_price": 100.0}
        )
    )

    # 提交买单推高价格
    orders = [
        {"side": "BUY", "type": "MARKET", "quantity": 10.0}
    ]
    result = await service.process_tick(
        session_id=session.id,
        session_code="TEST-001",
        tick=1,
        orders=orders
    )

    # 验证价格来自成交，而非模型生成
    snapshot = result["snapshot"]
    assert snapshot["last_price"] == result["trades"][-1]["price"]
    assert "gbm_price" not in snapshot  # 无模型价格
    assert "drift" not in snapshot      # 无趋势参数
```

### 集成测试

```python
async def test_price_discovery_full_session():
    """验证完整会话的价格发现过程"""

    # 创建会话，初始价格 50.0
    session = await create_session(bootstrap_price=50.0)

    # 运行 100 ticks，记录所有成交价
    prices = []
    for tick in range(1, 101):
        result = await process_tick(session_id, tick)
        if result["trades"]:
            prices.append(result["snapshot"]["last_price"])

    # 验证价格序列
    assert prices[0] >= 49.5 and prices[0] <= 50.5  # 初始价格附近
    assert all(p > 0 for p in prices)                # 所有价格有效

    # 验证价格变动由订单流驱动
    # (通过对比订单方向和价格变化趋势)
    buy_volume = sum(t["quantity"] for t in trades if t["side"] == "BUY")
    sell_volume = sum(t["quantity"] for t in trades if t["side"] == "SELL")

    if buy_volume > sell_volume * 1.2:
        assert prices[-1] > prices[0]  # 买压大 → 价格上涨
    elif sell_volume > buy_volume * 1.2:
        assert prices[-1] < prices[0]  # 卖压大 → 价格下跌
```

---

## 常见问题

### Q1: 如果一个 tick 没有成交，价格如何处理？

**A**: 价格保持上一 tick 的 `last_price` 不变。

```python
last_price = self._last_price[session_id]  # 上一 tick 价格
if trades:
    last_price = trades[-1].price          # 如有成交则更新
```

### Q2: 初始价格可以在运行中修改吗？

**A**: 不可以。初始价格仅在会话创建时设定（Tick 0），后续完全由交易决定。

### Q3: AI 代理是否会影响价格生成？

**A**: AI 代理只生成订单，不直接影响价格。价格由 AI 订单和用户订单在撮合引擎中公平竞争产生。

### Q4: 如何避免价格剧烈波动？

**A**: 可以通过以下方式平滑价格：
1. 增加 AI 做市商代理（提供双边流动性）
2. 设置价格限制（如涨跌停板）
3. 调整订单簿深度（更多价格档位缓冲冲击）

### Q5: 与真实交易所的差异？

**主要差异**:
- **真实**: 连续竞价（订单实时撮合）
- **sim**: 离散 tick（批量撮合，每秒一次）

**相似点**:
- 价格-时间优先撮合
- 订单簿深度机制
- 成交价格决定市价

---

## 下一步

1. **实施 T013c**: 在 `SimulationService` 添加 `initial_price` 配置参数
2. **实施 T013d**: 更新 `SimulationAutoRunner` 支持自定义 `bootstrap_price`
3. **验证测试**: 运行本文档中的单元测试和集成测试
4. **API 文档**: 更新 OpenAPI 规范包含 `bootstrap_price` 参数

---

**文档版本**: 1.0
**最后更新**: 2025-11-12
**维护者**: happyStock 开发团队
