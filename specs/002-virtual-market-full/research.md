# Technical Research: A股虚拟市场完整实现

**Date**: 2025-10-28
**Purpose**: 解决Technical Context中的技术选型问题，为Phase 1设计提供依据

## Research Tasks

### 1. K线图库选择

**问题**: 前端需要展示K线图和实时价格数据，需要选择合适的图表库

**候选方案**:

#### Option A: Lightweight Charts (TradingView官方)
**优点**:
- TradingView官方开源库，专为金融图表设计
- 性能极佳，WebGL渲染，支持大数据量（百万级数据点）
- 内置金融图表类型（K线、蜡烛图、折线图等）
- 轻量级（~200KB gzipped）
- TypeScript支持良好
- 实时数据更新API友好

**缺点**:
- 功能相对聚焦，只做金融图表
- 定制化程度中等（不如ECharts灵活）

**集成成本**: 低
**学习曲线**: 平缓
**社区活跃度**: 高（TradingView维护）

#### Option B: ECharts
**优点**:
- 功能全面，支持各种图表类型
- 定制化程度高，主题系统完善
- 社区资源丰富，中文文档完善
- 开源免费

**缺点**:
- 包体积较大（~900KB gzipped with K线扩展）
- 金融图表功能需要额外的candlestick扩展
- 性能不如Lightweight Charts（对于实时更新场景）

**集成成本**: 中
**学习曲线**: 中等
**社区活跃度**: 高

#### Option C: Recharts
**优点**:
- React生态原生组件
- 声明式API，与React理念契合
- 轻量级

**缺点**:
- 金融图表支持不佳（需要自己实现K线组件）
- 性能一般，大数据量下表现不佳
- 不适合实时更新场景

**集成成本**: 中（需要自定义K线组件）
**学习曲线**: 平缓
**社区活跃度**: 中

**决策**: ✅ **选择Lightweight Charts**

**理由**:
1. **专业性**: 本项目定位是"专业图表工具 + AI模拟交易"，Lightweight Charts是金融图表的行业标准
2. **性能**: 需要支持实时数据更新（每分钟刷新），Lightweight Charts性能最佳
3. **品牌一致性**: 规格说明中提到"TradingView级别的专业图表分析工具"，使用TradingView官方库最契合
4. **数据量**: 90天分钟级K线数据（约13万条），Lightweight Charts可轻松处理
5. **包体积**: 相比ECharts更轻量，符合前端性能目标

**安装命令**:
```bash
npm install lightweight-charts
npm install @types/lightweight-charts --save-dev
```

**参考文档**: https://tradingview.github.io/lightweight-charts/

---

### 2. API集成测试策略

**问题**: 需要确定后端API的集成测试方法

**候选方案**:

#### Option A: Postman Collections + Newman
**优点**:
- Postman UI友好，便于手动测试
- 可导出为CI/CD可用的Newman脚本
- 支持环境变量、测试脚本

**缺点**:
- 需要维护额外的Postman collection文件
- 与Python测试框架分离，难以共享fixture

#### Option B: pytest + requests + pytest-asyncio
**优点**:
- 与单元测试框架统一，可共享fixture和helper
- Python生态，代码化测试易于版本控制
- 支持异步测试（适配FastAPI的async endpoint）
- 易于集成到CI/CD pipeline

**缺点**:
- 没有GUI，纯代码编写测试

**决策**: ✅ **选择pytest + requests + pytest-asyncio**

**理由**:
1. **一致性**: 后端已使用pytest，保持测试工具链统一
2. **代码优先**: API契约由OpenAPI spec定义，测试代码化更易维护
3. **异步支持**: FastAPI是异步框架，pytest-asyncio是最佳选择
4. **CI/CD友好**: 纯Python测试易于集成GitHub Actions或GitLab CI

**安装命令**:
```bash
pipenv install --dev pytest requests pytest-asyncio httpx
```

**测试结构**:
```python
# backend/tests/integration/test_stocks_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_get_stock_list():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stocks")
        assert response.status_code == 200
        assert len(response.json()) >= 100  # 至少100只股票
```

---

### 3. 部署目标环境

**问题**: 明确开发、测试、生产环境的部署方式

**候选方案**:

#### Option A: 本地开发（无容器化）
**适用场景**: MVP开发阶段
**优点**:
- 快速启动，无需Docker知识
- 调试方便，直接访问进程

**缺点**:
- 环境一致性差，依赖本地Python/Node版本
- 数据库、Redis需要手动安装

#### Option B: Docker Compose
**适用场景**: 团队协作、测试环境
**优点**:
- 环境一致，一键启动所有服务（PostgreSQL, Redis, Backend, Frontend）
- 易于分享和复现
- 接近生产环境

**缺点**:
- 初次配置需要编写Dockerfile和docker-compose.yml
- 资源消耗稍大

#### Option C: 云平台（Vercel前端 + Railway后端）
**适用场景**: 生产部署
**优点**:
- Vercel完美支持Next.js，自动部署
- Railway支持Python + PostgreSQL + Redis一体化
- 免费额度适合MVP

**缺点**:
- 绑定特定云平台
- 数据持久化需要额外配置

**决策**: ✅ **三阶段策略**

1. **开发阶段（当前）**: 本地开发，无容器化
   - Frontend: `npm run dev` (localhost:3000)
   - Backend: `pipenv run uvicorn` (localhost:8000)
   - Database: 本地PostgreSQL安装
   - Redis: 本地Redis安装

