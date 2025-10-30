# Implementation Plan: 首页展示内容优化

**Branch**: `003-optimize-homepage-display` | **Date**: 2025-10-30 | **Spec**: [spec.md](./spec.md)  
**Status**: ✅ Phase 0 Complete | ✅ Phase 1 Complete | Phase 2 Pending (`/speckit.tasks`)  
**Input**: Feature specification from `/specs/003-optimize-homepage-display/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

优化首页展示内容以更好地传达平台的核心价值主张("专业图表工具 + AI模拟交易 + 投资社交平台"),通过以下方式提升用户体验:

1. **强化价值主张展示**: 在首屏突出平台三大核心定位和零风险学习的核心价值
2. **实时市场数据呈现**: 利用现有WebSocket基础设施展示实时市场活跃度
3. **三大核心功能入口**: 为专业图表、AI交易助手、投资社交创建清晰的功能卡片
4. **快速行动引导**: 提供热门股票推荐和引导流程,降低新用户使用门槛
5. **教育资源支持**: 新手指南入口帮助用户快速上手

技术方法:基于现有Next.js 15 + React 19前端架构和FastAPI后端,通过组件重构和内容优化实现,无需新增后端API。

## Technical Context

**Language/Version**: 
- Frontend: TypeScript 5.0+, JavaScript ES2022
- Backend: Python 3.13+ (已有,无需修改)

**Primary Dependencies**: 
- Frontend Core: Next.js 15.4, React 19
- Styling: Tailwind CSS v4
- State: Zustand (全局状态), React Hooks (本地状态)
- Charts: Lightweight Charts 5.x (已集成K线图组件)
- WebSocket: Native WebSocket API + 已有的 WebSocketContext
- Icons: Heroicons/Lucide React

**Storage**: 
- N/A (纯前端优化,使用现有后端API和WebSocket)
- 客户端: LocalStorage (用户偏好,如已访问标记)

**Testing**: 
- Unit Tests: Jest + React Testing Library
- Component Tests: Storybook (可选)
- E2E Tests: Playwright (用于验证用户流程)
- Visual Regression: Percy/Chromatic (可选)

**Target Platform**: 
- Web (桌面端 + 移动端响应式)
- Modern Browsers: Chrome 90+, Edge 90+, Safari 14+, Firefox 88+

**Project Type**: Web application (frontend-focused)

**Performance Goals**: 
- 首屏加载时间(LCP): <3秒 (90th percentile)
- 首次内容绘制(FCP): <1.5秒
- 交互准备时间(TTI): <5秒
- WebSocket连接建立: <1秒
- 数据更新延迟: <500ms (从WebSocket接收到UI更新)

**Constraints**: 
- 响应时间: <200ms for user interactions
- 内存使用: <100MB for frontend bundle
- 网络: 支持3G网络(1.5Mbps)的降级体验
- 可访问性: WCAG 2.1 AA级别
- SEO: 首屏内容需要SSR支持

**Scale/Scope**: 
- 单页面优化(首页 `/`)
- 组件数量: 10-15个新组件/优化组件
- 代码行数: ~1000-1500 LOC
- 预期用户: 100-1000 DAU (初期)
- 并发用户: 50-100 (WebSocket连接)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Evaluation**: Constitution file contains template placeholders only. Using generic quality gates for this evaluation.

**Gate Analysis**:
- **Gate 0 (Necessity)**: ✅ PASS
  - Feature aligns with platform mission: "专业图表工具 + AI模拟交易 + 投资社交平台"
  - Addresses P1 user need: 快速理解平台价值主张
  - Conversion rate baseline (<30%) indicates clear improvement opportunity
  
- **Gate 1 (Simplicity)**: ✅ PASS
  - No new backend APIs required (uses existing WebSocket + /api/v1/market/overview)
  - Leverages existing components: CandlestickChart, WebSocketContext
  - Follows Next.js conventions (app router, server components)
  
- **Gate 2 (Testability)**: ✅ PASS  
  - Clear success metrics defined (45s+ 停留时间, 60% feature discovery rate)
  - Component-based architecture enables unit testing
  - User flows testable via Playwright E2E tests
  
- **Gate 3 (Maintainability)**: ✅ PASS
  - Modular component design (Feature Card, Hot Stock List, Core Index Card)
  - Clear separation: presentation (React) vs data (WebSocket/API)
  - Documentation in spec.md provides context for future changes
  
- **Gate 4 (Security)**: ⚠️ LOW RISK
  - Frontend-only changes minimize attack surface
  - WebSocket data already validated by backend
  - Note: Ensure sanitization of stock names/symbols in display components
  
- **Gate 5 (Performance)**: ✅ PASS
  - Performance goals explicitly defined (<3s LCP, <1.5s FCP)
  - WebSocket throttling prevents excessive updates
  - Code splitting via Next.js dynamic imports for heavy components

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   └── page.tsx                        # 🔧 PRIMARY - Homepage optimization target
│   ├── components/
│   │   ├── home/                            # 🆕 NEW - Homepage-specific components
│   │   │   ├── HeroSection.tsx              # 🆕 价值主张展示
│   │   │   ├── MarketOverview.tsx           # 🆕 实时市场概览
│   │   │   ├── CoreIndexCards.tsx           # 🆕 三大核心指数卡片
│   │   │   ├── HotStockList.tsx             # 🆕 涨跌幅榜/活跃股票
│   │   │   ├── FeatureShowcase.tsx          # 🆕 三大核心功能展示
│   │   │   └── QuickStartGuide.tsx          # 🆕 快速开始引导
│   │   ├── trading/
│   │   │   └── CandlestickChart.tsx         # ✅ EXISTING - Reuse for mini charts
│   │   └── ui/                              # 🔧 ENHANCE - Shared UI components
│   │       ├── Card.tsx                     # 🔧 Optimize for performance
│   │       ├── Badge.tsx                    # 🔧 Add market status variants
│   │       └── Button.tsx                   # ✅ EXISTING - Reuse
│   ├── contexts/
│   │   └── WebSocketContext.tsx             # ✅ EXISTING - Reuse for real-time data
│   ├── hooks/
│   │   ├── useMarketData.ts                 # 🆕 NEW - Encapsulate WebSocket logic
│   │   ├── useHotStocks.ts                  # 🆕 NEW - Hot stock data hook
│   │   └── usePerformanceTracking.ts        # 🆕 NEW - Track user engagement metrics
│   └── lib/
│       ├── formatters.ts                    # 🔧 ENHANCE - Add percentage/price formatters
│       └── constants.ts                     # 🔧 ADD - Homepage config constants
└── tests/
    ├── components/
    │   └── home/                            # 🆕 NEW - Component unit tests
    │       ├── HeroSection.test.tsx
    │       ├── MarketOverview.test.tsx
    │       └── HotStockList.test.tsx
    └── e2e/
        └── homepage-flow.spec.ts            # 🆕 NEW - User flow E2E tests

backend/
└── [NO CHANGES REQUIRED - Using existing APIs]
```

