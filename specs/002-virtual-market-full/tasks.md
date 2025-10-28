# Tasks: A股虚拟市场完整实现

**Input**: Design documents from `/specs/002-virtual-market-full/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. This task list focuses on implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/` and `frontend/` at repository root
- Backend Python: `backend/lib/`, `backend/models/`, `backend/api/`, `backend/scheduler/`
- Frontend TypeScript: `frontend/src/app/`, `frontend/src/components/`
- Database scripts: `sql_scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure (lib/, models/, api/, scheduler/) per plan.md
- [ ] T002 Install backend dependencies: `pipenv install numpy apscheduler`
- [ ] T003 [P] Install frontend dependencies: `npm install lightweight-charts`
- [ ] T004 [P] Create SQL schema file `sql_scripts/init_virtual_market.sql` based on data-model.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create database tables: Execute `sql_scripts/init_virtual_market.sql` (stocks, stock_metadata, sectors, indices, index_constituents, price_data, market_states)
- [ ] T006 [P] Insert sector data: 10 sectors with beta coefficients in `backend/lib/data_initializer.py`
- [ ] T007 [P] Insert index definitions: 13 indices (HAPPY300/50/GROW100 + 10 sector indices) in `backend/lib/data_initializer.py`
- [ ] T008 [P] Define Stock model in `backend/models/stock.py` (symbol, name, current_price, sector_code, etc.)
- [ ] T009 [P] Define StockMetadata model in `backend/models/stock.py` (beta, volatility, market_cap, etc.)
- [ ] T010 [P] Define Index model in `backend/models/index.py` (code, name, current_value, base_point, etc.)
- [ ] T011 [P] Define Sector model in `backend/models/market.py` (code, name, beta, avg_change_pct)
- [ ] T012 [P] Define PriceData model in `backend/models/price.py` (target_type, target_code, timestamp, OHLC)
- [ ] T013 [P] Define MarketState model in `backend/models/market.py` (state, daily_trend, volatility_multiplier)
- [ ] T014 Configure database connection pool in `backend/lib/db_manager.py` (PostgreSQL + connection pooling)
- [ ] T015 Setup FastAPI CORS middleware in `backend/main.py` for localhost:3000
- [ ] T016 [P] Create base API response schemas in `backend/api/schemas.py` (Error, StockSummary, IndexSummary)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 查看真实感的股票市场数据 (Priority: P1) 🎯 MVP

**Goal**: 用户能看到100+只虚拟股票，具有真实A股特征（代码、价格、板块分类、90天历史K线）

**Independent Test**: 访问 http://localhost:3000/stocks 显示至少100只股票，每只有代码、名称、价格、涨跌幅、板块。点击任意股票查看详情和K线图。

### Implementation for User Story 1

#### Backend - 股票数据初始化

- [ ] T017 [P] [US1] Insert 106 stocks data in `backend/lib/data_initializer.py` (金融12只+消费15只+科技20只+新能源10只+医药12只+工业10只+地产8只+能源8只+材料6只+公用事业5只)
- [ ] T018 [P] [US1] Insert stock metadata (beta, market_cap, volatility) for all 106 stocks in `backend/lib/data_initializer.py`
- [ ] T019 [US1] Implement price generation algorithm using GBM in `backend/lib/price_generator.py` (geometric_brownian_motion function with numpy)
- [ ] T020 [US1] Implement historical data generation (90 days, daily K-lines initially) in `backend/lib/data_initializer.py` (generates ~9540 records: 106 stocks × 90 days)
- [ ] T021 [US1] Run data initialization script to populate database with stocks + 90-day history

#### Backend - 股票API实现

- [ ] T022 [P] [US1] Implement GET /api/v1/stocks endpoint in `backend/api/stocks.py` (list stocks with filters: sector, search, sort, pagination)
- [ ] T023 [P] [US1] Implement GET /api/v1/stocks/{symbol} endpoint in `backend/api/stocks.py` (stock detail with metadata)
- [ ] T024 [P] [US1] Implement GET /api/v1/stocks/{symbol}/klines endpoint in `backend/api/stocks.py` (K-line data with period filter)
- [ ] T025 [US1] Register stock routes in `backend/main.py` (app.include_router from api.stocks)

#### Frontend - 股票列表页面

- [ ] T026 [P] [US1] Create stock list page in `frontend/src/app/stocks/page.tsx` (displays 100 stocks, pagination)
- [ ] T027 [P] [US1] Create StockList component in `frontend/src/app/components/StockList.tsx` (table with symbol, name, price, change%, sector)
- [ ] T028 [P] [US1] Create PriceDisplay component in `frontend/src/app/components/PriceDisplay.tsx` (format price, show red/green for change)
- [ ] T029 [US1] Implement sector filter dropdown in `frontend/src/app/stocks/page.tsx` (filter by 10 sectors)
- [ ] T030 [US1] Implement search functionality in `frontend/src/app/stocks/page.tsx` (search by symbol or name)

#### Frontend - 股票详情页面

- [ ] T031 [P] [US1] Create stock detail page in `frontend/src/app/stocks/[symbol]/page.tsx` (dynamic route)
- [ ] T032 [P] [US1] Create KLineChart component in `frontend/src/app/components/KLineChart.tsx` (using lightweight-charts library)
- [ ] T033 [US1] Fetch and display stock metadata (beta, market_cap, sector) in stock detail page
- [ ] T034 [US1] Fetch and render 90-day K-line data in KLineChart component
- [ ] T035 [US1] Add time period selector (日K/周K/月K) to KLineChart component

**Checkpoint**: At this point, User Story 1 should be fully functional - users can browse stocks, view details, and see K-line charts

---

## Phase 4: User Story 2 - 理解市场整体走势通过指数 (Priority: P1)

**Goal**: 用户能看到HAPPY300/50/GROW100三大指数的实时点位、涨跌幅和K线图，了解指数成分股和权重

**Independent Test**: 访问 http://localhost:3000/indices 显示3大指数的当前点位和涨跌幅。点击HAPPY300查看成分股列表及权重。

### Implementation for User Story 2

#### Backend - 指数成分股关系

- [ ] T036 [P] [US2] Insert index constituents for HAPPY300 (top 100 stocks by market cap) in `backend/lib/data_initializer.py`
- [ ] T037 [P] [US2] Insert index constituents for HAPPY50 (top 50 from HAPPY300) in `backend/lib/data_initializer.py`
- [ ] T038 [P] [US2] Insert index constituents for GROW100 (50 growth stocks) in `backend/lib/data_initializer.py`
- [ ] T039 [US2] Calculate initial weights for all index constituents in `backend/lib/data_initializer.py` (free-float market cap weighted, max 10% per stock)

#### Backend - 指数计算引擎

- [ ] T040 [US2] Implement HAPPY300Calculator class in `backend/lib/index_calculator.py` (select_constituents, calculate_weights, calculate_index methods)
- [ ] T041 [US2] Implement weight calculation with 10% cap in `backend/lib/index_calculator.py` (apply_weight_cap function)
- [ ] T042 [US2] Implement divisor initialization and management in `backend/lib/index_calculator.py` (store in database or config)
- [ ] T043 [US2] Generate 90-day historical index values based on constituent stock prices in `backend/lib/data_initializer.py`

#### Backend - 指数API实现

- [ ] T044 [P] [US2] Implement GET /api/v1/indices endpoint in `backend/api/indices.py` (list all indices with type filter)
- [ ] T045 [P] [US2] Implement GET /api/v1/indices/{code} endpoint in `backend/api/indices.py` (index detail)
- [ ] T046 [P] [US2] Implement GET /api/v1/indices/{code}/constituents endpoint in `backend/api/indices.py` (list constituents with weights)
- [ ] T047 [P] [US2] Implement GET /api/v1/indices/{code}/klines endpoint in `backend/api/indices.py` (index K-line data)
- [ ] T048 [US2] Register index routes in `backend/main.py`

#### Frontend - 指数看板页面

- [ ] T049 [P] [US2] Create indices page in `frontend/src/app/indices/page.tsx` (index dashboard)
- [ ] T050 [P] [US2] Create IndexCard component in `frontend/src/app/components/IndexCard.tsx` (displays index name, value, change%)
- [ ] T051 [US2] Display 3 core indices (HAPPY300/50/GROW100) in grid layout on indices page
- [ ] T052 [US2] Add color coding (red/green) based on index change in IndexCard component

#### Frontend - 指数详情页面

- [ ] T053 [P] [US2] Create index detail page in `frontend/src/app/indices/[code]/page.tsx` (dynamic route)
- [ ] T054 [US2] Display index K-line chart (reuse KLineChart component from US1)
- [ ] T055 [US2] Display constituents table with symbol, name, weight, rank in index detail page
- [ ] T056 [US2] Add link from constituent to stock detail page (navigate to /stocks/[symbol])

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can view both stocks and indices

---

## Phase 5: User Story 3 - 观察市场联动效果 (Priority: P2)

**Goal**: 当大盘上涨时，大部分股票跟随上涨（且不同板块涨幅不同），用户能观察到Beta系数的影响

**Independent Test**: 观察HAPPY300上涨1%时，科技板块涨约1.3%、金融板块涨约0.7%、公用事业涨约0.5%。查看股票详情页显示Beta值及解释。

### Implementation for User Story 3

#### Backend - 市场状态管理

- [ ] T057 [US3] Implement MarketStateManager class in `backend/lib/market_state_manager.py` (get_current_state, transition_state methods)
- [ ] T058 [US3] Insert initial market state (BULL/BEAR/SIDEWAYS) in `backend/lib/data_initializer.py`
- [ ] T059 [US3] Implement state transition logic in `backend/lib/market_state_manager.py` (牛市→横盘→熊市 cycle, min 7 days per state)

#### Backend - 三层价格生成机制

- [ ] T060 [US3] Enhance price_generator.py with market influence (30%) in `backend/lib/price_generator.py` (market_trend × stock.beta × 0.3)
- [ ] T061 [US3] Enhance price_generator.py with sector influence (30%) in `backend/lib/price_generator.py` (sector_trend × 0.3)
- [ ] T062 [US3] Keep individual GBM component (40%) in `backend/lib/price_generator.py` (existing GBM × 0.4)
- [ ] T063 [US3] Implement sector_trend calculation in `backend/lib/price_generator.py` (market_trend × sector.beta + noise)
- [ ] T064 [US3] Add 涨跌停 limit (±10%) to price generation in `backend/lib/price_generator.py`

#### Backend - 板块统计API

- [ ] T065 [P] [US3] Implement GET /api/v1/sectors endpoint in `backend/api/market.py` (list 10 sectors with avg_change_pct)
- [ ] T066 [P] [US3] Implement GET /api/v1/sectors/{code}/stocks endpoint in `backend/api/market.py` (stocks in sector)
- [ ] T067 [P] [US3] Implement GET /api/v1/market/state endpoint in `backend/api/market.py` (current market state)
- [ ] T068 [US3] Register market routes in `backend/main.py`

#### Frontend - 板块热力图

- [ ] T069 [P] [US3] Create sectors page in `frontend/src/app/sectors/page.tsx`
- [ ] T070 [P] [US3] Create SectorHeatMap component in `frontend/src/app/components/SectorHeatMap.tsx` (grid of sectors colored by change%)
- [ ] T071 [US3] Fetch sector data and calculate color intensity based on avg_change_pct in SectorHeatMap
- [ ] T072 [US3] Add sector name and change% labels to heatmap cells

#### Frontend - Beta系数显示

- [ ] T073 [US3] Add Beta display to stock detail page in `frontend/src/app/stocks/[symbol]/page.tsx` (show beta value + explanation)
- [ ] T074 [US3] Add tooltip/help icon for Beta in stock detail page (explain "Beta>1表示比大盘波动大")
- [ ] T075 [US3] Display market_cap_tier (超大盘/大盘/中盘/小盘/微盘) in stock detail page

**Checkpoint**: All联动 features work - users can observe market linkage and understand Beta

---

## Phase 6: User Story 4 - 获取实时更新的市场数据 (Priority: P2)

**Goal**: 市场数据每分钟自动更新，用户无需刷新页面即可看到价格变化

**Independent Test**: 打开股票列表或指数看板，等待1-2分钟，观察数据自动刷新（价格、涨跌幅变化）

### Implementation for User Story 4

#### Backend - 定时任务调度

- [ ] T076 [US4] Implement scheduler setup in `backend/scheduler/jobs.py` (APScheduler AsyncIOScheduler)
- [ ] T077 [US4] Create generate_prices_job in `backend/scheduler/jobs.py` (runs every 1 minute)
- [ ] T078 [US4] Call price_generator.generate_all_stocks() in generate_prices_job
- [ ] T079 [US4] Call index_calculator.calculate_all_indices() in generate_prices_job
- [ ] T080 [US4] Start scheduler on FastAPI startup in `backend/main.py` (@app.on_event("startup"))
- [ ] T081 [US4] Shutdown scheduler gracefully in `backend/main.py` (@app.on_event("shutdown"))

#### Backend - 批量价格生成优化

- [ ] T082 [US4] Implement generate_all_stocks method in `backend/lib/price_generator.py` (vectorized with numpy for 106 stocks)
- [ ] T083 [US4] Implement calculate_all_indices method in `backend/lib/index_calculator.py` (calculate 13 indices)
- [ ] T084 [US4] Batch insert new price_data records in `backend/lib/price_generator.py` (use executemany for performance)
- [ ] T085 [US4] Update stocks table current_price and change_pct after generation in `backend/lib/price_generator.py`

#### Frontend - 自动刷新机制

- [ ] T086 [US4] Implement auto-refresh with setInterval (60 seconds) in `frontend/src/app/stocks/page.tsx`
- [ ] T087 [US4] Implement auto-refresh for index dashboard in `frontend/src/app/indices/page.tsx`
- [ ] T088 [US4] Add loading indicator during data fetch in stock list page
- [ ] T089 [US4] Pause auto-refresh when user is inactive (>5 min) in `frontend/src/app/stocks/page.tsx`
- [ ] T090 [US4] Resume auto-refresh on user interaction in `frontend/src/app/stocks/page.tsx`

**Checkpoint**: Real-time updates work - prices change automatically every minute

---

## Phase 7: User Story 5 - 了解个股所属板块和市场地位 (Priority: P3)

**Goal**: 用户能查看每只股票的详细元数据（板块、市值大小、Beta、是否为指数成分股）

**Independent Test**: 点击任意股票进入详情页，查看板块归属、市值等级、Beta系数、在HAPPY300中的权重

### Implementation for User Story 5

#### Backend - 元数据增强

- [ ] T091 [US5] Ensure stock detail API includes full metadata in `backend/api/stocks.py` (market_cap_tier, beta, volatility, outstanding_shares, listing_date)
- [ ] T092 [US5] Add is_happy300 and weight_in_happy300 fields to stock detail response in `backend/api/stocks.py`
- [ ] T093 [US5] Query index_constituents to find which indices stock belongs to in `backend/api/stocks.py`

#### Frontend - 元数据展示

- [ ] T094 [US5] Create metadata section in stock detail page `frontend/src/app/stocks/[symbol]/page.tsx` (display all metadata fields)
- [ ] T095 [US5] Display "HAPPY300成分股，权重X%" if applicable in stock detail page
- [ ] T096 [US5] Display "非HAPPY300成分股" if not in HAPPY300 in stock detail page
- [ ] T097 [US5] Add section showing all indices this stock belongs to (with weights) in stock detail page

#### Frontend - 板块详情页

- [ ] T098 [P] [US5] Create sector detail page (if needed) in `frontend/src/app/sectors/[code]/page.tsx`
- [ ] T099 [US5] Display all stocks in selected sector with sector avg beta, total market cap

**Checkpoint**: Users can explore detailed stock metadata and sector information

---

## Phase 8: User Story 6 - 通过历史数据学习K线分析 (Priority: P3)

**Goal**: 用户能查看任意股票或指数的历史K线数据（至少90天），支持不同时间周期切换

**Independent Test**: 打开任意股票K线图，切换时间周期（日K、周K、月K），查看是否正确显示历史数据

### Implementation for User Story 6

#### Backend - K线数据聚合

- [ ] T100 [US6] Implement weekly K-line aggregation in `backend/api/stocks.py` (aggregate daily data to weekly)
- [ ] T101 [US6] Implement monthly K-line aggregation in `backend/api/stocks.py` (aggregate daily data to monthly)
- [ ] T102 [US6] Support period parameter (1d/1w/1M) in GET /klines endpoint in `backend/api/stocks.py`

#### Frontend - K线图增强

- [ ] T103 [US6] Add period selector UI (日K/周K/月K buttons) to KLineChart component in `frontend/src/app/components/KLineChart.tsx`
- [ ] T104 [US6] Implement period switching logic (re-fetch with different period) in KLineChart component
- [ ] T105 [US6] Add zoom and pan controls to K-line chart using lightweight-charts features
- [ ] T106 [US6] Display detailed info on hover (date, OHLC, volume, change%) in KLineChart component
- [ ] T107 [US6] Add volume bars below K-line chart in KLineChart component

**Checkpoint**: Users can analyze historical K-line data with different time periods

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T108 [P] Add error handling middleware in `backend/main.py` (catch all exceptions, return standard Error schema)
- [ ] T109 [P] Add request logging in `backend/main.py` (log all API requests with timestamp, method, path, status)
- [ ] T110 [P] Implement Redis caching for GET /stocks and GET /indices in `backend/api/stocks.py` and `backend/api/indices.py` (cache for 30 seconds)
- [ ] T111 [P] Add database connection pooling optimization in `backend/lib/db_manager.py` (configure pool size, overflow)
- [ ] T112 [P] Add loading states to all frontend pages in `frontend/src/app/*/page.tsx` (skeleton loaders or spinners)
- [ ] T113 [P] Add error boundaries to frontend app in `frontend/src/app/layout.tsx` (catch React errors gracefully)
- [ ] T114 [P] Optimize frontend bundle size (code splitting, lazy loading for charts) in `frontend/next.config.js`
- [ ] T115 [P] Add responsive design for mobile devices in all frontend components (media queries, Tailwind responsive classes)
- [ ] T116 Code cleanup: Remove console.log statements, fix linting warnings in backend and frontend
- [ ] T117 Performance testing: Verify 100 stocks load in <3s, K-line rendering <1s
- [ ] T118 Security review: Check SQL injection prevention, validate all user inputs
- [ ] T119 Run quickstart.md validation: Follow all steps to ensure documentation is accurate
- [ ] T120 Update README.md with feature overview and link to quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P3) → US6 (P3) in priority order
  - Or work on multiple stories in parallel if team capacity allows
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: ✅ Independent - Can start after Foundational
- **User Story 2 (P1)**: ⚠️ Soft dependency on US1 (needs stock data), but independently testable
- **User Story 3 (P2)**: ⚠️ Soft dependency on US1-2 (enhances existing features), but independently testable
- **User Story 4 (P2)**: ⚠️ Soft dependency on US1-2 (adds real-time to existing data), but independently testable
- **User Story 5 (P3)**: ⚠️ Soft dependency on US1 (enhances stock detail page), but independently testable
- **User Story 6 (P3)**: ⚠️ Soft dependency on US1 (enhances K-line chart), but independently testable

**Note**: All user stories are designed to be independently testable. Soft dependencies mean they enhance existing features but can be validated on their own.

### Within Each User Story

- Backend data initialization before API implementation
- API implementation before frontend pages
- Models/components can be built in parallel [P]
- Integration tasks depend on component tasks being complete

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004 can all run in parallel (different files)

**Phase 2 (Foundational)**:
- T006, T007, T008-T013, T016 can run in parallel after T005 (database creation)

**Phase 3 (US1)**:
- T017-T018 (data insertion) can run in parallel
- T022-T024 (API endpoints) can run in parallel after models are done
- T026-T028 (frontend components) can run in parallel
- T031-T032 (detail page components) can run in parallel

**Phase 4 (US2)**:
- T036-T038 (index constituents) can run in parallel
- T044-T047 (API endpoints) can run in parallel
- T049-T050 (frontend components) can run in parallel

**Phase 5-8**: Similar patterns - components and API endpoints can be built in parallel within each story

**Phase 9 (Polish)**:
- T108-T115 can all run in parallel (different concerns)

---

## Parallel Example: User Story 1 (查看真实感的股票市场数据)

```bash
# Parallel group 1: Data preparation
Task: "T017 [P] [US1] Insert 106 stocks data"
Task: "T018 [P] [US1] Insert stock metadata"

# Sequential: T019-T021 (depends on above)

# Parallel group 2: API endpoints
Task: "T022 [P] [US1] Implement GET /api/v1/stocks"
Task: "T023 [P] [US1] Implement GET /api/v1/stocks/{symbol}"
Task: "T024 [P] [US1] Implement GET /api/v1/stocks/{symbol}/klines"

# Parallel group 3: Frontend components
Task: "T026 [P] [US1] Create stock list page"
Task: "T027 [P] [US1] Create StockList component"
Task: "T028 [P] [US1] Create PriceDisplay component"

# Parallel group 4: Detail page
Task: "T031 [P] [US1] Create stock detail page"
Task: "T032 [P] [US1] Create KLineChart component"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only - Both P1)

**推荐的MVP范围**: US1 + US2（查看股票 + 查看指数）

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T016) - **CRITICAL BLOCKING PHASE**
3. Complete Phase 3: User Story 1 (T017-T035) - 股票功能完整可用
4. Complete Phase 4: User Story 2 (T036-T056) - 指数功能完整可用
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready - **此时已有完整的股票+指数查看功能**

**为什么US1+US2作为MVP**:
- 两者都是P1优先级
- 覆盖了核心价值：股票数据 + 市场指数
- 用户可以浏览股票、查看K线、理解大盘
- 后续US3-US6是增强功能，可渐进交付

### Incremental Delivery (Full Feature)

1. Complete Setup + Foundational → Foundation ready (T001-T016)
2. Add US1 + US2 → MVP ready (T017-T056) → Deploy/Demo 🎯
3. Add US3 (market linkage) → Enhanced realism (T057-T075) → Deploy/Demo
4. Add US4 (real-time updates) → Live market (T076-T090) → Deploy/Demo
5. Add US5 (metadata) → Deep insights (T091-T099) → Deploy/Demo
6. Add US6 (K-line analysis) → Full charting (T100-T107) → Deploy/Demo
7. Polish → Production ready (T108-T120) → Deploy/Demo

### Parallel Team Strategy

With 2-3 developers after Foundational phase completes:

1. Team completes Setup + Foundational together (T001-T016)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T017-T035) - 股票功能
   - **Developer B**: User Story 2 (T036-T056) - 指数功能
   - **Developer C** (optional): Start US3 or prepare infrastructure for US4
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 120 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 12 tasks ⚠️ BLOCKING
- Phase 3 (US1): 19 tasks 🎯 MVP
- Phase 4 (US2): 21 tasks 🎯 MVP
- Phase 5 (US3): 19 tasks
- Phase 6 (US4): 15 tasks
- Phase 7 (US5): 9 tasks
- Phase 8 (US6): 8 tasks
- Phase 9 (Polish): 13 tasks

**MVP Scope** (US1+US2): 56 tasks (Setup + Foundational + US1 + US2)

**Parallel Opportunities**: ~50 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**: Each user story has clear test criteria - can be validated without completing other stories

---

## Notes

- [P] tasks = different files/concerns, no sequential dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **重要提示**: Phase 2 (Foundational) 必须100%完成才能开始任何用户故事
- **建议**: 先完成US1+US2作为MVP，验证后再继续US3-US6
- **数据量**: 初始化90天历史数据可能需要10-20分钟，可以先用30天测试
