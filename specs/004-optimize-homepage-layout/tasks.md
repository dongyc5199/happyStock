# Tasks: 首页布局优化与整页滚动

**Feature**: 004-optimize-homepage-layout  
**Input**: Design documents from `/specs/004-optimize-homepage-layout/`  
**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ research.md, ✅ data-model.md, ✅ quickstart.md

**Tests**: E2E 测试包含在任务中，单元测试为可选项（按需添加）

**Organization**: 任务按用户故事分组，使每个故事能够独立实现和测试

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 任务所属的用户故事（如 US1, US2, US3）
- 描述中包含具体文件路径

---

## Phase 1: Setup (共享基础设施)

**目的**: 项目初始化和基础结构搭建

- [ ] T001 创建布局组件目录结构 `frontend/src/components/layout/`
- [ ] T002 [P] 创建类型定义文件 `frontend/src/types/layout.ts`
- [ ] T003 [P] 创建 Zustand store `frontend/src/stores/layoutPreferences.ts`
- [ ] T004 [P] 创建滚动工具函数文件 `frontend/src/lib/scroll-utils.ts`

**检查点**: 基础目录结构和核心文件已创建

---

## Phase 2: Foundational (阻塞性前置条件)

**目的**: 所有用户故事依赖的核心基础设施，必须在任何用户故事开始前完成

**⚠️ 关键**: 此阶段完成前，不能开始任何用户故事的实现

- [ ] T005 实现 `useReducedMotion` Hook 在 `frontend/src/hooks/useReducedMotion.ts` - 检测 prefers-reduced-motion 偏好
- [ ] T006 [P] 实现 `useSectionVisibility` Hook 在 `frontend/src/hooks/useSectionVisibility.ts` - 使用 Intersection Observer 检测区域可见性
- [ ] T007 [P] 配置 Zustand store 初始状态和 localStorage 持久化逻辑在 `frontend/src/stores/layoutPreferences.ts`
- [ ] T008 在 `frontend/src/types/layout.ts` 定义核心类型：PageSection, NavigationDot, LayoutPreferences, ScrollState

**检查点**: 基础设施就绪 - 用户故事实现可以开始并行进行

---

## Phase 3: User Story 1 - 快速浏览首页关键信息 (Priority: P1) 🎯 MVP

**目标**: 重新组织首页内容为清晰的功能区域，每个区域有明确的标题和视觉边界

**独立测试**: 用户访问首页后能在 5 秒内识别出所有主要功能区域，每个区域的标题和内容清晰可见

### 实现 User Story 1

- [ ] T009 [P] [US1] 创建 `PageSection` 组件在 `frontend/src/components/layout/PageSection.tsx` - 实现 Section 包裹器，包含标题、视觉边界、最小高度设置
- [ ] T010 [P] [US1] 在 `frontend/src/lib/scroll-utils.ts` 添加 `getSectionConfig()` 函数 - 定义所有首页区域配置数组
- [ ] T011 [US1] 重构 `frontend/src/app/page.tsx` - 将现有组件包裹在 PageSection 中，实现 FR-001~FR-004
- [ ] T012 [US1] 为每个区域添加视觉边界样式 - 使用 Tailwind CSS 实现背景色变化、分隔线或留白（FR-003）
- [ ] T013 [US1] 确保首屏展示最重要的 3 个区域 - Hero, MarketOverview, CoreIndexCards（FR-004）
- [ ] T014 [US1] 响应式布局优化 - 验证桌面端（≥1024px）、平板端（768-1023px）、移动端（<768px）布局（FR-015）

**检查点**: 首页内容已重新组织为清晰的区域结构，视觉边界明确，响应式布局工作正常

---

## Phase 4: User Story 2 - 使用整页滚动快速导航 (Priority: P1) 🎯 MVP

**目标**: 实现整页滚动模式，用户滚动时自动对齐到内容区域边界，配合导航点快速定位

**独立测试**: 用户使用鼠标滚轮、键盘或触摸手势滚动时，页面自动对齐到最近的内容区域边界

### 实现 User Story 2 - 基础滚动

