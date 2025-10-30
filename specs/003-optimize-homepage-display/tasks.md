# Tasks: 首页展示内容优化

**Feature Branch**: `003-optimize-homepage-display`  
**Input**: Design documents from `/specs/003-optimize-homepage-display/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: This feature does NOT explicitly request TDD approach. Test tasks are NOT included in initial implementation phases. Tests will be added in the Polish phase.

**Organization**: Tasks are grouped by user story (US1-US5 with priorities P1, P2, P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `backend/` (frontend-focused feature, no backend changes)
- All paths shown below use Windows-style absolute paths with forward slashes

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for homepage optimization

- [ ] T001 Create `frontend/src/components/home/` directory for homepage-specific components
- [ ] T002 Create `frontend/src/hooks/` directory if not exists (for custom hooks)
- [ ] T003 [P] Add formatter utilities in `frontend/src/lib/formatters.ts` (formatPrice, formatPercentage, formatNumber functions)
- [ ] T004 [P] Add homepage constants in `frontend/src/lib/constants.ts` (feature cards, quick start steps, education resources static data)
- [ ] T005 Verify WebSocketProvider is properly configured in `frontend/src/app/layout.tsx` (already exists, validate only)

**Checkpoint**: Basic project structure ready for component development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create `useHotStocks` custom hook in `frontend/src/hooks/useHotStocks.ts` (derives hot stock lists from WebSocket data)
- [ ] T007 Create `Badge` UI component in `frontend/src/components/ui/Badge.tsx` (percentage change badge with auto color variants)
- [ ] T008 Verify existing API client functions in `frontend/src/lib/api/virtual-market.ts` (marketApi.getMarketOverview, indicesApi.getIndices)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 快速理解平台价值主张 (Priority: P1) 🎯 MVP

**Goal**: 让用户在首页立即了解happyStock的核心价值("专业图表工具 + AI模拟交易 + 投资社交平台"),在5秒内理解平台定位

**Independent Test**: 
1. 访问 `http://localhost:3000/`
2. 验证首屏显示主标题包含"专业图表工具 + AI模拟交易 + 投资社交平台"
3. 验证副标题包含"零风险学习投资"
4. 验证有2个显著的CTA按钮("开始免费交易"和"查看功能演示")

### Implementation for User Story 1

- [ ] T009 [P] [US1] Create `HeroSection` component in `frontend/src/components/home/HeroSection.tsx` (hero section with value proposition, CTAs, social proof)
- [ ] T010 [US1] Update `frontend/src/app/page.tsx` to use `HeroSection` component (replace existing hero, add SSR data fetching)
- [ ] T011 [US1] Add social proof counter to `HeroSection` (display user count with increment animation)
- [ ] T012 [US1] Style `HeroSection` with Tailwind CSS (gradient background, responsive layout, 60-40 split)
- [ ] T013 [US1] Add "查看功能演示" modal placeholder in `HeroSection` (button triggers modal, modal shows "功能演示即将推出")

**Acceptance Verification**:
- [ ] ✅ User can see platform positioning in hero headline
- [ ] ✅ User can understand "zero-risk learning" value proposition
- [ ] ✅ User can identify two CTA buttons
- [ ] ✅ Hero section is responsive on mobile/tablet/desktop

**Checkpoint**: At this point, User Story 1 should be fully functional - homepage shows clear value proposition with CTAs

---

## Phase 4: User Story 2 - 直观感受市场活跃度 (Priority: P1)

**Goal**: 让用户在首页看到实时市场数据和活跃度指标,在30秒内观察到数据变化,感受市场"活"的特性

**Independent Test**:
1. 访问 `http://localhost:3000/`
2. 验证市场概况区域显示7项统计数据(总股票数、上涨、下跌、平盘、涨停、跌停、市场状态)
3. 等待30秒,验证至少一项数据发生变化
4. 验证核心指数卡片显示3个指数的实时数据
5. 验证热门股票列表显示实时涨跌数据