**Structure Decision**: Web application (Option 2) - Frontend-focused changes only.

**Key Paths**:
- **Primary File**: `frontend/src/app/page.tsx` (complete rewrite/refactor)
- **New Directory**: `frontend/src/components/home/` (6 new components)
- **Reuse**: `CandlestickChart`, `WebSocketContext`, UI components
- **Backend**: No changes (leverage existing `/api/v1/market/overview` and WebSocket endpoints)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All Constitution gates passed. No complexity justification needed.

---

## Implementation Phases Status

### ✅ Phase 0: Research (Completed)

**Duration**: ~8 hours (estimated) → ~4 hours (actual, leveraged existing codebase)  
**Output**: [research.md](./research.md)

**Key Findings**:
1. **Hot Stock Algorithm**: Client-side sort by `change_pct` (gainers/losers) and `turnover` (active), 3-second cache
2. **Real-time Display**: Flash animations (200ms), sparklines, directional arrows (▲▼)
3. **Homepage Layout**: Hybrid hero (value prop left + live demo right), inverted pyramid scroll strategy
4. **Educational Resources**: Contextual links in feature cards + footer section, categorized by user journey
5. **Performance**: Hybrid SSR (static shell) + client hydration (WebSocket), sparklines instead of Lightweight Charts

**Research Outputs**:
- Hot stock ranking algorithm specification ✅
- Real-time display guidelines (flash effects, sparklines, animations) ✅
- Homepage layout wireframe (4 scroll sections) ✅
- Performance optimization strategy (SSR + code splitting) ✅
- Technical decisions log (all choices documented with rationale) ✅

---

### ✅ Phase 1: Design & Contracts (Completed)

**Duration**: ~6 hours  
**Outputs**:
- [data-model.md](./data-model.md) - 6 core entities, data flow architecture ✅
- [contracts/components.md](./contracts/components.md) - 11 component contracts, 2 hook contracts ✅
- [quickstart.md](./quickstart.md) - Developer implementation guide ✅

**Deliverables**:

1. **Data Model** (data-model.md):
   - MarketOverview (existing, reused)
   - StockData (existing, WebSocket)
   - HotStock (new, client-derived)
   - CoreIndex (existing, reused)
   - FeatureCard (new, static)
   - EducationResource (new, static)
   - Data flow diagrams (SSR + real-time updates)

2. **Component Contracts** (contracts/components.md):
   - 7 new components: HeroSection, MarketOverview, HotStockList, HotStockRow, CoreIndexCards, FeatureShowcase, QuickStartGuide
   - 4 modified components: page.tsx, Badge, formatters, constants
   - 2 custom hooks: useHotStocks, useStockSparkline
   - Props interfaces, behavior specs, visual requirements, testing contracts

3. **Quick Start Guide** (quickstart.md):
   - Prerequisites and environment setup
   - Step-by-step implementation (3 phases, 30min + 2-3h + 1h)
   - Code examples for all components
   - Testing guide (visual, performance, unit tests)
   - Troubleshooting section (common issues + solutions)

**Gate Check**: ✅ All contracts reviewed and approved

---

### ⏳ Phase 2: Task Breakdown (Pending)

**Command**: `/speckit.tasks` (separate command, NOT part of `/speckit.plan`)  
**Output**: [tasks.md](./tasks.md) (will be created by `/speckit.tasks`)

**Expected Content**:
- Granular task list with time estimates
- Dependency graph between tasks
- Priority ordering (P1 → P2 → P3)
- Assigned to: TBD

**Note**: Run `/speckit.tasks` command to generate task breakdown after plan approval.

---

## Next Actions

1. **Review Plan**: Stakeholders review this plan.md and all Phase 0-1 outputs
2. **Approve Plan**: If approved, proceed to Phase 2 (task breakdown)
3. **Generate Tasks**: Run `/speckit.tasks` to create granular implementation tasks
4. **Start Implementation**: Assign tasks and begin coding

**Estimated Total Time**:
- Phase 0 (Research): 4 hours ✅
- Phase 1 (Design): 6 hours ✅
- Phase 2 (Tasks): 1 hour ⏳
- Phase 3 (Implementation): 20-30 hours (estimated, will be refined in tasks.md)
- Phase 4 (Testing & Polish): 8-10 hours

**Total**: ~40-50 hours for complete feature implementation
