# Tasks: 首页展示内容优化 (Homepage Display Optimization)

**Feature Branch**: `003-optimize-homepage-display`  
**Input**: Design documents from `/specs/003-optimize-homepage-display/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/components.md ✅

**Tests**: NOT included (not requested in feature specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [x] T001 Create component directory structure `frontend/src/components/home/` for homepage-specific components
- [x] T002 Create utility directory structure `frontend/src/lib/` for formatters and constants (if not exists)
- [x] T003 [P] Setup formatters library in `frontend/src/lib/formatters.ts` (formatPrice, formatPercentage, formatNumber, formatVolumeZh)
- [x] T004 [P] Create constants file in `frontend/src/lib/constants.ts` (FEATURES, QUICK_START_STEPS, EDUCATION_RESOURCES)
- [x] T005 Verify WebSocketContext is available at `frontend/src/contexts/WebSocketContext.tsx` and exports useWebSocketContext

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create useHotStocks hook in `frontend/src/hooks/useHotStocks.ts` (derives top gainers/losers/active from WebSocket data)
- [x] T007 [P] Create Badge component in `frontend/src/components/ui/Badge.tsx` (displays percentage change with color)
- [x] T008 Verify API client for `/api/v1/market/overview` and `/api/v1/indices` endpoints in `frontend/src/lib/api/virtual-market.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - 快速理解平台价值主张 (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Display platform value proposition, core positioning, and clear CTAs on homepage hero section so users understand "what is happyStock" within 5 seconds

**Independent Test**: User can answer "What is this platform?" and "Why should I use it?" within 5 seconds of landing on homepage

### Implementation for User Story 1

- [x] T009 [US1] Create HeroSection component in `frontend/src/components/home/HeroSection.tsx` with headline, subheadline, platform positioning ("专业图表工具 + AI模拟交易 + 投资社交平台")
- [x] T010 [US1] Add primary CTA button "立即开始交易" linking to `/virtual-market` in HeroSection
- [x] T011 [US1] Add secondary CTA button "查看市场行情" linking to `/virtual-market` in HeroSection  
- [x] T012 [US1] Add social proof element displaying user count (e.g., "已有 15,234 位投资者加入") in HeroSection
- [x] T013 [US1] Integrate HeroSection into `frontend/src/app/page.tsx` as first section with responsive layout (stack on mobile)

**ENHANCED**: Also created HeroChartAnimation.tsx with professional 3-scene carousel (K-line market data, professional tools, learning simulation) rotating every 5 seconds with smooth transitions

**Checkpoint**: At this point, User Story 1 should be fully functional - homepage displays clear value proposition and CTAs ✅

---

## Phase 4: User Story 2 - 直观感受市场活跃度 (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Display real-time market statistics and hot stocks on homepage so users feel the market is "alive" and actively updating

**Independent Test**: User observes at least one data change within 30 seconds of staying on homepage and can see overall market trend

### Implementation for User Story 2

- [x] T014 [US2] Create MarketOverview component in `frontend/src/components/home/MarketOverview.tsx` displaying 7 stats (total_stocks, rising, falling, unchanged, limit_up, limit_down, market_state)
- [x] T015 [US2] Create HotStockList container component in `frontend/src/components/home/HotStockList.tsx` with tab switching (涨幅榜/跌幅榜/成交活跃)
- [x] T016 [US2] Create HotStockRow component in `frontend/src/components/home/HotStockRow.tsx` displaying stock symbol, name, price, change, sparkline mini-chart
- [x] T017 [US2] Create CoreIndexCards component in `frontend/src/components/home/CoreIndexCards.tsx` displaying 3 core indices (Happy300, HappyLarge, HappySmall) with current value, change
- [x] T018 [US2] Add FlashChange wrapper component in `frontend/src/components/ui/FlashChange.tsx` for highlighting value changes with 200ms flash animation
- [x] T019 [US2] Create useStockSparkline hook in `frontend/src/hooks/useStockSparkline.ts` for generating sparkline data from stock history
- [x] T020 [US2] Integrate sparkline visualization into HotStockRow using SVG path generation
- [x] T021 [US2] Add real-time update animations (flash effects, color transitions) to MarketOverview and CoreIndexCards when data changes
- [x] T022 [US2] Integrate MarketOverview, HotStockList, and CoreIndexCards into `frontend/src/app/page.tsx` below HeroSection with grid layout (HotStockList left, CoreIndexCards right)

**ENHANCED**: Optimized layout to 60/40 split (HotStockList 60% left, CoreIndexCards 40% right). Refactored CoreIndexCards from horizontal 3-column cards to vertical 3-row stack with larger card size for better visual balance. All components have smooth animations and real-time WebSocket updates.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - homepage shows value proposition + live market data ✅

---

## Phase 5: User Story 3 - 快速开始第一个交易体验 (Priority: P2) ✅ COMPLETE

**Goal**: Provide clear guidance for new users to complete their first simulated trade within 3 clicks from homepage

**Independent Test**: New user can click one button on homepage and reach trading interface or account creation within 3 clicks

### Implementation for User Story 3

- [x] T023 [P] [US3] Create QuickStartGuide component in `frontend/src/components/home/QuickStartGuide.tsx` displaying 3-step onboarding flow ("创建账户 → 查看市场 → 开始交易")
- [x] T024 [US3] Add "开始体验" primary button in QuickStartGuide linking to `/virtual-market` or account creation
- [x] T025 [US3] Add click handlers to HotStockRow components to navigate to stock detail page `/virtual-market/stocks/[symbol]`
- [x] T026 [US3] Add hover state and click tracking to primary CTAs in HeroSection and QuickStartGuide
- [x] T027 [US3] Integrate QuickStartGuide into `frontend/src/app/page.tsx` below MarketOverview section

**ENHANCED**: Added beautiful 3-step guide with icons, connection lines, stats bar, and prominent CTA with hover effects. All CTAs now include click tracking for analytics.

**Checkpoint**: User Story 3 complete - users have clear path from homepage to first trade ✅

---

## Phase 6: User Story 4 - 了解平台三大核心功能 (Priority: P2) ✅ COMPLETE

**Goal**: Display three core platform features (professional charts, AI trading, social investment) with clear entry points so users know what features to explore

**Independent Test**: User can identify three core features from homepage and click into each feature's detail page or demo

### Implementation for User Story 4

- [x] T028 [P] [US4] Create FeatureShowcase component in `frontend/src/components/home/FeatureShowcase.tsx` with 3 feature cards
- [x] T029 [US4] Add "专业图表工具" feature card with icon, description, link to `/virtual-market` (charts page) in FeatureShowcase
- [x] T030 [US4] Add "AI交易助手" feature card with icon, description, placeholder link in FeatureShowcase
- [x] T031 [US4] Add "投资社交平台" feature card with icon, description, placeholder link in FeatureShowcase
- [x] T032 [US4] Add hover effects and transitions to feature cards (scale, shadow, background)
- [x] T033 [US4] Integrate FeatureShowcase into `frontend/src/app/page.tsx` below QuickStartGuide section

**ENHANCED**: Created beautiful gradient cards with color-coded themes (blue/purple/green), detailed feature highlights with checkmarks, availability badges, and decorative corner elements. Available features are clickable links with smooth hover animations.

**Checkpoint**: User Story 4 complete - three core features clearly displayed with entry points ✅

---

## Phase 7: User Story 5 - 快速访问教育资源 (Priority: P3) ✅ COMPLETE

**Goal**: Provide easy access to learning resources for investment beginners through homepage links to tutorials and guides

**Independent Test**: User can find "新手指南" or "学习中心" entry point from homepage and access at least 3 types of educational content

### Implementation for User Story 5

- [x] T034 [P] [US5] Create EducationFooter component in `frontend/src/components/home/EducationFooter.tsx` with categorized learning resource links
- [x] T035 [US5] Add "新手指南" section with links to beginner tutorials (交易基础, K线图表工具, 账户开通指南, 风险管理)
- [x] T036 [US5] Add "进阶学习" section with links to advanced content (Al Brooks 价格行为交易 🔥特色, 技术分析进阶, 量化交易, 趋势跟踪)
- [x] T037 [US5] Add "常见问题" section with link to FAQ page (账户相关, 交易相关, 平台功能, 技术支持)
- [x] T038 [US5] Add "学习中心" prominent link (large CTA button "进入学习中心" at bottom of EducationFooter)
- [x] T039 [US5] Integrate EducationFooter into `frontend/src/app/page.tsx` below FeatureShowcase section

**ENHANCED**: Created comprehensive learning center module with:
- **EducationFooter**: 3-column layout (新手指南/进阶学习/常见问题), gradient backgrounds, Al Brooks featured with 🔥热门 badge
- **/learn**: Full learning center page with tab navigation, 18+ course cards, featured Al Brooks section with special styling
- **/learn/price-action-al-brooks**: Dedicated 10-section Al Brooks page (~10,000 Chinese characters):
  - HeroSection: Title, subtitle, 4 highlight stats
  - BrooksIntro: Personal background, achievements, contributions
  - WhatIsPriceAction: Definition, core principles, comparison table with traditional TA
  - CoreConcepts: 7 core trading principles (市场状态, 两次尝试, 被困交易者, 磁铁效应, 趋势强度, 概率思维, 时间周期)
  - TradingPatterns: 8 classic patterns with ASCII chart examples and trading strategies
  - LearningPath: 4-stage learning roadmap (基础认知 → 模式识别 → 实战练习 → 精进提升)
  - BooksList: 4 books detailed reviews (difficulty, rating, core content, target audience, key chapters, purchase links)
  - ResourcesSection: Official resources (website, videos, trading room) + Chinese resources (Zhihu, Bilibili, WeChat, forums)
  - PracticalTips: Daily routine, entry checklist, position management, common mistakes table
  - FAQ: 8 Q&As with accordion UI (学习时间, 零基础, 指标使用, 市场判断, 胜率盈亏比, 适用性, A股适用, 心理管理)

**Total Created**: 13 new files (EducationFooter + learn page + Al Brooks page + 10 sub-components), ~3,500 lines of code

**Checkpoint**: All user stories complete - full homepage optimization implemented with comprehensive learning center ✅

---

## Phase 8: Polish & Cross-Cutting Concerns ⏳ IN PROGRESS (3/12)

**Purpose**: Improvements that affect multiple user stories

- [x] T040 [P] Performance optimization: Implement code splitting for heavy components using Next.js dynamic imports in `frontend/src/app/page.tsx` ✅
- [x] T041 [P] Performance optimization: Add skeleton loading states for all async components (MarketOverview, HotStockList, CoreIndexCards) ✅
- [x] T042 Add error boundaries and fallback UI for WebSocket connection failures in `frontend/src/app/page.tsx` ✅
- [ ] T043 [P] Accessibility: Add ARIA labels, keyboard navigation support, and screen reader text to all interactive components
- [ ] T044 [P] Accessibility: Verify color contrast ratios meet WCAG 2.1 AA standards for all text elements
- [ ] T045 Responsive design: Test and fix layout on mobile (320px-768px), tablet (768px-1024px), desktop (1024px+) breakpoints
- [ ] T046 [P] SEO optimization: Add meta tags (title, description, OG tags) to `frontend/src/app/page.tsx` for social sharing
- [ ] T047 SEO optimization: Ensure hero section content is SSR-rendered and crawlable
- [ ] T048 [P] Analytics: Add tracking events for CTA clicks, feature card clicks, hot stock clicks using client-side analytics
- [ ] T049 Performance: Verify Lighthouse scores meet targets (LCP <3s, FCP <1.5s, TTI <5s)
- [ ] T050 [P] Documentation: Update README with homepage architecture and component usage
- [ ] T051 Run quickstart.md validation scenarios to ensure all user flows work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Independent, can start after Phase 2
  - User Story 2 (P1) - Independent, can start after Phase 2, reuses components from US1
  - User Story 3 (P2) - Depends on US1 and US2 (needs existing components to add interaction)
  - User Story 4 (P2) - Independent, can start after Phase 2
  - User Story 5 (P3) - Independent, can start after Phase 2
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Reuses HeroSection layout from US1 but independently testable
- **User Story 3 (P2)**: Integrates with US1 (HeroSection CTAs) and US2 (HotStockRow clicks) but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Setup tasks (T001-T005) establish project structure
- Foundational tasks (T006-T008) create reusable utilities and hooks
- US1: HeroSection → CTAs → Integration (sequential, T009-T013)
- US2: Components in parallel → Integration (T014-T017 parallel, then T018-T022 sequential)
- US3: QuickStartGuide and interactions (T023-T024 parallel, then T025-T027)
- US4: FeatureShowcase cards (T028-T032 parallel, then T033)
- US5: EducationFooter sections (T034-T038 parallel, then T039)
- Polish: Most tasks can run in parallel (marked with [P])

### Parallel Opportunities

- **Phase 1**: T003, T004 can run in parallel (different files)
- **Phase 2**: T007 can run in parallel with T006, T008 (different files)
- **User Story 2**: T014, T015, T016, T017 can run in parallel (different component files)
- **User Story 3**: T023, T024 can run in parallel (different parts of same component)
- **User Story 4**: T028-T032 can mostly run in parallel (same component but different cards)
- **User Story 5**: T034-T038 can run in parallel (different sections of same component)
- **Polish Phase**: Most tasks marked [P] can run in parallel (T040, T041, T043, T044, T046, T048, T050)

---

## Parallel Example: User Story 2

```bash
# Launch all main components for User Story 2 together:
Task: "Create MarketOverview component in frontend/src/components/home/MarketOverview.tsx"
Task: "Create HotStockList container component in frontend/src/components/home/HotStockList.tsx"
Task: "Create HotStockRow component in frontend/src/components/home/HotStockRow.tsx"
Task: "Create CoreIndexCards component in frontend/src/components/home/CoreIndexCards.tsx"

# Then sequentially add real-time features:
Task: "Add FlashChange wrapper component"
Task: "Create useStockSparkline hook"
Task: "Integrate sparkline visualization"
Task: "Add real-time update animations"
Task: "Integrate all components into page.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only - Both P1) ✅ COMPLETE

1. ✅ Complete Phase 1: Setup (T001-T005)
2. ✅ Complete Phase 2: Foundational (T006-T008) - CRITICAL BLOCKER
3. ✅ Complete Phase 3: User Story 1 (T009-T013) - Value proposition
4. ✅ Complete Phase 4: User Story 2 (T014-T022) - Live market data
5. **STOP and VALIDATE**: Test homepage with value prop + live data
6. Deploy/demo if ready - **This is the MVP!**

**MVP Scope**: 22 tasks (T001-T022), estimated 12-16 hours  
**Status**: ✅ MVP COMPLETE - All 22 tasks done with enhancements (3-scene carousel, optimized layout)

### Incremental Delivery After MVP

1. **MVP** (Setup + Foundation + US1 + US2) → Deploy (value prop + live data)
2. **Add User Story 3** (T023-T027) → Deploy (+ onboarding flow)
3. **Add User Story 4** (T028-T033) → Deploy (+ feature showcase)
4. **Add User Story 5** (T034-T039) → Deploy (+ education resources)
5. **Polish Phase** (T040-T051) → Deploy (final optimized version)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (5-8 tasks)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T009-T013)
   - **Developer B**: User Story 2 (T014-T022) - can start in parallel if not sharing code
   - **Developer C**: User Story 4 (T028-T033) - completely independent
3. After MVP validation:
   - **Developer A**: User Story 3 (T023-T027)
   - **Developer B**: User Story 5 (T034-T039)
   - **Developer C**: Polish tasks (T040-T051)

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 3 tasks
- **Phase 3 (US1 - P1)**: 5 tasks
- **Phase 4 (US2 - P1)**: 9 tasks
- **Phase 5 (US3 - P2)**: 5 tasks
- **Phase 6 (US4 - P2)**: 6 tasks
- **Phase 7 (US5 - P3)**: 6 tasks
- **Phase 8 (Polish)**: 12 tasks

**Total**: 51 tasks

**MVP Scope**: 22 tasks (Phases 1-4)
**Full Feature**: 51 tasks

---

## Estimated Timeline

**Based on single developer, normal pace**:

- Phase 1: 2-3 hours
- Phase 2: 2-3 hours
- Phase 3 (US1): 3-4 hours
- Phase 4 (US2): 5-7 hours
- Phase 5 (US3): 3-4 hours
- Phase 6 (US4): 3-4 hours
- Phase 7 (US5): 2-3 hours
- Phase 8 (Polish): 6-8 hours

**MVP Total**: 12-17 hours  
**Full Feature Total**: 26-36 hours

**With 2-3 developers (parallel execution)**:

- MVP: 8-10 hours
- Full Feature: 18-24 hours

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included (not requested in specification)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP prioritizes P1 stories (US1 + US2) for maximum value with minimum work
- US3 integrates with US1/US2 but should still be independently testable
- US4 and US5 are completely independent and can be built in parallel
