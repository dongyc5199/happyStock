# 后端测试总结（2025-11）

本文记录当前后端可复现的测试集合、运行环境以及关键结论，涵盖两大模块：
1. **密码重置 / 邮件通知体系**（原有功能）
2. **仿真子系统**（SimulationService + Worker + API）

---

## 1. 环境与依赖
- Python 3.13（仓库 `Pipfile` 默认）
- PostgreSQL + TimescaleDB（可选，仿真测试在 Timescale 缺失时会跳过依赖用例）
- Redis 7+
- Pipenv 2024+

安装依赖：
```bash
pipenv install
pipenv install --dev  # 提供 httpx、pytest 等测试工具
```

常用测试命令：
```bash
# 运行所有单元测试
pipenv run pytest backend/tests/unit

# 仅运行仿真核心 + 集成验证
pipenv run pytest backend/tests/unit/test_sim_services.py backend/tests/integration/test_sim_flow.py

# 全量（包含可能依赖 Timescale/Redis 的集成测试）
pipenv run pytest backend/tests
```

---

## 2. 密码重置 & 邮件模块
- **测试时间**：2025-11-01 21:19
- **环境**：Redis、FastAPI、前端均在本地；SQLite 作为数据库；SMTP 尚未接入真实服务
- **核心结论**：
  - Token 生成/验证/标记逻辑全部通过（43 字节 URL-safe；重复使用阻断）
  - 邮件模板可渲染（Jinja2），含重置链接；SMTP 相关用例需待真实服务器配置后执行
  - API `POST /api/auth/forgot-password`、`POST /api/auth/reset-password` 代码完成，但端到端依赖 SMTP
- **后续建议**：
  1. 配置 SMTP（如 Gmail App Password）重新执行 smoke 测试
  2. 编写/补充前端回归脚本并记录在 `TEST_CHECKLIST.md`
  3. 迁移到 Pydantic v2 风格校验（当前警告提示）

---

## 3. 仿真子系统

### 3.1 单元测试：`backend/tests/unit/test_sim_services.py`
覆盖要点：
- `SimulationService.process_tick` 将新增订单/成交落地 Timescale（带 `participant_db_id`）并返回 `{"status": "accepted", "trace_id": ...}`
- 自动注册默认策略（散户、游资、机构、做市）及订单生成
- `SimulationWorker` 异步调用 + 重试逻辑（单测通过模拟 Repository/Cache）

执行：
```bash
pipenv run pytest backend/tests/unit/test_sim_services.py
```

### 3.2 集成测试：`backend/tests/integration`
- `test_sim_flow.py`：验证 `/api/sim/start → /api/sim/step → /api/sim/state` 完整流程、trace id、情绪/特征字段
- `test_sim_endpoints.py`：在 Timescale 可用时验证 API 返回 202；若检测到 503（仿真数据库未启动）则自动跳过

执行：
```bash
pipenv run pytest backend/tests/integration
```

### 3.3 运行前置条件
- Redis：`start_redis.sh` 或 `start_redis.bat`
- Timescale：若不在本地运行，可跳过依赖 Timescale 的集成测试；启用时需执行 `backend/sim/migrations/0001~0003`
- FastAPI：建议在单独终端启动 `pipenv run uvicorn main:app --reload`

### 3.4 主要变更摘要
- API `/api/sim/start|step|player/order|tick` 统一返回 `202 Accepted` 与 trace id，支持 `X-Trace-Id` 幂等
- `SimulationWorker` 新增队列限流（默认 256）、失败重试（默认 3 次）
- `SimulationService` 首次 tick 自动为 session 注册四类策略，并在 `/api/sim/state` 返回 `features`/`emotion`
- 文档更新：`doc/sim/README.md`、`doc/sim/plan.md`、`doc/sim/tasks.md`、`doc/sim/checklists.md`

---

## 4. 后续计划
1. 在 `backend/TEST_SUMMARY.md`（本文）持续补充新的模块测试记录
2. 整理 Pipenv 依赖说明（已新增 `httpx`、`pytest` 至 `[dev-packages]`）
3. 编写 SimulationWorker 运维手册（限流、重试、监控）并记录在 `doc/sim/tasks.md`
4. 配置 CI / CD：建议在 CI 环境运行 `pipenv run pytest backend/tests/unit backend/tests/integration/test_sim_flow.py`