- [ ] T015 [US2] 在 `frontend/src/app/page.tsx` 或 `layout.tsx` 添加 CSS scroll-snap 配置 - 实现 `scroll-snap-type: y mandatory/proximity`（FR-005）
- [ ] T016 [US2] 为每个 PageSection 添加 scroll-snap-align 属性 - 确保对齐到区域顶部
- [ ] T017 [US2] 实现 `useScrollSnap` Hook 在 `frontend/src/hooks/useScrollSnap.ts` - 处理键盘导航、滚动状态管理（FR-006, FR-010）
- [ ] T018 [US2] 在 `frontend/src/lib/scroll-utils.ts` 添加滚动计算函数 - `calculateScrollTarget()`, `isSlowScroll()` 等

### 实现 User Story 2 - 导航点

- [ ] T019 [P] [US2] 创建 `SectionNavigationDots` 组件在 `frontend/src/components/layout/SectionNavigationDots.tsx` - 显示导航点，响应点击跳转（FR-007）
- [ ] T020 [US2] 集成导航点到 `frontend/src/app/page.tsx` - 桌面端右侧，移动端底部，实时高亮当前区域
- [ ] T021 [US2] 实现导航点 ARIA 属性 - `role="navigation"`, `aria-label`, `aria-current`（FR-021）

### 实现 User Story 2 - 滚动模式切换

- [ ] T022 [P] [US2] 创建 `ScrollSettingsToggle` 组件在 `frontend/src/components/layout/ScrollSettingsToggle.tsx` - 允许用户禁用整页滚动（FR-009）
- [ ] T023 [US2] 在 Zustand store 添加 `toggleScrollSnap()` action - 切换滚动模式并保存到 localStorage
- [ ] T024 [US2] 实现滚动模式切换逻辑 - 动态添加/移除 scroll-snap CSS 类

### 实现 User Story 2 - 性能和可访问性

- [ ] T025 [US2] 优化滚动性能 - 使用 throttle/debounce，确保 60fps（FR-018）
- [ ] T026 [US2] 实现 prefers-reduced-motion 支持 - 禁用动画或使用瞬时跳转（FR-023）
- [ ] T027 [US2] 添加屏幕阅读器支持 - ARIA live region 宣布区域切换（FR-020）

**检查点**: 整页滚动功能完整实现，导航点工作正常，性能达标 60fps，可访问性符合要求

---

## Phase 5: User Story 3 - 折叠和展开次要内容 (Priority: P2)

**目标**: 允许用户折叠次要内容区域，状态持久化到本地存储

**独立测试**: 用户可以点击按钮折叠或展开指定的内容区域，折叠状态在页面刷新后保持

### 实现 User Story 3

- [ ] T028 [P] [US3] 创建 `CollapsibleSection` 组件在 `frontend/src/components/layout/CollapsibleSection.tsx` - 包裹可折叠区域（FR-011）
- [ ] T029 [P] [US3] 实现 `useCollapsibleState` Hook 在 `frontend/src/hooks/useCollapsibleState.ts` - 管理折叠状态 + localStorage 持久化（FR-012）
- [ ] T030 [US3] 在 Zustand store 添加 `toggleSection()` action - 切换区域折叠状态
- [ ] T031 [US3] 实现折叠/展开动画 - 使用 CSS `max-height` + `transition`，避免布局抖动（FR-013）
- [ ] T032 [US3] 为折叠区域添加预览或说明 - 标题栏显示简要信息（FR-014）
- [ ] T033 [US3] 集成 CollapsibleSection 到 `page.tsx` - 包裹 QuickStartGuide, FeatureShowcase, EducationFooter
- [ ] T034 [US3] 实现折叠动画期间禁用整页滚动 - 设置 `isAnimating` 状态，暂停 scroll-snap
- [ ] T035 [US3] 添加折叠按钮 ARIA 属性 - `aria-expanded`, `aria-controls`（FR-022）

**检查点**: 折叠功能完整实现，状态正确持久化，动画流畅无卡顿，与整页滚动无冲突

---

## Phase 6: User Story 4 - 自定义首页区域顺序 (Priority: P3) ⚠️ 可选

**目标**: 高级用户可通过拖拽调整区域顺序，保存后下次访问保持自定义顺序

**独立测试**: 用户可以进入编辑模式，通过拖拽重新排列区域顺序，保存后下次访问保持自定义顺序

**注意**: 此用户故事为 P3 优先级，可根据时间和资源决定是否实现

### 实现 User Story 4（如果实现）