### Implementation for User Story 2

- [ ] T014 [P] [US2] Create `MarketOverview` component in `frontend/src/components/home/MarketOverview.tsx` (display market statistics, uses SSR initial data)
- [ ] T015 [P] [US2] Create `HotStockList` component in `frontend/src/components/home/HotStockList.tsx` (client component, uses useHotStocks hook)
- [ ] T016 [P] [US2] Create `HotStockRow` sub-component in `frontend/src/components/home/HotStockRow.tsx` (memoized row with flash animation, sparkline placeholder)
- [ ] T017 [P] [US2] Create `CoreIndexCards` component in `frontend/src/components/home/CoreIndexCards.tsx` (3 index cards, uses SSR data)
- [ ] T018 [US2] Update `frontend/src/app/page.tsx` to add `MarketOverview` section (fetch SSR data from /api/v1/market/overview)
- [ ] T019 [US2] Update `frontend/src/app/page.tsx` to add `HotStockList` sections (3 columns: gainers, losers, active)
- [ ] T020 [US2] Update `frontend/src/app/page.tsx` to add `CoreIndexCards` section (fetch SSR data from /api/v1/indices?type=CORE)
- [ ] T021 [US2] Add CSS flash animation for price changes in `HotStockRow` (200ms background flash, red for up, green for down)
- [ ] T022 [US2] Add `@media (prefers-reduced-motion: reduce)` styles for accessibility

**Acceptance Verification**:
- [ ] ✅ User can see market overview with 7 stats
- [ ] ✅ User observes data changes within 30 seconds
- [ ] ✅ User can see 3 core indices with real-time values
- [ ] ✅ Flash animations trigger on price updates
- [ ] ✅ Reduced motion preference is respected

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - homepage shows value proposition + real-time market data

---

## Phase 5: User Story 3 - 快速开始第一个交易体验 (Priority: P2)

**Goal**: 引导新用户快速开始第一次模拟交易,从首页点击一个按钮后3次点击内完成买入交易

**Independent Test**:
1. 访问 `http://localhost:3000/`
2. 点击"开始免费交易"按钮
3. 验证跳转到 `/virtual-market` 页面
4. 在热门股票列表点击任一股票
5. 验证跳转到 `/virtual-market/stocks/{symbol}` 详情页
6. 验证详情页有交易按钮可点击

### Implementation for User Story 3

- [ ] T023 [US3] Add primary CTA button link in `HeroSection` (href="/virtual-market", styled with blue gradient)
- [ ] T024 [US3] Ensure `HotStockRow` links to stock detail page (href="/virtual-market/stocks/{symbol}")
- [ ] T025 [US3] Add sticky CTA in homepage header (appears after 300px scroll, links to /virtual-market)
- [ ] T026 [US3] Verify stock detail page has trading functionality (check existing `/virtual-market/stocks/[symbol]/page.tsx`)
- [ ] T027 [US3] Add end-of-page CTA after all sections (duplicate of hero CTA, re-engage users)

**Acceptance Verification**:
- [ ] ✅ User can click "开始免费交易" and reach market page
- [ ] ✅ User can click hot stock and reach stock detail page
- [ ] ✅ Stock detail page has trading buttons visible
- [ ] ✅ Sticky CTA appears on scroll
- [ ] ✅ End-of-page CTA re-engages users

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - homepage guides users to first trade

---

## Phase 6: User Story 4 - 了解平台三大核心功能 (Priority: P2)

**Goal**: 让用户清晰了解三大核心功能(专业图表、AI交易、社交平台),能够点击进入每个功能的详细页面或演示

**Independent Test**:
1. 访问 `http://localhost:3000/`
2. 滚动到"三大核心功能"区域
3. 验证显示3个功能卡片(图表工具、AI交易、投资社交)
4. 点击"专业图表工具"卡片
5. 验证跳转到 `/virtual-market` (图表展示页面)
6. 返回首页,点击"AI交易助手"卡片
7. 验证显示说明或跳转到演示页面
8. 返回首页,点击"投资社交"卡片
9. 验证显示说明或跳转到演示页面

