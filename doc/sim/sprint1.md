# Sprint 1：架构与环境推进记录

## 目标定位
- 建立可复用的本地/云端 PostgreSQL（TimescaleDB）与 Redis 部署方案。
- 准备统一的容器编排模板，为后续仿真后端与 API 联调提供基础设施。
- 明确运维要点（AOF、监控、连接池参数），支撑 ≥500 并发和低延迟目标。

## 本地部署方案
1. 复制仓库根目录下的 `docker-compose.sim.yml`。
2. 在 `.env` 或 PowerShell 会话中导出：
   ```powershell
   $env:SIM_DB_PASSWORD = "ChangeMe123!"
   $env:SIM_REDIS_PASSWORD = "SimRedisPass!"
   ```
3. 执行：
   ```powershell
   docker compose -f docker-compose.sim.yml up -d timescale redis
   docker compose -f docker-compose.sim.yml logs -f timescale
   ```
4. 初始化扩展：
   ```powershell
   docker exec -it sim-timescale psql -U postgres -d happystock -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
   ```

### Windows 现有 Redis 安装
- 已在 `C:\Redis` 检测到官方 Windows Redis 发行版，可直接运行 `C:\Redis\redis-server.exe`；
- 启动脚本 `start.bat` 会自动检查并复用该实例，后续仿真模块只需在 `.env` 中指向 `localhost:6379`；
- 推荐将 `C:\Redis\redis.windows.conf` 按上述参数（appendonly、appendfsync 等）调整并以 `redis-server.exe redis.windows.conf` 启动，确保持久化策略一致。

## 云端部署建议
- **Managed PostgreSQL/TimescaleDB**：优先选择 Timescale Cloud、AWS RDS for PostgreSQL（需手动启用 timescaledb）。设置 `max_connections` ≥ 200、`shared_buffers` ≥ 25% 内存、开启 `timescaledb.telemetry_level=off`。
- **Redis 服务**：选择 AWS ElastiCache / Azure Cache for Redis。启用 AOF（everysec）、复制集 + 自动故障转移，配置 CloudWatch/Prometheus 告警阈值（CPU > 70%、内存 > 75%、连接数接近上限）。
- **网络安全**：数据库与缓存放置在私有子网，通过安全组或防火墙仅向应用子网开放端口。

## Redis 参数基线
| 项目 | 建议值 |
| ---- | ------ |
| appendonly | yes |
| appendfsync | everysec |
| maxmemory-policy | allkeys-lru |
| tcp-keepalive | 60 |
| hash-max-ziplist-entries | 512 |

## 监控与运维要点
- PostgreSQL：启用 pg_stat_statements，采集慢查询；Timescale 使用 `timescaledb_information.hypertable` 监控 chunk 数量。
- Redis：采集 `used_memory`, `connected_clients`, `instantaneous_ops_per_sec` 指标；设置 `repl-backlog-size` ≥ 128MB 支撑瞬时写入。
- Compose 部署需配合 `docker stats` 与 `docker logs` 做首轮健康检查。

## 尚未完成事项
- [ ] 编写 Kubernetes 清单，覆盖 statefulset/operator 场景
- [ ] 与 DevOps 团队确认云端审计日志与备份策略

## 当前进度摘要（2025-11-03）
- ✅ 校验本地 `C:\Redis` 安装并补充持久化建议；
- ✅ 提供 Timescale/Redis 部署指南与参数基线；
- ✅ `docker-compose.sim.yml` 样例已提交，可直接 `docker compose up -d` 启动。
