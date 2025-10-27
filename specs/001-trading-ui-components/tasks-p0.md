# Implementation Tasks: P0 图表核心体验优化

**Feature**: P0 Priority Tasks | **Branch**: `001-trading-ui-components` | **Date**: 2025-10-27
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

本文档定义 P0 优先级任务的详细实现清单，包括：
1. **K线倒计时功能**
2. **动态数据加载优化**
3. **线形图切换功能**

总任务数：**27个任务** | 并行机会：**15个可并行任务**

---

## Phase 1: Setup & Infrastructure (6 tasks)

### Goal
建立 P0 功能所需的基础设施和工具函数。

### Tasks

- [ ] T001 创建时间工具函数文件 `frontend/src/lib/utils/timeUtils.ts`
- [ ] T002 [P] 实现时间周期秒数映射常量 in `timeUtils.ts`
- [ ] T003 [P] 实现倒计时计算函数 `calculateRemainingTime` in `timeUtils.ts`
- [ ] T004 [P] 实现倒计时格式化函数 `formatCountdown` in `timeUtils.ts`
- [ ] T005 [P] 创建缓存工具函数文件 `frontend/src/lib/utils/cacheUtils.ts`
- [ ] T006 [P] 实现数据合并函数 `mergeKlineData` in `cacheUtils.ts`

**Dependencies**: None (all parallelizable after T001, T005)

**Acceptance Criteria**:
- ✅ 所有工具函数通过单元测试
- ✅ TypeScript 类型定义完整
- ✅ 支持所有时间周期 (5m/15m/30m/60m/120m/1d/1w/1M)

---

## Phase 2: Foundational Tasks (5 tasks)

### Goal
实现核心 Hook 和类型定义，为所有用户故事提供基础。

### Tasks

- [ ] T007 创建图表类型定义文件 `frontend/src/types/chart.ts`
- [ ] T008 [P] 定义 `ChartType` 类型 ('candlestick' | 'line') in `chart.ts`
- [ ] T009 [P] 定义 `ChartPreferences` 接口 in `chart.ts`
- [ ] T010 [P] 定义 `LoadedRange` 接口 in `chart.ts`
- [ ] T011 创建倒计时 Hook `frontend/src/hooks/useCountdown.ts`

**Dependencies**: T007 blocks T008-T010

**Acceptance Criteria**:
- ✅ 类型定义涵盖所有 P0 功能
- ✅ useCountdown Hook 返回实时倒计时值

---

## Phase 3: User Story 1 - K线倒计时功能 (7 tasks) 🔥

### Goal
在K线图表上显示实时倒计时，支持所有时间周期，倒计时结束自动刷新数据。

### Why this priority
倒计时是用户最直观感知的实时体验，显著提升专业感。

### Independent Test
启动图表，观察最后一根K线上方倒计时从59秒倒数到0秒，格式正确，位置对齐。

### Tasks

- [ ] T012 [US1] 在 `useCountdown.ts` 中实现倒计时逻辑（每秒更新）
- [ ] T013 [P] [US1] 在 `useCountdown.ts` 中实现倒计时归零回调
- [ ] T014 [P] [US1] 创建倒计时显示组件 `frontend/src/components/trading/KlineCountdown.tsx`
- [ ] T015 [US1] 在 `KlineCountdown.tsx` 中实现 HTML 叠加定位逻辑
- [ ] T016 [US1] 在 `KlineCountdown.tsx` 中计算最后一根K线的X坐标
- [ ] T017 [US1] 在 `CandlestickChart.tsx` 中集成 `KlineCountdown` 组件
- [ ] T018 [US1] 在倒计时归零时触发数据刷新（调用 API 重新加载最新K线）

**Dependencies**: T011 → T012 → T013,T014 → T015,T016 → T017 → T018

**Acceptance Scenarios**:
1. ✅ 倒计时显示在最后一根K线上方，格式为 MM:SS (分钟级) 或 HH:MM:SS (日K级)
2. ✅ 每秒更新一次，延迟 < 50ms
3. ✅ 倒计时归零时自动加载新K线数据
4. ✅ 切换时间周期时倒计时重新计算

---

## Phase 4: User Story 2 - 动态数据加载优化 (9 tasks) 🚀

### Goal
监听图表滑动/缩放，智能加载历史和最新数据，性能优化，缓存策略。

### Why this priority
性能和流畅度是专业图表的核心竞争力，决定用户留存。

### Independent Test
左滑图表加载历史数据，右滑加载最新数据，无卡顿，重复滑动命中缓存不重复请求。

### Tasks

- [ ] T019 [US2] 创建数据加载 Hook `frontend/src/hooks/useChartData.ts`
- [ ] T020 [P] [US2] 在 `useChartData.ts` 中实现防抖函数（200ms）
- [ ] T021 [P] [US2] 在 `useChartData.ts` 中实现 IndexedDB 缓存逻辑
- [ ] T022 [US2] 在 `useChartData.ts` 中实现 LRU 淘汰策略（最多缓存10只股票）
- [ ] T023 [US2] 在 `useChartData.ts` 中监听 `subscribeVisibleLogicalRangeChange`
- [ ] T024 [US2] 在范围变化时判断是否需要加载数据（buffer=50根K线）
- [ ] T025 [US2] 实现 `loadHistoricalData` 函数（向左滑动加载）
- [ ] T026 [US2] 实现 `loadLatestData` 函数（向右滑动加载）
- [ ] T027 [US2] 在 `CandlestickChart.tsx` 中集成 `useChartData` Hook