- [ ] T036 [P] [US4] 创建 `DraggableSection` 组件在 `frontend/src/components/layout/DraggableSection.tsx` - 包裹可拖拽区域
- [ ] T037 [P] [US4] 实现 `useSectionOrder` Hook 在 `frontend/src/hooks/useSectionOrder.ts` - 管理区域顺序
- [ ] T038 [US4] 在 Zustand store 添加 `reorderSections()` action - 保存自定义顺序到 localStorage
- [ ] T039 [US4] 集成拖拽库（如 @dnd-kit/core） - 添加到 package.json 并配置
- [ ] T040 [US4] 实现编辑模式切换 - "自定义布局"按钮，显示/隐藏拖拽手柄
- [ ] T041 [US4] 实现拖拽逻辑 - 拖拽时其他区域自动调整位置
- [ ] T042 [US4] 实现保存和取消按钮 - 保存时更新顺序并退出编辑模式
- [ ] T043 [US4] 实现"恢复默认"按钮 - 重置顺序为系统默认，清除 localStorage
- [ ] T044 [US4] 添加拖拽可访问性支持 - 键盘拖拽（@dnd-kit 内置支持）

**检查点**: 拖拽重排功能完整实现，状态正确持久化，可访问性良好

---

## Phase 7: E2E 测试（集成测试）

**目的**: 验证所有用户故事的端到端流程

- [ ] T045 [P] 创建整页滚动 E2E 测试 `frontend/tests/e2e/scroll-navigation.spec.ts` - 测试鼠标滚轮、键盘、导航点跳转
- [ ] T046 [P] 创建折叠功能 E2E 测试 `frontend/tests/e2e/collapsible-sections.spec.ts` - 测试折叠/展开、状态持久化
- [ ] T047 [P] 创建响应式布局 E2E 测试 `frontend/tests/e2e/responsive-layout.spec.ts` - 测试桌面端、平板端、移动端布局

**检查点**: 所有 E2E 测试通过，用户故事端到端验证通过

---

## Phase 8: Polish & Cross-Cutting Concerns

**目的**: 影响多个用户故事的优化和改进

### 性能优化

- [ ] T048 [P] 使用 Chrome DevTools Performance 测试滚动性能 - 验证 60fps 目标（FR-018, SC-004）
- [ ] T049 [P] 运行 Lighthouse 审计 - 验证首屏加载时间 ≤110% baseline（FR-019, SC-002）
- [ ] T050 优化 Zustand store 性能 - 使用 batch 更新，debounce localStorage 写入
- [ ] T051 [P] 优化 Intersection Observer - 使用单个 Observer 观察所有区域

### 可访问性完善

- [ ] T052 [P] 运行 axe DevTools 扫描 - 验证 WCAG 2.1 AA 合规性（SC-010）
- [ ] T053 [P] 测试键盘导航完整性 - Tab 键遍历所有交互元素（FR-022）
- [ ] T054 [P] 测试屏幕阅读器兼容性 - 使用 NVDA/JAWS/VoiceOver 验证（FR-020）

### 浏览器兼容性

- [ ] T055 [P] 测试 Chrome、Firefox、Safari、Edge 最新 2 版本 - 验证功能完整可用（SC-009）
- [ ] T056 [P] 测试 CSS scroll-snap 降级方案 - 不支持的浏览器使用标准滚动
- [ ] T057 测试 JavaScript 禁用降级 - 页面仍可滚动和阅读

### 移动端优化

- [ ] T058 [P] 测试触摸手势滚动 - 真实设备测试，验证响应时间 <100ms（FR-016, SC-005）
- [ ] T059 [P] 优化移动端导航点 - 确保点击区域 ≥44x44px，位置合理

### 文档和验证

- [ ] T060 [P] 更新 quickstart.md - 添加新功能的测试场景
- [ ] T061 执行 quickstart.md 完整验证 - 测试所有 8 个场景，40+ 测试用例
- [ ] T062 [P] 更新 README.md - 添加布局优化功能的使用说明
- [ ] T063 [P] 添加代码注释和 JSDoc - 确保所有 Hooks 和组件有文档

**检查点**: 所有优化完成，性能达标，可访问性合规，跨浏览器测试通过

---

## Dependencies & Execution Order

### 阶段依赖

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 - 阻塞所有用户故事
- **User Stories (Phase 3-6)**: 全部依赖 Foundational 阶段完成
  - 用户故事可以并行进行（如果有多人协作）
  - 或按优先级顺序执行（P1 → P2 → P3）