2. **测试/协作阶段**: Docker Compose
   - 提供`docker-compose.yml`便于团队成员快速启动
   - 包含PostgreSQL, Redis, Backend, Frontend四个服务

3. **生产部署（未来）**: 云平台
   - Frontend: Vercel (Next.js自动部署)
   - Backend + DB: Railway或Render
   - 可根据实际情况调整

**当前阶段行动**:
- ✅ 保持现状（本地开发）
- ⏭️ 后续阶段再引入Docker Compose（不在当前MVP范围）

**理由**:
- 项目处于Week 1-2的早期MVP阶段，团队规模小（可能solo开发）
- 本地开发效率最高，无需额外学习Docker
- 符合Constitution Check中的"简洁优先"原则

---

### 4. 价格生成算法 - 几何布朗运动（GBM）实现

**问题**: 需要生成具有真实感的股票价格波动

**技术选型**: ✅ **NumPy + 几何布朗运动（Geometric Brownian Motion）**

**决策依据**:

#### 几何布朗运动（GBM）公式
股票价格满足随机微分方程：
```
dS = μS dt + σS dW
```
其中：
- S: 股票价格
- μ: 漂移率（drift，市场趋势）
- σ: 波动率（volatility）
- dW: 维纳过程（Wiener process，随机扰动）

**离散化公式**（用于代码实现）：
```
S(t+Δt) = S(t) × exp((μ - σ²/2)Δt + σ√Δt × Z)
```
其中Z ~ N(0, 1)（标准正态分布）

**三层影响因子**:
根据规格说明，个股价格 = 市场影响(30%) + 板块影响(30%) + 个股波动(40%)

```python
# 简化的实现逻辑
market_trend = get_market_state().daily_trend  # 如牛市: +0.5%, 熊市: -0.5%
sector_trend = market_trend * sector.beta * 0.5 + sector_noise * 0.5
individual_gbm = geometric_brownian_motion(stock.volatility)

final_change = (
    market_trend * stock.beta * 0.3 +
    sector_trend * 0.3 +
    individual_gbm * 0.4
)
new_price = stock.current_price * (1 + final_change)
```

**NumPy优势**:
- 高效的向量化运算（可一次性为106只股票生成价格）
- 内置随机数生成器（`numpy.random.normal`）
- 数学函数支持（`numpy.exp`, `numpy.sqrt`）

**参考实现**:
```python
import numpy as np

def generate_price(current_price, volatility, drift, dt=1/1440):
    """
    生成下一个价格点
    dt = 1/1440 表示1分钟（1天=1440分钟）
    """
    z = np.random.normal(0, 1)
    change = (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * z
    return current_price * np.exp(change)
```

**验证方法**:
- 统计生成价格的日均波动率，应接近预设的σ
- 计算个股与大盘的相关系数，应接近Beta值
- 检查涨跌停限制（±10%）是否生效

**依赖安装**:
```bash
pipenv install numpy
```

---

### 5. 定时任务调度 - APScheduler

**问题**: 每分钟自动生成价格数据和计算指数

**技术选型**: ✅ **APScheduler (Advanced Python Scheduler)**

**决策依据**:

#### APScheduler vs 其他方案

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| APScheduler | 轻量级、内嵌式、易集成FastAPI | 单机方案、无分布式支持 | MVP、中小规模应用 |
| Celery + Redis | 分布式任务队列、高可靠性 | 架构复杂、需要额外的broker和worker | 大规模生产环境 |
| Cron + 脚本 | 简单、系统级 | 与应用分离、难以管理 | 独立批处理任务 |

**选择APScheduler的理由**:
1. **轻量级**: 符合MVP阶段的简洁原则，无需额外部署worker
2. **易集成**: 可直接嵌入FastAPI应用，启动时自动开始调度
3. **功能足够**: 支持cron表达式、interval调度、date调度
4. **持久化支持**: 可选的SQLAlchemy job store（后续需要时可启用）

**实现示例**:
```python
# backend/scheduler/jobs.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=1, id='generate_prices')
async def generate_market_prices():
    """每分钟生成一次价格"""
    print(f"[{datetime.now()}] Generating prices...")
    # 调用价格生成引擎
    await price_generator.generate_all_stocks()
    await index_calculator.calculate_all_indices()

# backend/main.py
from fastapi import FastAPI
from scheduler.jobs import scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("Scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
```

**依赖安装**:
```bash
pipenv install apscheduler
```

---

## Summary of Decisions

| 决策点 | 选择 | 主要理由 |
|--------|------|----------|
| **K线图库** | Lightweight Charts | 专业性强、性能优秀、品牌一致性 |
| **API集成测试** | pytest + requests | 与现有测试框架统一、代码化易维护 |
| **部署策略** | 三阶段（当前本地开发） | 符合MVP阶段、简洁优先原则 |
| **价格生成算法** | NumPy + GBM | 行业标准算法、高效向量化运算 |
| **定时任务** | APScheduler | 轻量级、易集成、功能足够 |

## Next Steps (Phase 1)

所有NEEDS CLARIFICATION项已解决，可以进入Phase 1：
1. ✅ 创建data-model.md（数据模型设计）
2. ✅ 创建contracts/（API契约定义）
3. ✅ 创建quickstart.md（快速开始指南）
