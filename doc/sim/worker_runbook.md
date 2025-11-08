## SimulationWorker 运维手册

### 1. 概述
`SimulationWorker` 负责消费 `/api/sim/step`、`/api/sim/player/order` 等异步请求。  
核心参数（默认值）：

| 参数 | 说明 | 默认 |
| ---- | ---- | ---- |
| `max_queue_size` | 每个 session 的待处理请求上限 | 256 |
| `retry_attempts` | 处理失败时的重试次数 | 3 |
| `retry_delay` | 重试间隔（秒） | 0.5 |

### 2. 受限场景
1. **队列满（429）**  
   - 当某个 session 的队列达到 `max_queue_size` 时，`SimulationWorker.submit` 会抛出异常 → FastAPI 返回 `HTTP 429`，并告知“simulation queue at capacity”。
   - 应对：客户端可退回 429，并在数百毫秒后重试；若持续触发，考虑扩容 worker 或回放速度限流。

2. **任务失败重试**  
   - `SimulationService.process_tick` 出现异常时，Worker 会自动重试（最多 3 次）。
   - 重试全部失败时，控制台会输出 `[!] SimulationWorker failed tick session:tick after N attempts: <error>`。建议收集日志并通过告警系统通知。

### 3. 监控指标
建议将以下指标纳入 Prometheus / Grafana：
| 指标 | 说明 |
|------|------|
| 队列长度 | `queue.qsize()` 定期采样 |
| 429 次数 | `/api/sim/step` 返回 429 的计数 |
| 重试事件 | 捕获失败日志或暴露 counter |
| 处理时延 | 通过 trace id 在接收/完成时记录 |

### 4. 告警建议
1. 队列长度超过 80%（约 > 200）持续 1 分钟，启动告警。
2. 429 次数在 5 分钟内超过阈值（如 50 次）需人工确认。
3. 重试全部失败的日志触发高优先级告警（若影响真实用户）。

### 5. Trace id 排查
所有 `/api/sim` 接口返回 `trace_id`，可以在日志中搜索  
`trace_id=<value>` 或 Redis key `sim:{session}:trace:{value}` 检查状态。
建议前端或调用方在请求头 `X-Trace-Id` 自带幂等 key，便于排错。

### 6. 队列扩容
若业务持续高并发，可通过环境变量或配置文件调整：
```python
SimulationWorker(service, max_queue_size=512, retry_attempts=5, retry_delay=1.0)
```
配合增加 worker 实例或分片（按 session_code hash）。
