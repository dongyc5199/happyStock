# Agent 行为参数持久化修复

## 问题描述

用户发现了一个关键的数据流断层问题：

1. **Agent注册时**有完整的行为参数（profit_target、risk_tolerance、herd_behavior_strength等）
2. **生成订单时**GeneratedOrder没有携带这些参数
3. **转换为payload时**（services.py:277-285）只转换基本字段，丢失了行为参数
4. **存库时**（repositories.py:225-315）需要这些字段来填充session_participant表
5. **结果**：数据库中behavior_category等字段为NULL，API返回空值

## 修复方案

### 1. ✅ 扩展GeneratedOrder数据类

**文件**：`backend/sim/agents/base.py`

**修改**：添加行为参数字段到GeneratedOrder

```python
@dataclass(slots=True)
class GeneratedOrder:
    order_id: str
    participant_id: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None
    pool_code: str | None = None
    # Behavior parameters for persistence
    participant_code: str | None = None
    participant_type: str = "agent"
    behavior_category: str | None = None
    profit_target: float | None = None
    stop_loss: float | None = None
    herd_behavior_strength: float | None = None
    momentum_sensitivity: float | None = None
    risk_tolerance: float | None = None
```

### 2. ✅ 更新services.py传递行为参数

**文件**：`backend/sim/services.py`

**修改**：在payload中包含所有行为参数

```python
payload = {
    "order_id": generated.order_id,
    "participant_id": generated.participant_id,
    "participant_code": generated.participant_code or generated.participant_id,
    "participant_type": generated.participant_type,
    "side": generated.side,
    "type": generated.order_type,
    "quantity": generated.quantity,
    "price": generated.price,
    "timestamp": timestamp_ns,
    # Behavior parameters for persistence
    "behavior_category": generated.behavior_category,
    "profit_target": generated.profit_target,
    "stop_loss": generated.stop_loss,
    "herd_behavior_strength": generated.herd_behavior_strength,
    "momentum_sensitivity": generated.momentum_sensitivity,
    "risk_tolerance": generated.risk_tolerance,
}
```

### 3. ✅ 更新RetailSentimentAgent

**文件**：`backend/sim/agents/retail.py`

**修改**：生成订单时填充所有行为参数

```python
order = GeneratedOrder(
    order_id=f"{self.code}-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
    participant_id=f"{self.code}-agent",
    participant_code=self.code,
    participant_type="agent",
    side=side,
    order_type="MARKET",
    quantity=quantity,
    price=None,
    behavior_category="retail",
    profit_target=self.profit_target,
    stop_loss=self.stop_loss,
    herd_behavior_strength=self.herd_behavior_strength,
    momentum_sensitivity=self.momentum_sensitivity,
    risk_tolerance=self.risk_tolerance,
)
```

### 4. ✅ 更新PropMomentumAgent

**文件**：`backend/sim/agents/prop.py`

**修改**：
1. 添加辅助方法 `_create_order()` 来统一创建订单并填充行为参数
2. 更新所有GeneratedOrder创建（止盈订单、止损订单、主订单、支持订单、burst订单）使用辅助方法

```python
def _create_order(
    self,
    order_id: str,
    participant_id: str,
    side: str,
    quantity: float,
    price: float | None = None,
) -> GeneratedOrder:
    """Helper to create order with behavior parameters."""
    return GeneratedOrder(
        order_id=order_id,
        participant_id=participant_id,
        participant_code=self.code,
        participant_type="agent",
        side=side,
        order_type="MARKET" if price is None else "LIMIT",
        quantity=quantity,
        price=price,
        behavior_category="prop",
        profit_target=self.profit_target,
        stop_loss=self.stop_loss,
        herd_behavior_strength=self.herd_behavior_strength,
        momentum_sensitivity=self.momentum_sensitivity,
        risk_tolerance=self.risk_tolerance,
    )
```

### 5. ⏳ 待完成：InstitutionalRebalanceAgent

**文件**：`backend/sim/agents/institutional.py`

