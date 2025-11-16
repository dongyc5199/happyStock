# 动态参与者系统设计文档

## 概述

实现一个动态的AI参与者管理系统，能够根据市场走势自动增加新的参与者（散户、游资、机构），模拟真实市场的资金流入效应。

## 核心特性

### 1. 参与者数量配置

| 类型 | 初始数量 | 最大数量 | 占比目标 |
|------|---------|---------|---------|
| 散户 | 5 | 50 | 70-80% |
| 游资 | 3 | 10 | 15-20% |
| 机构 | 2 | 5 | 5-10% |
| 做市商 | 1 | 2 | 固定 |

**散户占比最大**：保持 70-80% 的散户比例，符合真实市场特征

### 2. 入场触发条件

#### 散户入场（最容易）
- **价格上涨** > 2%（10 tick内）：基础概率 0.3 → 0.5
- **正面情绪** > 0.5：额外 +0.3 概率
- **成交量激增** > 120%：额外 +0.2 概率
- **高波动率** > 3%：额外 +0.15 概率（散户追涨杀跌）

**总概率范围**：0.3 - 0.95

#### 游资入场（较谨慎）
- **价格上涨** > 3%：基础概率 0.15 → 0.3
- **成交量激增** > 150%：额外 +0.3 概率（游资看重流动性）
- **高波动率** > 5%：额外 +0.2 概率
- **正面情绪** > 0.3：额外 +0.1 概率

**总概率范围**：0.15 - 0.7

#### 机构入场（最谨慎）
- **价格回调** -2% to 0%：基础概率 0.05 → 0.15（机构逢低吸纳）
- **成交量稳定放大** > 130%：额外 +0.2 概率
- **低波动率** < 2%：额外 +0.1 概率（机构偏好稳定）
- **情绪中性** -0.2 to 0.2：额外 +0.05 概率

**总概率范围**：0.05 - 0.4

### 3. 评估时机

- **评估间隔**：每 10 个 tick 评估一次
- **批量入场**：每次评估可能有 0-3 个新参与者入场
- **渐进式增长**：避免突然涌入大量参与者

### 4. 新参与者配置

#### 散户（动态生成）
```python
RetailSentimentAgent(
    code=f"retail-dynamic-{N}",
    base_quantity=random.uniform(20.0, 50.0),
    herd_behavior_strength=random.uniform(0.4, 0.95),  # 随机羊群强度
    momentum_sensitivity=random.uniform(0.5, 0.9),
    risk_tolerance=random.uniform(0.5, 0.8),
    initial_cash=random.uniform(30000, 80000),  # 3-8万资金
)
```

#### 游资（动态生成）
```python
PropMomentumAgent(
    code=f"prop-dynamic-{N}",
    base_quantity=random.uniform(60.0, 150.0),
    profit_target=random.uniform(0.025, 0.06),  # 2.5%-6%
    stop_loss=random.uniform(0.01, 0.025),
    risk_tolerance=random.uniform(0.6, 0.95),
    initial_cash=random.uniform(100000, 200000),  # 10-20万资金
)
```

#### 机构（动态生成）
```python
InstitutionalRebalanceAgent(
    code=f"inst-dynamic-{N}",
    base_quantity=random.uniform(150.0, 300.0),
    mean_reversion_window=random.randint(50, 150),
    rebalance_threshold=random.uniform(0.015, 0.03),
    split_orders=True,
    initial_cash=random.uniform(300000, 600000),  # 30-60万资金
)
```

## 实现架构

### 核心组件

#### 1. DynamicParticipantManager
```
职责：
- 监控市场状况
- 计算入场概率
- 创建新参与者
- 维护参与者计数
```

#### 2. 与 SimulationService 集成

```python
class SimulationService:
    def __init__(self, ...):
        # 新增
        self._dynamic_participants = DynamicParticipantManager(
            retail_max=50,
            prop_max=10,
            institutional_max=5,
            evaluation_interval=10,
        )

    async def process_tick(self, ...):
        # 现有逻辑
        ...

        # 新增：更新市场数据
        if snapshot.last_price and total_volume:
            self._dynamic_participants.update_market_data(
                session_id,
                price=snapshot.last_price,
                volume=total_volume,
            )

        # 新增：评估是否添加新参与者
        await self._evaluate_new_participants(
            session_id,
            session_code,
            tick,
            snapshot,
        )
```

#### 3. 新参与者入场逻辑

```python
async def _evaluate_new_participants(
    self,
    session_id: int,
    session_code: str,
    tick: int,
    snapshot: MarketSnapshot,
):
    """评估并添加新参与者"""
    if self._agents is None:
        return

    # 计算市场状况
    condition = MarketCondition(
        price_change_pct=...,
        volume_surge=...,
        sentiment=snapshot.emotion or 0.0,
        volatility=snapshot.features.get("volatility", 0.0),
        tick=tick,
    )

    # 评估各类型参与者
    for agent_type in ["retail", "prop", "institutional"]:
        if self._dynamic_participants.should_add_participant(
            session_id,
            agent_type,
            condition,
        ):
            # 创建并注册新参与者
            new_agent = self._dynamic_participants.create_new_participant(
                session_id,
                agent_type,
                sequence_number=self._dynamic_participants.get_counts(session_id)[agent_type] + 1,
            )

            await self._agents.register(
                session_id=session_id,
                agent=new_agent,
                weight=1.0,
                pool_code=agent_type,
            )

            self._dynamic_participants.increment_count(session_id, agent_type)

            logger.info(
                f"New {agent_type} participant joined session {session_code}: {new_agent.code}"
            )
```