### Implementation for User Story 4

- [ ] T028 [P] [US4] Create `FeatureShowcase` component in `frontend/src/components/home/FeatureShowcase.tsx` (3 feature cards with icons, descriptions, CTAs)
- [ ] T029 [US4] Define feature cards data in `frontend/src/lib/constants.ts` (3 objects: chart tool, AI trading, social platform)
- [ ] T030 [US4] Import Lucide React icons in `FeatureShowcase` (BarChart3, Brain, Users)
- [ ] T031 [US4] Update `frontend/src/app/page.tsx` to add `FeatureShowcase` section (position between hot stocks and indices)
- [ ] T032 [US4] Add secondary action links to feature cards ("📖 学习K线图基础" for chart tool, contextual learning links)
- [ ] T033 [US4] Add hover effects to feature cards (shadow-lg to shadow-xl transition)

**Acceptance Verification**:
- [ ] ✅ User can see 3 distinct feature cards
- [ ] ✅ User can click "专业图表工具" and reach chart page
- [ ] ✅ User can click "AI交易助手" and see explanation
- [ ] ✅ User can click "投资社交" and see explanation
- [ ] ✅ Hover effects work smoothly

**Checkpoint**: At this point, User Stories 1-4 should all work - homepage showcases all three core platform features

---

## Phase 7: User Story 5 - 快速访问教育资源 (Priority: P3)

**Goal**: 为投资新手提供快速访问学习资源的入口,能够找到并访问至少3种教育内容

**Independent Test**:
1. 访问 `http://localhost:3000/`
2. 滚动到页面底部
3. 验证显示"新手指南"区域
4. 验证至少有3个教育资源链接(按难度分类)
5. 点击"K线图入门教程"
6. 验证跳转到教程页面(或显示"即将推出")

### Implementation for User Story 5

- [ ] T034 [P] [US5] Create `QuickStartGuide` component in `frontend/src/components/home/QuickStartGuide.tsx` (3-step visual guide: 注册 → 选股 → 下单)
- [ ] T035 [P] [US5] Create `EducationFooter` component in `frontend/src/components/home/EducationFooter.tsx` (3-column footer: 新手指南, 进阶技巧, 常见问题)
- [ ] T036 [US5] Define education resources data in `frontend/src/lib/constants.ts` (array of EducationResource objects)
- [ ] T037 [US5] Update `frontend/src/app/page.tsx` to add `QuickStartGuide` section (position after core indices)
- [ ] T038 [US5] Update `frontend/src/app/page.tsx` to add `EducationFooter` section (position at page end, before site footer)
- [ ] T039 [US5] Add contextual education links to `FeatureShowcase` (e.g., "📖 学习K线图基础" link in chart tool card)

**Acceptance Verification**:
- [ ] ✅ User can find "新手指南" section at bottom
- [ ] ✅ User can see 3-step quick start guide
- [ ] ✅ User can access 3+ education resource links
- [ ] ✅ Contextual learning links work in feature cards
- [ ] ✅ Education footer has 3-column layout

**Checkpoint**: At this point, ALL user stories (1-5) should work independently - homepage is fully functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and overall quality

### Performance Optimization

- [ ] T040 [P] Enable Next.js compression in `frontend/next.config.ts` (compress: true, optimizePackageImports: ['lucide-react'])
- [ ] T041 [P] Optimize Tailwind CSS purging in `frontend/tailwind.config.js` (verify content paths include all components)
- [ ] T042 [P] Add font optimization in `frontend/src/app/layout.tsx` (use next/font/google for Inter font)
- [ ] T043 Measure bundle size with `npm run build` (target: <100KB gzipped homepage bundle)
- [ ] T044 Add loading skeleton screens to all SSR components (MarketOverview, CoreIndexCards)
- [ ] T045 Add error boundaries to handle API failures gracefully (show fallback UI on error)

