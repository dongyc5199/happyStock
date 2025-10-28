# Implementation Plan: A股虚拟市场完整实现

**Branch**: `002-virtual-market-full` | **Date**: 2025-10-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-virtual-market-full/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

实现一个包含106只虚拟股票、3大核心指数（HAPPY300/50/GROW100）和10个行业板块的完整A股模拟市场系统。系统将生成具有真实市场特征的价格数据（市场联动、板块轮动、Beta系数影响），为用户提供零风险的投资学习环境。

**核心功能**：
- 106只虚拟股票（覆盖10大行业板块）+ 完整的股票元数据（Beta、市值、板块归属）
- 3大核心指数（HAPPY300综合、HAPPY50蓝筹、GROW100成长）+ 10个行业指数
- 三层价格生成机制（市场状态 → 板块联动 → 个股波动）
- 每分钟自动生成实时价格数据 + 90天历史K线数据
- 前端展示：股票列表、指数看板、板块热力图、K线图、股票详情

**技术方法**：采用定时任务驱动的价格生成引擎，使用几何布朗运动（GBM）+ 市场/板块影响因子的混合算法生成价格。指数采用自由流通市值加权法计算。前端使用图表库展示K线和实时数据。

## Technical Context

**Language/Version**:
- Backend: Python 3.13
- Frontend: TypeScript 5+ (Node.js运行时)

**Primary Dependencies**:
- Backend: FastAPI, psycopg2-binary (PostgreSQL driver), Redis, NumPy (价格生成算法), APScheduler (定时任务)
- Frontend: Next.js 15.4, React 19, Tailwind CSS v4, NEEDS CLARIFICATION: K线图库选择（Lightweight Charts vs ECharts vs Recharts）

**Storage**:
- Primary: PostgreSQL（存储股票元数据、价格历史数据、指数数据、成分股关系）
- Cache: Redis（缓存实时价格、会话数据）

**Testing**:
- Backend: pytest（单元测试）, pytest-asyncio（异步测试）
- Frontend: Jest + React Testing Library
- Integration: NEEDS CLARIFICATION: API集成测试策略（Postman collections vs pytest + requests）

**Target Platform**:
- Backend: Linux server (开发环境可能是Windows)
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge latest 2 versions)
- Deployment: NEEDS CLARIFICATION: 部署目标（本地开发 vs Docker容器 vs 云平台）

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- 价格生成：每分钟为106只股票 + 13个指数生成新数据，处理时间 < 5秒
- API响应：GET请求 < 500ms (p95), POST请求 < 1s (p95)
- 前端加载：首页 < 3秒，股票列表页（100只股票）< 3秒
- 数据刷新：前端自动刷新延迟 < 2秒

**Constraints**:
- 数据量：初始90天历史数据约1300万条记录（106股票 × 90天 × 1440分钟）
- 内存：前端页面内存占用 < 200MB，后端单进程 < 500MB
- 并发：支持100并发用户同时查看数据
- 涨跌停限制：股票单日涨跌幅 ±10%（模拟A股规则）
- 数据一致性：指数计算必须与成分股价格同步，误差 < 0.01点

**Scale/Scope**:
- 106只虚拟股票 + 13个指数（3核心 + 10行业）
- 10个行业板块
- 预计用户量：1000人以内（初期MVP）
- 数据保留：永久保留所有历史数据
- 代码规模：预估后端 3000-5000 LOC，前端 4000-6000 LOC

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ⚠️ CONDITIONAL PASS (Constitution template未完成，基于CLAUDE.md的项目原则进行检查)

由于项目的constitution.md文件仍为模板状态，我们基于CLAUDE.md中记录的项目架构和开发规范进行检查：

### 检查项

#### 1. 架构一致性 ✅
- **要求**: 遵循现有的Frontend (Next.js) + Backend (FastAPI) + Database (PostgreSQL) 架构
- **本功能**: 完全符合现有架构，扩展后端API和前端页面，使用相同的技术栈
- **结论**: 通过

#### 2. 数据库模式管理 ✅
- **要求**: 数据库schema定义在sql_scripts/目录下
- **本功能**: 将在sql_scripts/创建虚拟市场相关的SQL脚本（股票、指数、价格数据表）
- **结论**: 通过

#### 3. 开发环境一致性 ✅
- **要求**: 使用Pipenv管理Python依赖，npm管理前端依赖
- **本功能**: 新增的Python库（NumPy, APScheduler）将添加到Pipfile，前端图表库添加到package.json
- **结论**: 通过

#### 4. MVP阶段范围控制 ⚠️
- **要求**: 项目处于Week 1-2的早期MVP阶段，应聚焦核心功能
- **本功能**: 虚拟市场是核心功能之一，但范围较大（106股票+指数+联动机制+前端展示），可能需要2-3周完成
- **建议**: 考虑分阶段实施，先实现Phase 1-2（股票数据+指数计算），后续迭代添加Phase 3-4（联动机制+完整前端）
- **结论**: 有条件通过（建议分阶段）