**需要修改**：4处GeneratedOrder创建
- TWAP分批订单（line 130）
- Mean reversion订单（line 142）
- 常规rebalance订单（line 165）
- Block trade订单（line 182）

**建议实现**：
```python
def _create_order(
    self,
    order_id: str,
    participant_id: str,
    side: str,
    quantity: float,
    price: float | None = None,
) -> GeneratedOrder:
    """Helper to create order with behavior parameters."""
    return GeneratedOrder(
        order_id=order_id,
        participant_id=participant_id,
        participant_code=self.code,
        participant_type="agent",
        side=side,
        order_type="MARKET" if price is None else "LIMIT",
        quantity=quantity,
        price=price,
        behavior_category="institutional",
        profit_target=self.profit_target,
        stop_loss=self.stop_loss,
        herd_behavior_strength=self.herd_behavior_strength,
        momentum_sensitivity=self.momentum_sensitivity,
        risk_tolerance=self.risk_tolerance,
    )
```

### 6. ⏳ 待完成：MarketMakerAgent

**文件**：`backend/sim/agents/market_maker.py`

**需要修改**：2处GeneratedOrder创建（bid和ask订单，line 67-82）

**建议实现**：
```python
def _create_order(
    self,
    order_id: str,
    participant_id: str,
    side: str,
    quantity: float,
    price: float,
) -> GeneratedOrder:
    """Helper to create order with behavior parameters."""
    return GeneratedOrder(
        order_id=order_id,
        participant_id=participant_id,
        participant_code=self.code,
        participant_type="agent",
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
        behavior_category="market_maker",
        # Market makers don't have these parameters, set to None
        profit_target=None,
        stop_loss=None,
        herd_behavior_strength=None,
        momentum_sensitivity=None,
        risk_tolerance=None,
    )
```

## 数据流验证

### 修复前的数据流（断层）

```
Agent注册
  ├─ profit_target: 0.03
  ├─ risk_tolerance: 0.7
  └─ behavior_category: "prop"
      ↓
生成订单 (GeneratedOrder)
  ├─ order_id: "prop-1-100-abc123"
  ├─ side: "BUY"
  ├─ quantity: 120.0
  └─ ❌ 行为参数丢失！
      ↓
转换payload (services.py:277-285)
  ├─ order_id: "prop-1-100-abc123"
  ├─ side: "BUY"
  ├─ quantity: 120.0
  └─ ❌ behavior_category、profit_target等字段缺失
      ↓
存库 (repositories.py:225-315)
  ├─ session_participant表插入/更新
  ├─ behavior_category: NULL ❌
  ├─ profit_target: NULL ❌
  └─ risk_tolerance: NULL ❌
      ↓
API返回 (GET /agents, /pools)
  └─ ❌ 返回空值，与文档不符
```

### 修复后的数据流（完整）

```
Agent注册
  ├─ profit_target: 0.03
  ├─ risk_tolerance: 0.7
  └─ behavior_category: "prop"
      ↓
生成订单 (GeneratedOrder)
  ├─ order_id: "prop-1-100-abc123"
  ├─ side: "BUY"
  ├─ quantity: 120.0
  ├─ ✅ participant_code: "prop-aggressive-1"
  ├─ ✅ participant_type: "agent"
  ├─ ✅ behavior_category: "prop"
  ├─ ✅ profit_target: 0.03
  ├─ ✅ stop_loss: 0.015
  ├─ ✅ herd_behavior_strength: 0.4
  ├─ ✅ momentum_sensitivity: 0.85
  └─ ✅ risk_tolerance: 0.7
      ↓
转换payload (services.py:277-294)
  ├─ order_id: "prop-1-100-abc123"
  ├─ participant_code: "prop-aggressive-1"
  ├─ participant_type: "agent"
  ├─ side: "BUY"
  ├─ quantity: 120.0
  ├─ ✅ behavior_category: "prop"
  ├─ ✅ profit_target: 0.03
  ├─ ✅ stop_loss: 0.015
  ├─ ✅ herd_behavior_strength: 0.4
  ├─ ✅ momentum_sensitivity: 0.85
  └─ ✅ risk_tolerance: 0.7
      ↓
存库 (repositories.py:225-315)
  ├─ session_participant表插入/更新
  ├─ ✅ participant_code: "prop-aggressive-1"
  ├─ ✅ behavior_category: "prop"
  ├─ ✅ profit_target: 0.03
  ├─ ✅ stop_loss: 0.015
  ├─ ✅ herd_behavior_strength: 0.4
  ├─ ✅ momentum_sensitivity: 0.85
  └─ ✅ risk_tolerance: 0.7
      ↓
API返回 (GET /agents, /pools)
  └─ ✅ 返回完整行为参数，符合文档
```