### Accessibility

- [ ] T046 [P] Add `aria-label` attributes to all icon buttons in components
- [ ] T047 [P] Add `aria-live="polite"` to real-time updating sections (HotStockList, MarketOverview)
- [ ] T048 [P] Verify color contrast meets WCAG AA standards (red-600, green-600, blue-600)
- [ ] T049 Run axe-core accessibility audit with Chrome DevTools (fix all critical issues)
- [ ] T050 Test keyboard navigation (Tab through all interactive elements, Enter to activate)

### Testing (Added in Polish Phase)

- [ ] T051 [P] Write unit tests for `useHotStocks` hook in `frontend/src/hooks/useHotStocks.test.ts`
- [ ] T052 [P] Write unit tests for formatters in `frontend/src/lib/formatters.test.ts`
- [ ] T053 [P] Write component tests for `HeroSection` in `frontend/src/components/home/HeroSection.test.tsx`
- [ ] T054 [P] Write component tests for `HotStockRow` (test memoization) in `frontend/src/components/home/HotStockRow.test.tsx`
- [ ] T055 Create E2E test for homepage engagement flow in `frontend/tests/e2e/homepage-flow.spec.ts` (using Playwright)

### Documentation & Validation

- [ ] T056 [P] Update README.md with homepage optimization details
- [ ] T057 Run quickstart.md validation (follow implementation guide step-by-step)
- [ ] T058 Take screenshots for documentation (hero, market overview, hot stocks, features, education)
- [ ] T059 Validate all acceptance criteria from spec.md (checklist of 15+ scenarios)
- [ ] T060 Run Lighthouse performance audit (target: Performance 90+, Accessibility 95+)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Can start immediately after Phase 2
- **User Story 2 (Phase 4)**: Depends on Foundational - Can start immediately after Phase 2 (parallel with US1)
- **User Story 3 (Phase 5)**: Depends on US1 + US2 components (needs HeroSection, HotStockRow)
- **User Story 4 (Phase 6)**: Depends on Foundational - Can start after Phase 2 (parallel with US1/US2)
- **User Story 5 (Phase 7)**: Depends on US4 (needs FeatureShowcase for contextual links)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Setup (Phase 1) → Foundational (Phase 2) → [US1, US2, US4 can run in parallel]
                                             ↓       ↓       ↓
                                            US3 ← [US1+US2]  US5 ← US4
                                             ↓                ↓
                                          [All stories complete] → Polish (Phase 8)
