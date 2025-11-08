# 仿真 Redis 键设计

## 命名约定
- 统一前缀 `sim:{session_code}`，确保多房间隔离。
- 真实玩家使用 `player:{player_id}`，匿名智能体使用 `agent:{participant_id}`。

| 功能 | Key 示例 | 类型 | TTL | 备注 |
| ---- | -------- | ---- | --- | ---- |
| 会话状态 | `sim:{session}/status` | string | 永久 | running / paused / closed |
| 当前 tick | `sim:{session}:tick` | string | 永久 | 与数据库 current_tick 对齐 |
| 排行榜 | `sim:{session}:leaderboard` | zset | 永久 | score 作为分数，成员为 participant_id |
| 玩家快照 | `sim:{session}:player:{participant}` | hash | 30s | 缓存现金、仓位、得分，后端刷新 |
| orderbook 缓存 | `sim:{session}:ob:{side}` | list | 5s | 仅做前端加速，可回源数据库 |
| 实时事件流 | `sim:{session}:stream` | stream | 24h | 推送 tick/order/trade 事件给推送层 |
| 回放索引 | `sim:{session}:replay` | hash | 永久 | 指向对象存储路径/校验信息 |
| 速率限制 | `sim:ratelimit:{player}` | string | 60s | 控制玩家下单频率 |
| AI 教练队列 | `sim:coach:queue` | list | 近期 1000 条 | 存放 AI 教练 JSON 日志（见 `doc/sim/coach_schema.md`），消费方 `BRPOP` 后持久化 |

## 失效策略
- ZSET 排行榜定期（每 5 分钟）与数据库同步，支持 `ZREMRANGEBYRANK` 清理过期成员。
- Stream 控制 `maxlen ~ 1000`，避免无限增长。
- Hash 缓存使用 `EXPIRE` + 被动刷新，Redis 缓存失效时回源数据库。

## 安全与运维
- 所有键受 `requirepass` 保护，客户端需使用 `SIM_REDIS_URL` 内的凭证。
- 建议对 leaderboard / stream 设置 `notify-keyspace-events`，便于监控。
- 通过 `SCARD`、`XLEN`、`INFO keyspace` 定期审计缓存尺寸，防止爆内存。
