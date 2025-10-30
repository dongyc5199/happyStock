# Implementation Plan: 首页布局优化与整页滚动

**Branch**: `004-optimize-homepage-layout` | **Date**: 2025-10-30 | **Spec**: [spec.md](./spec.md)  
**Status**: ✅ Phase 0 Complete | ✅ Phase 1 Complete | Phase 2 Pending (`/speckit.tasks`)  
**Input**: Feature specification from `/specs/004-optimize-homepage-layout/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

优化首页布局以改善内容组织和导航体验，通过以下方式提升用户浏览效率：

1. **内容归类与聚合**：将现有首页内容（价值主张、市场数据、功能展示、快速开始、教育资源等）重新组织为清晰的功能区域，每个区域有明确的标题和视觉边界
2. **整页滚动导航**：实现全屏滚动模式，用户滚动时自动对齐到内容区域边界，配合侧边导航点快速定位
3. **折叠展开控制**：允许用户折叠次要内容区域，状态持久化到本地存储
4. **自定义布局顺序**（可选）：高级用户可拖拽调整区域顺序

技术方法：基于现有 Next.js 15 + React 19 架构，使用 Intersection Observer API 检测区域可见性，CSS scroll-snap 或自研整页滚动实现，Framer Motion 处理动画，localStorage 持久化用户偏好。纯前端实现，无需后端修改。

## Technical Context

**Language/Version**: 
- Frontend: TypeScript 5.0+, JavaScript ES2022
- Backend: N/A (纯前端特性，无需后端修改)

**Primary Dependencies**: 
- Frontend Core: Next.js 15.4.6, React 19.1.0, React DOM 19.1.0
- Styling: Tailwind CSS v4 (PostCSS)
- Animation: NEEDS CLARIFICATION (选项：Framer Motion vs CSS Animations vs 自研)
- Scroll Library: NEEDS CLARIFICATION (选项：CSS scroll-snap vs fullPage.js vs react-fullpage vs 自研)
- Drag & Drop: NEEDS CLARIFICATION (仅用于 US4-P3，可延后决定)
- Icons: Lucide React 0.548+
- State Management: Zustand 5.0.8 (用户偏好)
- Utilities: clsx 2.1.1, tailwind-merge 3.3.1

**Storage**: 
- LocalStorage (用户偏好：折叠状态、区域顺序、整页滚动开关)
- 无后端存储需求

**Testing**: 
- Unit Tests: Jest + React Testing Library
- Component Tests: Storybook (可选)
- E2E Tests: Playwright (验证滚动行为、折叠状态持久化)
- Performance Tests: Chrome DevTools Performance Profiler (验证 60fps 滚动)
- Accessibility Tests: axe-core (验证 WCAG 2.1 AA)

**Target Platform**: 
- Web (响应式设计)
- 桌面端：≥1024px (Chrome 90+, Edge 90+, Safari 14+, Firefox 88+)
- 平板端：768-1023px
- 移动端：<768px (触摸手势支持)

**Project Type**: Web application (frontend-focused, single-page optimization)

**Performance Goals**: 
- 滚动性能：60fps (16.67ms/frame)
- 触摸响应：<100ms (移动端)
- 动画持续时间：600-1000ms (平滑感)
- 首屏加载时间：保持现有水平 (不超过 110% baseline)
- 内容识别时间：<5秒 (用户能识别所有主要区域)

**Constraints**: 
- 响应时间：<200ms for user interactions
- 无布局抖动 (Layout Shift)
- 支持 prefers-reduced-motion (可访问性)
- 兼容现有 WebSocket 实时更新 (不能阻塞数据流)
- 降级体验：JavaScript 禁用时页面仍可滚动和阅读

**Scale/Scope**: 
- 单页面优化：首页 `/`
- 内容区域数量：5-10 个
- 新增组件：5-8 个 (Section Wrapper, Navigation Dots, Collapsible Section, Scroll Controller, Settings Toggle)
- 修改组件：1 个 (page.tsx - 重新组织现有内容)
- 代码行数估算：~800-1200 LOC
- 本地存储数据：<10KB (用户偏好 JSON)
- 预期用户：100-1000 DAU (初期)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Evaluation**: Constitution file contains template placeholders only. Using generic quality gates for this evaluation.

**Gate Analysis**:
- **Gate 0 (Necessity)**: ✅ PASS
  - Feature addresses real user pain point: 首页内容过多导致信息混乱
  - Aligns with platform evolution: Feature 003 添加了大量内容，现在需要优化组织方式
  - Clear user value: 提升浏览效率，降低跳出率 20%
  
- **Gate 1 (Simplicity)**: ✅ PASS
  - 纯前端实现，无后端 API 修改
  - 复用现有组件架构 (Next.js app router, Tailwind CSS)
  - 渐进式实现：P1 stories 可独立交付价值，P2/P3 可选
  - 技术选型简单：优先考虑 CSS scroll-snap (原生) vs 轻量库
  
- **Gate 2 (Testability)**: ✅ PASS  
  - 每个 User Story 独立可测试 (4 个故事各自独立)
  - 明确的成功标准 (60fps, 5秒识别, 90%完成率)
  - E2E 测试覆盖：滚动行为、状态持久化、响应式布局
  - 性能可量化：Chrome DevTools Performance 测量帧率
  
- **Gate 3 (Maintainability)**: ✅ PASS
  - 模块化组件设计 (Section Wrapper, Navigation Dots)
  - 清晰的关注点分离：布局逻辑 vs 内容组件
  - 配置驱动：区域定义可提取为配置数组
  - 文档完善：spec.md 定义了 23 个需求和 9 个边缘案例
  
- **Gate 4 (Security)**: ✅ LOW RISK
  - 纯客户端状态管理 (localStorage)
  - 无用户输入验证需求 (只读配置)
  - XSS 风险低：仅渲染现有组件，无动态 HTML 注入
  
- **Gate 5 (Performance)**: ⚠️ REQUIRES ATTENTION
  - 性能目标明确：60fps 滚动，<100ms 触摸响应
  - 风险点：
    - 滚动监听器可能导致性能问题 → 需使用 Intersection Observer + throttle
    - 动画库选择影响 bundle size → 优先考虑 CSS Animations
    - 折叠动画可能导致布局抖动 → 需使用 transform 而非 height 动画
  - 缓解措施：
    - Phase 0 research 必须评估不同滚动实现的性能
    - 使用 requestAnimationFrame 优化滚动事件处理
    - Lighthouse 测试验证性能回归

**Gate Status**: ✅ APPROVED for Phase 0 (requires performance research focus)

## Project Structure

### Documentation (this feature)

```text
specs/004-optimize-homepage-layout/
├── plan.md              # ✅ This file (/speckit.plan command output)
├── research.md          # ⏳ Phase 0 output (next)
├── data-model.md        # ⏳ Phase 1 output
├── quickstart.md        # ⏳ Phase 1 output
├── contracts/           # N/A (纯前端特性，无 API contracts)
├── checklists/
│   └── requirements.md  # ✅ Already created (quality validation)
└── tasks.md             # ⏳ Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                         # 🔧 PRIMARY - 重新组织为 Section 结构
│   │   └── layout.tsx                       # 🔧 可能需要修改 (全局滚动设置)
│   ├── components/
│   │   ├── home/                            # 🔧 EXISTING - 现有首页组件
│   │   │   ├── HeroSection.tsx              # ✅ 保持不变
│   │   │   ├── MarketOverview.tsx           # ✅ 保持不变
│   │   │   ├── CoreIndexCards.tsx           # ✅ 保持不变
│   │   │   ├── HotStockList.tsx             # ✅ 保持不变
│   │   │   ├── FeatureShowcase.tsx          # ✅ 保持不变
│   │   │   ├── QuickStartGuide.tsx          # ✅ 保持不变
│   │   │   ├── EducationFooter.tsx          # ✅ 保持不变
│   │   │   └── WebSocketErrorWrapper.tsx    # ✅ 保持不变
│   │   ├── layout/                          # 🆕 NEW - 布局相关组件
│   │   │   ├── PageSection.tsx              # 🆕 Section 包裹器 (FR-001~004)
│   │   │   ├── SectionNavigationDots.tsx    # 🆕 侧边导航点 (FR-007)
│   │   │   ├── CollapsibleSection.tsx       # 🆕 可折叠区域 (FR-011~014)
│   │   │   ├── ScrollController.tsx         # 🆕 整页滚动逻辑 (FR-005~010)
│   │   │   ├── ScrollSettingsToggle.tsx     # 🆕 滚动模式切换开关 (FR-009)
│   │   │   └── DraggableSection.tsx         # 🆕 可拖拽区域 (US4-P3, 可延后)
│   │   └── ui/                              # 🔧 EXISTING - 共享 UI 组件
│   │       ├── ErrorBoundary.tsx            # ✅ 保持不变
│   │       └── Skeleton.tsx                 # ✅ 保持不变
│   ├── hooks/
│   │   ├── useScrollSnap.ts                 # 🆕 NEW - 整页滚动逻辑封装
│   │   ├── useSectionVisibility.ts          # 🆕 NEW - Intersection Observer 封装
│   │   ├── useCollapsibleState.ts           # 🆕 NEW - 折叠状态管理 + localStorage
│   │   ├── useSectionOrder.ts               # 🆕 NEW - 区域顺序管理 (US4-P3)
│   │   └── useReducedMotion.ts              # 🆕 NEW - prefers-reduced-motion 检测
│   ├── lib/
│   │   └── scroll-utils.ts                  # 🆕 NEW - 滚动工具函数 (计算对齐位置等)
│   ├── stores/
│   │   └── layoutPreferences.ts             # 🆕 NEW - Zustand store (用户布局偏好)
│   └── types/
│       └── layout.ts                        # 🆕 NEW - 布局相关类型定义
└── tests/
    ├── e2e/
    │   ├── scroll-navigation.spec.ts        # 🆕 NEW - 整页滚动 E2E 测试
    │   ├── collapsible-sections.spec.ts     # 🆕 NEW - 折叠功能 E2E 测试
    │   └── responsive-layout.spec.ts        # 🆕 NEW - 响应式布局测试
    └── unit/
        ├── hooks/
        │   ├── useScrollSnap.test.ts        # 🆕 NEW
        │   └── useCollapsibleState.test.ts  # 🆕 NEW
        └── components/
            └── layout/
                ├── PageSection.test.tsx     # 🆕 NEW
                └── ScrollController.test.tsx # 🆕 NEW
```

**Structure Decision**: 

采用 Web application 结构，专注于 frontend 目录。主要变更：

1. **新增 `components/layout/` 目录**：集中管理布局相关组件，与内容组件 (`components/home/`) 分离
2. **新增 `hooks/` 目录**：封装滚动、可见性、折叠状态等逻辑，便于复用和测试
3. **新增 `stores/layoutPreferences.ts`**：使用 Zustand 管理用户布局偏好（折叠状态、区域顺序）
4. **修改 `app/page.tsx`**：重构为基于 Section 的结构，不改变现有内容组件
5. **保持现有组件不变**：HeroSection, MarketOverview 等组件无需修改，仅被 PageSection 包裹

这种结构确保：
- ✅ 关注点分离：布局逻辑 vs 内容逻辑
- ✅ 可测试性：Hooks 和组件独立测试
- ✅ 可维护性：未来添加新区域只需配置，无需修改核心逻辑
- ✅ 向后兼容：不破坏现有 Feature 003 的组件

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: ✅ No violations found

所有 Constitution Gates 均通过，无需复杂性豁免。
