# Quick Start Guide: A股虚拟市场

**Date**: 2025-10-28
**Audience**: 开发人员
**Purpose**: 快速启动和运行虚拟市场系统

## Prerequisites

确保你的开发环境已安装：
- **Python 3.13** (后端)
- **Node.js 18+** (前端)
- **PostgreSQL 14+** (数据库)
- **Redis 7+** (缓存)
- **Pipenv** (Python包管理)

## Step 1: 数据库初始化

### 1.1 创建数据库

```bash
# PostgreSQL
createdb happystock_dev

# 或使用psql
psql -U postgres
CREATE DATABASE happystock_dev;
\q
```

### 1.2 执行数据库脚本

```bash
# 从项目根目录执行
cd E:\work\code\happyStock

# 先执行用户表（如果还没有）
psql -U postgres -d happystock_dev -f sql_scripts/create_user_table.sql

# 执行虚拟市场表（本功能）
psql -U postgres -d happystock_dev -f sql_scripts/init_virtual_market.sql
```

### 1.3 验证表创建

```sql
psql -U postgres -d happystock_dev

-- 检查表是否创建成功
\dt

-- 应该看到以下表：
-- stocks, stock_metadata, sectors, indices,
-- index_constituents, price_data, market_states
```

## Step 2: 后端设置

### 2.1 安装依赖

```bash
cd backend

# 安装所有依赖（包括新增的NumPy和APScheduler）
pipenv install numpy apscheduler

# 安装开发依赖
pipenv install --dev pytest pytest-asyncio httpx
```

### 2.2 配置环境变量

创建 `backend/.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/happystock_dev

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 应用配置
DEBUG=True
PRICE_GENERATION_ENABLED=True  # 是否启用价格生成定时任务
```

### 2.3 生成初始数据

运行数据初始化脚本（生成106只股票的90天历史数据）：

```bash
pipenv shell

# 运行数据初始化
python -m backend.lib.data_initializer

# 这将：
# 1. 插入106只股票的基本信息和元数据
# 2. 插入10个板块信息
# 3. 插入13个指数定义
# 4. 建立指数成分股关系
# 5. 生成90天的历史K线数据（约1500万条记录，需要10-20分钟）

# 注意：初始化过程可能较长，请耐心等待
```

### 2.4 启动后端服务

```bash
# 在backend目录下
pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或者先进入虚拟环境
pipenv shell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端启动**:
- 访问 http://localhost:8000 应该看到API根响应
- 访问 http://localhost:8000/docs 应该看到Swagger文档
- 访问 http://localhost:8000/api/v1/stocks 应该返回股票列表

## Step 3: 前端设置

### 3.1 安装依赖

```bash
cd frontend

# 安装Lightweight Charts图表库
npm install lightweight-charts

# 安装类型定义
npm install --save-dev @types/lightweight-charts
```

### 3.2 启动前端开发服务器

```bash
# 在frontend目录下
npm run dev

# 前端将运行在 http://localhost:3000
```

**验证前端启动**:
- 访问 http://localhost:3000 应该看到首页
- 访问 http://localhost:3000/stocks 应该看到股票列表
- 访问 http://localhost:3000/indices 应该看到指数看板

## Step 4: 验证系统运行

### 4.1 检查价格生成任务

后端启动后，APScheduler会每分钟自动生成价格数据。查看控制台输出：

```
INFO:     Started server process
INFO:     Waiting for application startup.
Scheduler started
INFO:     Application startup complete.
[2025-10-28 10:00:00] Generating prices...  # 每分钟会看到这条日志
```

### 4.2 测试API

```bash
# 获取股票列表
curl http://localhost:8000/api/v1/stocks | json_pp

# 获取某只股票详情
curl http://localhost:8000/api/v1/stocks/600001 | json_pp

# 获取K线数据
curl "http://localhost:8000/api/v1/stocks/600519/klines?period=1d&limit=30" | json_pp

# 获取指数列表
curl http://localhost:8000/api/v1/indices | json_pp

# 获取HAPPY300详情
curl http://localhost:8000/api/v1/indices/HAPPY300 | json_pp
```

### 4.3 测试前端页面

打开浏览器访问：

1. **股票列表**: http://localhost:3000/stocks
   - 应该看到至少100只股票
   - 可以按板块筛选
   - 显示实时价格和涨跌幅

2. **股票详情**: http://localhost:3000/stocks/600001
   - 显示股票完整信息
   - 显示K线图
   - 显示Beta系数和指数权重

3. **指数看板**: http://localhost:3000/indices
   - 显示HAPPY300、HAPPY50、GROW100三大指数
   - 显示涨跌点数和涨跌幅

4. **板块热力图**: http://localhost:3000/sectors
   - 显示10大板块的当日涨跌
   - 用颜色深浅表示涨跌幅

## Step 5: 开发工作流

### 5.1 启动全套开发环境

建议使用3个终端窗口：

```bash
# Terminal 1 - PostgreSQL & Redis（如果未自动启动）
# Windows: 通过服务管理启动
# Linux/Mac:
brew services start postgresql
brew services start redis

