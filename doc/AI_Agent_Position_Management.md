# AI Agent 资金和仓位管理设计

## 需求

1. **禁止做空**：AI 代理只能做多，必须先买入才能卖出
2. **资金限制**：每个 AI 代理有固定的初始资金，不能无限下单
3. **仓位限制**：卖出数量不能超过持有数量

## 实现方案

### 1. AgentStrategy 基类扩展

在 `backend/sim/agents/base.py` 中：

```python
class AgentStrategy(ABC):
    def __init__(
        self,
        code: str,
        *,
        weight: float = 1.0,
        initial_cash: float = 100000.0,  # 默认 10 万初始资金
    ):
        self.code = code
        self.weight = weight
        self.initial_cash = initial_cash

        # 每个会话独立追踪
        self._cash: Dict[int, float] = {}  # session_id -> 可用资金
        self._position: Dict[int, float] = {}  # session_id -> 持仓数量
```

### 2. 核心方法

#### 资金和持仓查询
```python
def get_cash(self, session_id: int) -> float:
    """获取可用资金"""

def get_position(self, session_id: int) -> float:
    """获取持仓数量"""
```

#### 资金和持仓更新
```python
def update_cash(self, session_id: int, amount: float) -> None:
    """更新资金（正数=增加，负数=减少）"""

def update_position(self, session_id: int, quantity: float) -> None:
    """更新持仓（正数=买入，负数=卖出）"""
```

#### 约束检查
```python
def can_buy(self, session_id: int, quantity: float, price: float) -> bool:
    """检查是否有足够资金买入"""
    required_cash = quantity * price
    return self.get_cash(session_id) >= required_cash

def can_sell(self, session_id: int, quantity: float) -> bool:
    """检查是否有足够持仓卖出（禁止做空）"""
    return self.get_position(session_id) >= quantity
```

### 3. 订单生成时的约束检查

代理在生成订单时必须：

1. **买入订单**：检查 `can_buy()`
   - 如果资金不足，减少订单数量或跳过

2. **卖出订单**：检查 `can_sell()`
   - 如果持仓不足，最多只能卖出持有数量
   - 如果没有持仓，不能生成卖单

### 4. 订单执行后的更新

当订单成交后，需要更新资金和持仓：

- **买入成交**：
  ```python
  agent.update_cash(session_id, -quantity * price)  # 扣除资金
  agent.update_position(session_id, quantity)       # 增加持仓
  ```

- **卖出成交**：
  ```python
  agent.update_cash(session_id, quantity * price)  # 增加资金
  agent.update_position(session_id, -quantity)     # 减少持仓
  ```

## 默认初始资金配置

| 代理类型 | 代理代码 | 初始资金 | 说明 |
|---------|---------|---------|------|
| 游资（激进） | prop-aggressive | 150,000 | 高风险高回报 |
| 游资（平衡） | prop-balanced | 120,000 | 平衡策略 |
| 游资（保守） | prop-conservative | 100,000 | 保守稳健 |
| 机构（大型） | inst-large | 500,000 | 大资金量 |
| 机构（中型） | inst-medium | 300,000 | 中等资金量 |
| 散户（跟风） | retail-follower-* | 50,000 | 小资金量 |
| 散户（适度） | retail-moderate-* | 60,000 | 小资金量 |
| 散户（独立） | retail-independent | 80,000 | 小资金量 |
| 做市商 | mm-primary | 1,000,000 | 需要大量资金提供流动性 |

**总计约 300 万初始资金**（11 个代理）

## 实现步骤

### Phase 1: 基础设施 ✅
- [x] 扩展 AgentStrategy 基类添加资金/持仓追踪
- [x] 添加约束检查方法

### Phase 2: 代理订单生成修改（进行中）
- [ ] PropMomentumAgent - 检查资金/持仓约束
- [ ] InstitutionalRebalanceAgent - 检查资金/持仓约束
- [ ] RetailSentimentAgent - 检查资金/持仓约束
- [ ] MarketMakerAgent - 检查资金/持仓约束

### Phase 3: 订单执行后更新
- [ ] 在 AgentRegistry 或 SimulationService 中监听成交事件
- [ ] 成交后自动更新对应代理的资金和持仓
- [ ] 持久化资金和持仓数据到数据库

### Phase 4: 监控和调试
- [ ] API 端点：查询代理资金和持仓
- [ ] 日志：记录资金和持仓变化
- [ ] 测试：验证约束正确执行

## 示例：PropMomentumAgent 修改

```python
async def generate_orders(
    self,
    session_id: int,
    session_code: str,
    tick: int,
    context: AgentContext,
) -> List[GeneratedOrder]:
    # ... existing logic ...

    # 确定买卖方向
    side = "BUY" if direction_score >= 0 else "SELL"
    quantity = self._calculate_quantity(...)  # 计算理想数量

    # 应用资金和持仓约束
    if side == "BUY":
        # 检查资金约束
        if context.last_price is None:
            return []

        max_affordable = self.get_cash(session_id) / context.last_price
        quantity = min(quantity, max_affordable)

        if quantity < 1.0:
            return []  # 资金不足，跳过

    elif side == "SELL":
        # 检查持仓约束（禁止做空）
        current_position = self.get_position(session_id)
        quantity = min(quantity, current_position)

        if quantity < 1.0:
            return []  # 没有持仓，跳过

    # 生成订单
    return [GeneratedOrder(..., quantity=quantity)]
```

## 注意事项

1. **市价单的资金预估**：
   - 市价单没有确定价格
   - 使用 `context.last_price` 或 `context.best_ask/best_bid` 估算
   - 可能实际成交价不同，需要容错

2. **部分成交**：
   - 订单可能只部分成交
   - 需要根据实际成交量更新资金/持仓
   - 不是根据订单量

3. **并发问题**：
   - 同一 tick 多个订单可能同时生成
   - 需要确保资金/持仓检查的一致性

4. **做市商特殊处理**：
   - 做市商需要同时挂买单和卖单
   - 需要更大的初始资金
   - 可能需要特殊的资金管理逻辑

## 测试场景

1. **资金耗尽测试**：
   - 代理连续买入直到资金耗尽
   - 验证不再生成买单

2. **持仓耗尽测试**：
   - 代理连续卖出直到持仓清空
   - 验证不再生成卖单

3. **禁止做空测试**：
   - 代理没有持仓时尝试卖出
   - 验证不生成卖单或订单被拒绝

4. **资金恢复测试**：
   - 代理买入后卖出
   - 验证资金正确恢复

5. **多会话隔离测试**：
   - 同一代理在多个会话中
   - 验证资金/持仓独立追踪