```

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Needs US1 (HeroSection) and US2 (HotStockRow) for CTA links
- **User Story 4 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 5 (P3)**: Needs US4 (FeatureShowcase) for contextual education links

### Within Each User Story

- **US1**: T009 (HeroSection) → T010 (page.tsx update) → T011-T013 (enhancements)
- **US2**: T014-T017 (all [P] components in parallel) → T018-T020 (page.tsx updates) → T021-T022 (animations)
- **US3**: T023-T025 (CTAs) → T026 (verification) → T027 (end-of-page CTA)
- **US4**: T028-T030 (all [P] in parallel) → T031 (page.tsx) → T032-T033 (enhancements)
- **US5**: T034-T036 (all [P] in parallel) → T037-T039 (page.tsx updates + integration)

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004 can run in parallel

**Phase 2 (Foundational)**: T006, T007, T008 can run in parallel

**Phase 3 (US1)**: T009 is independent, can start immediately after Phase 2

**Phase 4 (US2)**: T014, T015, T016, T017 can all run in parallel (different files)

**Phase 6 (US4)**: T028, T029, T030 can run in parallel

**Phase 7 (US5)**: T034, T035, T036 can run in parallel

**Phase 8 (Polish)**:
- Performance: T040, T041, T042 can run in parallel
- Accessibility: T046, T047, T048 can run in parallel
- Testing: T051, T052, T053, T054 can run in parallel
- Documentation: T056, T058 can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all components for User Story 2 together:
Task: "Create MarketOverview component in frontend/src/components/home/MarketOverview.tsx"
Task: "Create HotStockList component in frontend/src/components/home/HotStockList.tsx"
Task: "Create HotStockRow component in frontend/src/components/home/HotStockRow.tsx"
Task: "Create CoreIndexCards component in frontend/src/components/home/CoreIndexCards.tsx"

# Once components are done, update page.tsx sequentially:
Task: "Add MarketOverview section to page.tsx"
Task: "Add HotStockList sections to page.tsx"
Task: "Add CoreIndexCards section to page.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (5 tasks, ~30 minutes)
2. Complete Phase 2: Foundational (3 tasks, ~1 hour)
3. Complete Phase 3: User Story 1 (5 tasks, ~2 hours)
4. Complete Phase 4: User Story 2 (9 tasks, ~4 hours)
5. **STOP and VALIDATE**: Test homepage independently
   - Verify value proposition is clear
   - Verify real-time data updates work
   - Run Lighthouse audit (target: LCP <3s)
6. Deploy/demo if ready (MVP = P1 stories only)

**MVP Delivery**: ~8 hours total for P1 stories

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~1.5 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (~2 hours)
3. Add User Story 2 → Test independently → Deploy/Demo (~4 hours)
4. Add User Story 3 → Test independently → Deploy/Demo (~2 hours)
5. Add User Story 4 → Test independently → Deploy/Demo (~3 hours)
6. Add User Story 5 → Test independently → Deploy/Demo (~2 hours)
7. Polish Phase → Optimize and test → Final Deploy (~5 hours)

**Total Delivery**: ~19.5 hours for all stories + polish

### Parallel Team Strategy

With 2-3 developers:

1. Team completes Setup + Foundational together (~1.5 hours)
2. Once Foundational is done:
   - **Developer A**: User Story 1 + User Story 3 (dependent on US1)
   - **Developer B**: User Story 2 (P1, largest story, parallel with US1)
   - **Developer C**: User Story 4 + User Story 5 (dependent on US4)
3. All developers merge and resolve conflicts
4. Team completes Polish phase together

**Parallel Delivery**: ~12-15 hours with 3 developers

---

## Task Summary

| Phase | Task Count | Estimated Time | Priority |
|-------|------------|----------------|----------|
| Phase 1: Setup | 5 tasks | 30 min | Required |
| Phase 2: Foundational | 3 tasks | 1 hour | Required (BLOCKS stories) |
| Phase 3: US1 (P1) | 5 tasks | 2 hours | MVP |
| Phase 4: US2 (P1) | 9 tasks | 4 hours | MVP |
| Phase 5: US3 (P2) | 5 tasks | 2 hours | Nice-to-have |
| Phase 6: US4 (P2) | 6 tasks | 3 hours | Nice-to-have |
| Phase 7: US5 (P3) | 6 tasks | 2 hours | Optional |
| Phase 8: Polish | 21 tasks | 5 hours | Quality |

**Total Tasks**: 60 tasks  
**Total Estimated Time**: 19.5 hours (sequential) or 12-15 hours (parallel with 3 devs)

**MVP Scope (Recommended)**: Phase 1-4 (US1 + US2 only) = 22 tasks, ~8 hours

**Parallel Opportunities**: 25 tasks marked [P] can run in parallel (42% of all tasks)

**Independent Test Criteria**: Each user story (Phase 3-7) has clear acceptance verification checklist

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability (US1-US5)
- Each user story is independently completable and testable
- Tests are added in Phase 8 (Polish) since spec.md does not explicitly request TDD
- All components follow contracts defined in `contracts/components.md`
- All data models follow structures in `data-model.md`
- Follow quickstart.md for detailed implementation guidance
- Stop at any checkpoint to validate story independently
- Commit after each task or logical group (e.g., after completing all [P] tasks in a phase)