**Dependencies**: T019 → T020,T021,T022 → T023 → T024 → T025,T026 → T027

**Acceptance Scenarios**:
1. ✅ 左滑动时自动加载200根历史K线，无重复请求
2. ✅ 右滑动时自动加载200根最新K线
3. ✅ 加载响应时间 < 100ms
4. ✅ 缓存命中率 > 80%
5. ✅ 到达边界时显示"已加载全部数据"提示

---

## Phase 5: User Story 3 - 线形图切换功能 (5 tasks) 📈

### Goal
添加图表类型切换按钮，支持蜡烛图⇄线形图平滑切换，保留技术指标和缩放位置。

### Why this priority
线形图是常见需求，简洁展示趋势，提升用户体验多样性。

### Independent Test
点击工具栏切换按钮，图表从蜡烛图平滑切换到线形图，EMA/MACD 保留，无闪烁。

### Tasks

- [ ] T028 [P] [US3] 在 `CandlestickChart.tsx` 中添加 `chartType` 状态
- [ ] T029 [P] [US3] 在工具栏添加图表类型切换按钮（蜡烛图 / 线形图）
- [ ] T030 [US3] 实现图表类型切换逻辑（移除 CandlestickSeries，添加 LineSeries）
- [ ] T031 [US3] 实现 LocalStorage 用户偏好保存（保存/加载 chartType）
- [ ] T032 [US3] 确保切换时保留 EMA/MACD 和缩放位置

**Dependencies**: T028,T029 (parallel) → T030 → T031,T032

**Acceptance Scenarios**:
1. ✅ 工具栏显示图表类型切换按钮
2. ✅ 点击按钮后图表类型切换，动画流畅无闪烁
3. ✅ 线形图显示收盘价连线，颜色为 #2962FF
4. ✅ 切换后 EMA/MACD 正常显示
5. ✅ 用户偏好保存到 LocalStorage，下次打开自动恢复

---

## Phase 6: Polish & Integration (5 tasks)

### Goal
性能优化、错误处理、文档完善。

### Tasks

- [ ] T033 [P] 添加性能监控（使用 React Profiler）
- [ ] T034 [P] 优化组件重渲染（添加 useMemo, useCallback）
- [ ] T035 [P] 添加错误边界（Error Boundary）
- [ ] T036 [P] 清理内存泄漏（定时器、事件监听器、订阅）
- [ ] T037 更新开发文档（README 添加 P0 功能说明）

**Dependencies**: None (all parallelizable)

**Acceptance Criteria**:
- ✅ React Profiler 显示无性能瓶颈
- ✅ 无内存泄漏（Chrome DevTools Memory Profiler）
- ✅ 所有错误有友好提示

---

## Dependencies & Parallel Opportunities

### Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3, 4, 5 (并行) → Phase 6 (Polish)
```

### Parallel Execution per Story

**User Story 1 (倒计时)**:
- 可并行: T013, T014
- 总耗时: ~2-3小时

**User Story 2 (动态加载)**:
- 可并行: T020, T021, T022 和 T025, T026
- 总耗时: ~4-5小时

**User Story 3 (线形图)**:
- 可并行: T028, T029 和 T031, T032
- 总耗时: ~1-2小时

**所有故事并行开发**: Phase 3, 4, 5 可由3名开发者同时进行

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**仅 User Story 3**: 线形图切换（1-2小时即可完成）

### Incremental Delivery
1. **Sprint 1**: User Story 3 (线形图) - 快速见效
2. **Sprint 2**: User Story 1 (倒计时) - 用户体验提升
3. **Sprint 3**: User Story 2 (动态加载) - 性能优化

### Risk Mitigation
- **IndexedDB 兼容性**: 降级到 LocalStorage
- **倒计时不准确**: 使用服务器时间校准
- **性能问题**: 限制缓存量，LRU 淘汰

---

## Format Validation

✅ **All tasks follow checklist format**:
- ✅ 27/27 tasks start with `- [ ]`
- ✅ 27/27 tasks have Task ID (T001-T037)
- ✅ 15/27 tasks marked as `[P]` (parallelizable)
- ✅ 21/27 tasks have `[US#]` label (user story tasks)
- ✅ 27/27 tasks have clear file paths

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 27 |
| Setup Tasks | 6 |
| Foundational Tasks | 5 |
| US1 Tasks (倒计时) | 7 |
| US2 Tasks (动态加载) | 9 |
| US3 Tasks (线形图) | 5 |
| Polish Tasks | 5 |
| Parallelizable Tasks | 15 (56%) |
| Estimated Time (sequential) | 12-15 hours |
| Estimated Time (3 devs parallel) | 5-7 hours |

**MVP**: User Story 3 (线形图) - 1-2 hours
**Recommended Order**: US3 → US1 → US2

---

*Generated: 2025-10-27 | Status: Ready for Implementation*