# Terminal 2 - 后端
cd backend
pipenv run uvicorn main:app --reload

# Terminal 3 - 前端
cd frontend
npm run dev
```

### 5.2 代码修改后的热重载

- **后端**: FastAPI的`--reload`参数会自动检测`.py`文件变化并重启
- **前端**: Next.js会自动检测`.tsx`文件变化并热更新

### 5.3 测试运行

```bash
# 后端测试
cd backend
pipenv run pytest tests/

# 前端测试
cd frontend
npm test
```

## Step 6: 数据管理

### 6.1 重置数据库

如果需要清空并重新生成数据：

```bash
# 删除所有表数据（保留表结构）
psql -U postgres -d happystock_dev -c "TRUNCATE stocks, stock_metadata, sectors, indices, index_constituents, price_data, market_states CASCADE;"

# 重新运行数据初始化
cd backend
pipenv run python -m lib.data_initializer
```

### 6.2 查看价格数据统计

```sql
-- 查看总数据量
SELECT COUNT(*) FROM price_data;

-- 查看每只股票的数据量
SELECT target_code, COUNT(*) as count
FROM price_data
WHERE target_type = 'STOCK'
GROUP BY target_code
ORDER BY count DESC
LIMIT 10;

-- 查看最新价格
SELECT s.symbol, s.name, s.current_price, s.change_pct
FROM stocks s
ORDER BY s.market_cap_tier, s.current_price DESC
LIMIT 20;
```

## Common Issues & Troubleshooting

### Issue 1: 数据库连接失败

**症状**: `Connection refused` 或 `password authentication failed`

**解决方法**:
```bash
# 检查PostgreSQL是否运行
pg_isready

# 检查连接字符串
# backend/.env中的DATABASE_URL是否正确
```

### Issue 2: 历史数据生成太慢

**症状**: 运行`data_initializer.py`超过30分钟仍未完成

**解决方法**:
```python
# 修改初始化脚本，减少历史数据范围
# backend/lib/data_initializer.py

# 从90天改为30天
HISTORY_DAYS = 30  # 原来是90

# 从分钟级改为日级
PRICE_INTERVAL = '1d'  # 原来是'1m'
```

### Issue 3: 前端无法获取数据

**症状**: 前端显示"Failed to fetch"或空白

**解决方法**:
```typescript
// 检查前端API基础URL配置
// frontend/src/services/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// 确保后端CORS配置允许前端域名
// backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 开发环境
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 4: 定时任务未运行

**症状**: 控制台没有"Generating prices..."日志

**解决方法**:
```python
# 检查scheduler是否启动
# backend/main.py

@app.on_event("startup")
async def startup_event():
    if os.getenv("PRICE_GENERATION_ENABLED", "True") == "True":
        scheduler.start()
        print("✅ Scheduler started")
    else:
        print("⚠️ Price generation disabled")
```

## Next Steps

现在你已经完成了虚拟市场的基础设置！接下来可以：

1. **查看任务列表**: 运行 `/speckit.tasks` 生成详细的实现任务清单
2. **开始实现**: 按照`tasks.md`中的任务逐步实现功能
3. **参考文档**:
   - [spec.md](spec.md) - 功能规格说明
   - [research.md](research.md) - 技术研究文档
   - [data-model.md](data-model.md) - 数据模型设计
   - [contracts/](contracts/) - API契约定义

## Useful Commands Cheat Sheet

```bash
# 后端
pipenv shell                    # 进入虚拟环境
pipenv install <package>        # 安装包
pytest tests/                   # 运行测试
uvicorn main:app --reload      # 启动后端

# 前端
npm run dev                     # 启动开发服务器
npm run build                   # 生产构建
npm test                        # 运行测试

# 数据库
psql -U postgres -d happystock_dev                    # 连接数据库
psql -d happystock_dev -f sql_scripts/xxx.sql         # 执行SQL文件
pg_dump happystock_dev > backup.sql                   # 备份数据库
```

---

**提示**: 如遇到问题，请查看详细的错误日志，并参考本文档的Troubleshooting章节。祝开发顺利！🚀