## 预期API响应

修复后，API应该返回完整的行为参数：

### GET /api/sim/sessions/{id}/agents

```json
{
  "agents": [
    {
      "code": "prop-aggressive-1",
      "participant_type": "agent",
      "behavior_category": "prop",
      "profit_target": 0.03,
      "stop_loss": 0.015,
      "herd_behavior_strength": 0.4,
      "momentum_sensitivity": 0.85,
      "risk_tolerance": 0.7,
      "pool_code": "prop"
    },
    {
      "code": "retail-follower-1",
      "participant_type": "agent",
      "behavior_category": "retail",
      "profit_target": 0.30,
      "stop_loss": -0.20,
      "herd_behavior_strength": 0.9,
      "momentum_sensitivity": 0.8,
      "risk_tolerance": 0.7,
      "pool_code": "retail"
    }
  ]
}
```

### GET /api/sim/sessions/{id}/pools

```json
{
  "pools": [
    {
      "pool_code": "prop",
      "participant_count": 10,
      "avg_profit_target": 0.03,
      "avg_risk_tolerance": 0.68
    },
    {
      "pool_code": "retail",
      "participant_count": 100,
      "avg_profit_target": 0.30,
      "avg_risk_tolerance": 0.60
    }
  ]
}
```

## 修复状态

| 组件 | 状态 | 说明 |
|-----|------|------|
| GeneratedOrder数据类 | ✅ 完成 | 添加8个行为参数字段 |
| services.py payload | ✅ 完成 | 传递所有行为参数到payload |
| RetailSentimentAgent | ✅ 完成 | 填充所有行为参数 |
| PropMomentumAgent | ✅ 完成 | 使用辅助方法填充参数（5处订单生成） |
| InstitutionalRebalanceAgent | ⏳ 待完成 | 需要添加辅助方法（4处订单生成） |
| MarketMakerAgent | ⏳ 待完成 | 需要添加辅助方法（2处订单生成） |

## 测试验证

修复完成后，应该验证：

1. **数据库验证**：
```sql
SELECT
    participant_code,
    behavior_category,
    profit_target,
    stop_loss,
    herd_behavior_strength,
    momentum_sensitivity,
    risk_tolerance
FROM session_participant
WHERE session_id = 1
AND behavior_category IS NOT NULL;
```

应该看到100+行有完整的行为参数。

2. **API验证**：
```bash
# 查看所有agents
curl http://localhost:8000/api/sim/sessions/1/agents | python -m json.tool

# 查看pools
curl http://localhost:8000/api/sim/sessions/1/pools | python -m json.tool
```

应该看到behavior_category、profit_target等字段有值，不再是NULL。

## 下一步

1. ✅ 已完成基础设施和Retail、Prop修复
2. ⏳ 完成Institutional和MarketMaker修复
3. ⏳ 重启服务测试
4. ⏳ 验证数据库和API响应
5. ⏳ 确认与文档示例一致

## 总结

这个修复解决了关键的数据流断层问题，确保：
- Agent的行为参数在订单生成时被携带
- 参数正确传递到payload
- 数据库正确持久化这些参数
- API能够返回完整的agent配置信息

这对于监控、分析和调试agent行为至关重要。
