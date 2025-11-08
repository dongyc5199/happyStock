# AI 教练日志 Schema

仿真服务会在每个 tick 结束后，对活跃参与者输出统一格式的教练日志：

1. **数据库落地**：`agent_log` hypertable，字段 `event_type`=`category`，`detail` 存储完整 JSON。
2. **Redis 队列**：`sim:coach:queue`，使用 `LPUSH` 推入 JSON 字符串，长度保留最近 1000 条，供消费方实时拉取。

## JSON 字段说明

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `session_id` | number | 仿真会话 ID（Timescale 主键） |
| `session_code` | string | 会话编码，同 Redis 命名空间 |
| `tick` | number | 当前 tick |
| `participant_id` | string | 行为主体（玩家/智能体）标识 |
| `participant_type` | string | `player` / `agent`，基于 ID 前缀推断 |
| `category` | string | `positioning` / `risk` 等事件分类 |
| `severity` | string | `info` / `warning` |
| `headline` | string | 概要标题（中文） |
| `summary` | string | 详细描述 |
| `metrics` | object | 结构化指标，包含：`buy_volume`、`sell_volume`、`net_volume`、`avg_trade_price`、`score_delta`、`trade_count`、`sentiment`、`order_book_imbalance`、`last_price` |
| `recommendations` | string[] | 建议列表，至少 1 条 |
| `created_at` | string | ISO8601 时间戳 |

## 样例

```json
{
  "session_id": 12,
  "session_code": "demo-room",
  "tick": 42,
  "participant_id": "player-7",
  "participant_type": "player",
  "category": "risk",
  "severity": "warning",
  "headline": "净买入 8.00 手",
  "summary": "玩家「player-7」在 tick 42 净买入 8.00 手，成交均价 101.23。 盘口不平衡度 +0.45，情绪指数 +0.62。",
  "metrics": {
    "buy_volume": 8.0,
    "sell_volume": 0.0,
    "net_volume": 8.0,
    "avg_trade_price": 101.23,
    "score_delta": 8.0,
    "trade_count": 2,
    "sentiment": 0.62,
    "order_book_imbalance": 0.45,
    "last_price": 101.3
  },
  "recommendations": [
    "市场情绪偏热，留意追高后的回落风险。",
    "盘口极度不均衡，建议缩小委托尺寸或拆分执行。"
  ],
  "created_at": "2025-11-04T10:15:23.120000+00:00"
}
```

## 消费方式

- **Redis**：轮询 `sim:coach:queue`，消费后可自行 `RPOP` 或 `BRPOP`。建议通过 `created_at` + `participant_id` 去重。
- **数据库**：需要历史记录或联动 BI 时，直接查询 `agent_log`，`detail->>'headline'` 等字段可按 JSON 提取。