## 数据流

```
Tick N
  ↓
收集市场数据（价格、成交量）
  ↓
更新 DynamicParticipantManager 历史数据
  ↓
每 10 tick 评估一次
  ↓
计算市场状况（价格变化、成交量激增、情绪、波动率）
  ↓
计算各类型入场概率
  ↓
散户：概率 0.3-0.95（最高）
游资：概率 0.15-0.7（中等）
机构：概率 0.05-0.4（最低）
  ↓
随机判断是否入场
  ↓
创建新参与者（随机配置）
  ↓
注册到 AgentRegistry
  ↓
增加计数（维护占比）
  ↓
新参与者在下一个 tick 开始交易
```

## 示例场景

### 场景 1：价格快速上涨

```
Tick 0-10: 价格从 100 涨到 103 (+3%)
成交量正常

→ 散户入场概率：0.3 + 0.24(价格) + 0.1(情绪) = 0.64
→ 可能新增 2-3 个散户

Tick 10-20: 价格继续涨到 107 (+4%)
成交量激增 2倍

→ 散户入场概率：0.3 + 0.32 + 0.3(情绪) + 0.2(成交量) = 0.82
→ 游资入场概率：0.15 + 0.24 + 0.3(成交量) + 0.1(情绪) = 0.59
→ 可能新增 3-4 个散户 + 1-2 个游资

最终：散户 5→12 (75%), 游资 3→5 (31%), 机构 2 (12.5%)
```

### 场景 2：价格回调整理

```
Tick 0-10: 价格从 105 跌到 102 (-2.9%)
成交量平稳

→ 机构入场概率：0.05 + 0.15(逢低) + 0.1(低波动) = 0.3
→ 可能新增 0-1 个机构

Tick 10-20: 价格横盘 102
成交量稳定放大 1.3倍

→ 机构入场概率：0.05 + 0.2(成交量稳定) + 0.1(低波动) = 0.35
→ 可能新增 0-1 个机构

最终：机构 2→3-4
```

## API 监控

### 查询参与者统计
```bash
GET /api/sim/sessions/{session_id}/participants/stats

Response:
{
  "total_count": 28,
  "retail_count": 21,
  "prop_count": 5,
  "institutional_count": 2,
  "distribution": {
    "retail": 0.75,
    "prop": 0.179,
    "institutional": 0.071
  },
  "max_limits": {
    "retail": 50,
    "prop": 10,
    "institutional": 5
  }
}
```

### 查询入场历史
```bash
GET /api/sim/sessions/{session_id}/participants/history

Response:
{
  "entries": [
    {
      "tick": 50,
      "agent_code": "retail-dynamic-6",
      "agent_type": "retail",
      "trigger_reason": "price_surge_3.2%",
      "market_condition": {
        "price_change_pct": 0.032,
        "volume_surge": 1.8,
        "sentiment": 0.6
      }
    },
    ...
  ]
}
```

## 配置参数

### 环境变量
```bash
# 动态参与者系统
SIM_DYNAMIC_PARTICIPANTS_ENABLED=true
SIM_RETAIL_MAX=50
SIM_PROP_MAX=10
SIM_INSTITUTIONAL_MAX=5
SIM_EVALUATION_INTERVAL=10  # 每 N tick 评估一次
```

### 代码配置
在 `SimulationService` 初始化时：
```python
DynamicParticipantManager(
    retail_max=50,
    prop_max=10,
    institutional_max=5,
    evaluation_interval=10,
)
```

## 优势

1. ✅ **真实性**：模拟真实市场的资金流入效应
2. ✅ **散户占比**：自动维护 70-80% 散户比例
3. ✅ **动态性**：根据市场走势自动调整参与者数量
4. ✅ **多样性**：每个新参与者都有随机配置
5. ✅ **可控性**：设置最大数量限制，避免失控
6. ✅ **可观测性**：提供 API 监控参与者变化

## 后续优化

1. **参与者退出机制**：亏损或长期不活跃的参与者离场
2. **情绪传染**：新入场的散户受现有散户影响
3. **资金加权**：后期入场的参与者资金更少（追高风险）
4. **智能调节**：根据总市值动态调整参与者上限
5. **事件触发**：特殊事件（如涨停）触发大量散户涌入

## 总结

动态参与者系统让模拟市场更加真实和生动：
- **市场火热时**：散户和游资蜂拥入场
- **市场冷清时**：只有少数机构逢低吸纳
- **散户占比**：始终保持在 70-80%
- **资金管理**：每个参与者都有资金限制

整个系统自动运行，无需人工干预，为模拟交易提供更丰富的对手盘和更真实的市场体验。