#### 5. 代码组织规范 ✅
- **要求**: 前端使用@/*路径别名，App Router模式；后端RESTful API设计
- **本功能**: 将遵循现有规范，前端组件放在src/app/目录，后端API遵循REST原则
- **结论**: 通过

### 需要在Phase 1设计后重新检查的项
- [ ] 数据库表设计是否遵循现有的schema约定（外键、索引、命名规范）
- [ ] API endpoint设计是否与现有API风格一致
- [ ] 前端组件是否复用现有的UI组件和样式系统

## Project Structure

### Documentation (this feature)

```text
specs/002-virtual-market-full/
├── spec.md              # 功能规格说明（已完成）
├── plan.md              # 本文件（实现计划）
├── research.md          # Phase 0 输出（技术研究文档）
├── data-model.md        # Phase 1 输出（数据模型设计）
├── quickstart.md        # Phase 1 输出（快速开始指南）
├── contracts/           # Phase 1 输出（API契约定义）
│   ├── stocks-api.yaml  # 股票相关API
│   ├── indices-api.yaml # 指数相关API
│   └── market-api.yaml  # 市场数据API
├── checklists/
│   └── requirements.md  # 规格质量检查清单（已完成）
└── tasks.md             # Phase 2 输出（由/speckit.tasks生成）
```

### Source Code (repository root)

**Structure Decision**: 本项目采用Web application结构（frontend + backend），遵循现有的monorepo布局。

```text
happyStock/
├── backend/
│   ├── main.py                      # FastAPI入口（已存在）
│   ├── Pipfile                      # Python依赖（将添加numpy, apscheduler）
│   ├── lib/                         # 新增：业务逻辑库
│   │   ├── price_generator.py       # 价格生成引擎（GBM算法）
│   │   ├── index_calculator.py      # 指数计算器（HAPPY300/50/GROW100）
│   │   ├── market_state_manager.py  # 市场状态管理（牛/熊/横盘）
│   │   └── data_initializer.py      # 数据初始化（90天历史数据生成）
│   ├── models/                      # 新增：数据模型
│   │   ├── stock.py                 # Stock, StockMetadata模型
│   │   ├── index.py                 # Index, IndexConstituent模型
│   │   ├── price.py                 # PriceData模型
│   │   └── market.py                # MarketState, Sector模型
│   ├── api/                         # 新增：API路由
│   │   ├── stocks.py                # 股票相关endpoints
│   │   ├── indices.py               # 指数相关endpoints
│   │   └── market.py                # 市场数据endpoints
│   ├── scheduler/                   # 新增：定时任务
│   │   └── jobs.py                  # 价格生成、指数计算定时任务
│   └── tests/                       # 测试
│       ├── test_price_generator.py
│       ├── test_index_calculator.py
│       └── test_api/
│           ├── test_stocks_api.py
│           └── test_indices_api.py
│
├── frontend/
│   ├── src/
│   │   └── app/                     # Next.js App Router
│   │       ├── stocks/              # 新增：股票相关页面
│   │       │   ├── page.tsx         # 股票列表页
│   │       │   └── [symbol]/        # 股票详情页
│   │       │       └── page.tsx
│   │       ├── indices/             # 新增：指数相关页面
│   │       │   ├── page.tsx         # 指数看板
│   │       │   └── [code]/          # 指数详情页
│   │       │       └── page.tsx
│   │       ├── sectors/             # 新增：板块页面
│   │       │   └── page.tsx         # 板块热力图
│   │       └── components/          # 新增：共享组件
│   │           ├── StockList.tsx    # 股票列表组件
│   │           ├── IndexCard.tsx    # 指数卡片组件
│   │           ├── KLineChart.tsx   # K线图组件
│   │           ├── SectorHeatMap.tsx # 板块热力图组件
│   │           └── PriceDisplay.tsx # 价格显示组件
│   ├── package.json                 # 前端依赖（将添加图表库）
│   └── tests/                       # 前端测试
│       └── components/
│
├── sql_scripts/                     # 数据库脚本
│   ├── create_user_table.sql        # 已存在：用户表
│   └── init_virtual_market.sql      # 新增：虚拟市场所有表（本功能）
│       # 包含：stocks, stock_metadata, sectors, indices,
│       #       index_constituents, price_data, market_states
│
└── doc/
    └── A股虚拟市场完整设计方案.md  # 已存在：详细设计文档
```

**关键决策**：
1. **后端模块化**: 将价格生成、指数计算等核心逻辑放在lib/目录下，保持main.py简洁
2. **前端App Router**: 使用Next.js 15的App Router模式，stocks/和indices/作为主要路由
3. **数据库脚本**: 所有表定义集中在一个SQL文件（init_virtual_market.sql）便于初始化
4. **组件复用**: K线图、价格显示等组件设计为独立可复用组件

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