- **E2E Tests (Phase 7)**: 依赖对应用户故事完成
- **Polish (Phase 8)**: 依赖所有期望的用户故事完成

### 用户故事依赖

- **User Story 1 (P1)**: 可在 Foundational (Phase 2) 后开始 - 无其他故事依赖
- **User Story 2 (P1)**: 可在 Foundational (Phase 2) 后开始 - 依赖 US1 的 PageSection 组件
- **User Story 3 (P2)**: 可在 Foundational (Phase 2) 后开始 - 依赖 US1 的 PageSection 和 US2 的滚动逻辑
- **User Story 4 (P3)**: 可在 Foundational (Phase 2) 后开始 - 依赖 US1 的 PageSection

### 每个用户故事内部

- US1: 创建组件 → 重构 page.tsx → 样式优化 → 响应式验证
- US2: CSS scroll-snap → useScrollSnap Hook → 导航点组件 → 集成 → 性能优化
- US3: CollapsibleSection 组件 → useCollapsibleState Hook → 动画 → 集成 → 冲突处理
- US4: DraggableSection 组件 → useSectionOrder Hook → 拖拽集成 → 保存/恢复

### 并行机会

- Phase 1 所有标记 [P] 的任务可并行
- Phase 2 所有标记 [P] 的任务可并行
- Phase 2 完成后，US1-US4 可由不同开发者并行实现（如团队资源允许）
- 每个用户故事内，标记 [P] 的任务可并行（不同文件，无依赖）
- Phase 7 E2E 测试可并行编写和执行
- Phase 8 大部分任务可并行执行

---

## Parallel Example: User Story 2

```bash
# 并行启动 US2 的基础组件创建:
Task T019: "创建 SectionNavigationDots 组件"
Task T022: "创建 ScrollSettingsToggle 组件"

# 并行执行性能和可访问性优化:
Task T025: "优化滚动性能"
Task T026: "实现 prefers-reduced-motion 支持"
Task T027: "添加屏幕阅读器支持"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（关键 - 阻塞所有故事）
3. 完成 Phase 3: User Story 1（内容组织）
4. 完成 Phase 4: User Story 2（整页滚动）
5. **停止并验证**: 测试 US1 + US2 独立工作
6. 如果就绪，部署/演示 MVP

### Incremental Delivery

1. 完成 Setup + Foundational → 基础就绪
2. 添加 User Story 1 → 独立测试 → 部署/演示（内容组织 MVP）
3. 添加 User Story 2 → 独立测试 → 部署/演示（完整滚动体验）
4. 添加 User Story 3 → 独立测试 → 部署/演示（折叠功能）
5. 添加 User Story 4 → 独立测试 → 部署/演示（高级定制）
6. 每个故事增加价值而不破坏之前的故事

### Parallel Team Strategy

多开发者协作：

1. 团队一起完成 Setup + Foundational
2. Foundational 完成后：
   - 开发者 A: User Story 1（内容组织）
   - 开发者 B: User Story 2（整页滚动）
   - 开发者 C: User Story 3（折叠功能）
3. 故事独立完成并集成

---

## Task Summary

- **Total Tasks**: 63
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US1-P1)**: 6 tasks
- **Phase 4 (US2-P1)**: 13 tasks
- **Phase 5 (US3-P2)**: 8 tasks
- **Phase 6 (US4-P3)**: 9 tasks（可选）
- **Phase 7 (E2E Tests)**: 3 tasks
- **Phase 8 (Polish)**: 16 tasks

**MVP Scope** (建议): Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) = **27 tasks**

**Parallel Opportunities**: 
- Setup: 3 tasks 可并行
- Foundational: 2 tasks 可并行
- US1: 2 tasks 可并行
- US2: 4 tasks 可并行
- US3: 2 tasks 可并行
- US4: 2 tasks 可并行
- E2E: 3 tasks 可并行
- Polish: 11 tasks 可并行

**Total Parallel Opportunities**: ~29 tasks (46% of total)

---

## Notes

- [P] 标记的任务 = 不同文件，无依赖，可并行
- [Story] 标签将任务映射到特定用户故事，便于追踪
- 每个用户故事应该独立完成和测试
- 在每个检查点停止以独立验证故事
- 每个任务或逻辑组完成后提交代码
- 避免：模糊任务、同文件冲突、破坏故事独立性的跨故事依赖

---

**Generated**: 2025-10-30  
**Version**: 1.0  
**Status**: Ready for Implementation
