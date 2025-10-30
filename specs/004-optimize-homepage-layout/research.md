# Research: 首页布局优化与整页滚动

**Feature**: 004-optimize-homepage-layout  
**Date**: 2025-10-30  
**Status**: Phase 0 - Research & Technology Selection

## Research Tasks

基于 Technical Context 中的 "NEEDS CLARIFICATION" 项，需要研究以下技术选型：

1. **动画库选择** (Animation Library)
2. **滚动实现方案** (Scroll Implementation)
3. **拖拽库选择** (Drag & Drop - 可延后)

## Research Findings

### 1. 动画库选择 (Animation Library)

**研究任务**: 为折叠/展开动画选择最佳实现方式

#### 选项对比

| 方案 | Bundle Size | 性能 | 学习曲线 | 灵活性 | 项目现状 |
|------|------------|------|---------|--------|---------|
| **CSS Animations** | 0 KB | ⭐⭐⭐⭐⭐ (GPU 加速) | ⭐⭐⭐⭐ (简单) | ⭐⭐ (有限) | ✅ 已使用 Tailwind |
| **Framer Motion** | ~60 KB gzip | ⭐⭐⭐⭐ (优化良好) | ⭐⭐⭐ (中等) | ⭐⭐⭐⭐⭐ (强大) | ❌ 未安装 |
| **React Spring** | ~25 KB gzip | ⭐⭐⭐⭐ (基于 physics) | ⭐⭐ (复杂) | ⭐⭐⭐⭐ (强大) | ❌ 未安装 |
| **GSAP** | ~50 KB gzip | ⭐⭐⭐⭐⭐ (业界标准) | ⭐⭐⭐ (中等) | ⭐⭐⭐⭐⭐ (最强) | ❌ 未安装，商业许可 |

#### 决策: **CSS Animations (Primary) + Framer Motion (Optional Enhancement)**

**Rationale**:
1. **零 Bundle 增长**: CSS Animations 原生支持，无需额外依赖
2. **性能最优**: GPU 加速的 transform/opacity 动画可轻松达到 60fps
3. **Tailwind 集成**: 项目已使用 Tailwind CSS，可直接使用 `transition-*` 和 `animate-*` 工具类
4. **渐进增强**: 基础动画用 CSS，复杂交互（如拖拽重排）可按需引入 Framer Motion
5. **prefers-reduced-motion**: CSS 媒体查询天然支持可访问性需求

**实现策略**:
```css
/* 折叠/展开动画 - 使用 max-height + transform */
.section-content {
  max-height: 1000px; /* 大于实际内容高度 */
  overflow: hidden;
  transition: max-height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.section-content.collapsed {
  max-height: 0;
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .section-content {
    transition: none;
  }
}
```

**Alternatives Considered**:
- ❌ **Framer Motion**: 功能强大但增加 60KB bundle，对于简单的折叠动画过度设计
- ❌ **React Spring**: 基于物理的动画更适合游戏/交互艺术，本项目不需要
- ❌ **GSAP**: 商业项目需要付费许可，且 bundle size 较大

**如需 Framer Motion 的场景**（可选，Phase 2）:
- US4 (P3): 拖拽重排区域时的流畅过渡
- 复杂的 stagger 动画（导航点逐个出现）

---

### 2. 滚动实现方案 (Scroll Implementation)

**研究任务**: 选择整页滚动的最佳技术方案

#### 选项对比

| 方案 | 浏览器支持 | Bundle Size | 性能 | 灵活性 | 学习曲线 | 与 React 兼容性 |
|------|-----------|------------|------|--------|---------|----------------|
| **CSS scroll-snap** | ✅ 95%+ | 0 KB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **fullPage.js** | ✅ 全部 | ~18 KB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ (jQuery-based) |
| **react-fullpage** | ✅ 全部 | ~20 KB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ (React wrapper) |
| **自研 useScrollSnap** | 取决于实现 | 0 KB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

#### 决策: **CSS scroll-snap (Primary) + 自研 useScrollSnap Hook (Enhancement)**

**Rationale**:
1. **原生性能**: 浏览器原生实现，性能最优，无 JavaScript 阻塞
2. **零依赖**: 无需引入第三方库，减少 bundle size 和维护负担
3. **渐进增强**: 基础功能用 CSS，高级交互（导航点同步、键盘控制）用 JS 增强
4. **响应式友好**: CSS scroll-snap 天然支持不同视口尺寸
5. **可访问性**: 原生滚动行为保留辅助技术支持

**技术方案**:

```css
/* 容器滚动配置 */
.scroll-container {
  scroll-snap-type: y mandatory; /* 垂直方向强制对齐 */
  scroll-behavior: smooth;       /* 平滑滚动 */
  overflow-y: scroll;
  height: 100vh;
}

/* 区域对齐点 */
.page-section {
  scroll-snap-align: start;      /* 对齐到区域开始位置 */
  scroll-snap-stop: always;      /* 强制停止在每个区域 */
  min-height: 100vh;             /* 最小一屏高度 */
}

/* 桌面端：容器内滚动 vs 移动端：页面滚动 */
@media (min-width: 1024px) {
  .scroll-container {
    /* 使用容器滚动，不影响其他元素 */
  }
}

@media (max-width: 1023px) {
  body {
    scroll-snap-type: y proximity; /* 移动端使用 proximity 更灵活 */
  }
}
```

**JavaScript 增强层** (自研 `useScrollSnap` Hook):

```typescript
// hooks/useScrollSnap.ts
interface UseScrollSnapOptions {
  enabled: boolean;          // 是否启用整页滚动
  threshold: number;         // 对齐阈值 (0-1)
  onSectionChange: (index: number) => void; // 区域切换回调
}

export function useScrollSnap(options: UseScrollSnapOptions) {
  // 1. Intersection Observer: 检测当前可见区域
  // 2. 滚动事件监听: 更新导航点高亮
  // 3. 键盘事件: 支持 Page Up/Down, Arrow Keys
  // 4. History API: 记录当前区域 (FR-010)
  // 5. 禁用逻辑: 用户切换滚动模式时移除 scroll-snap-type
}
```

**处理边缘案例**:
- **区域高度 < 视口高度**: 使用 `min-height: 100vh` 确保一致性
- **区域高度 > 视口高度** (移动端): 使用 `scroll-snap-align: start` + `scroll-snap-stop: normal`
- **嵌套滚动容器** (如股票列表): 监听滚动事件，子容器滚动时暂停整页滚动
- **浏览器不支持 scroll-snap**: 降级为标准滚动，JavaScript 层检测支持度

**Alternatives Considered**:
- ❌ **fullPage.js**: jQuery 依赖与 React 19 不兼容，且 bundle size 较大
- ❌ **react-fullpage**: 商业许可（免费版有水印），功能过度设计（支持横向滚动、视差等不需要的特性）
- ⚠️ **纯自研**: 完全用 JS 实现滚动需要处理大量边缘案例（滚动惯性、触摸手势等），开发成本高

**为什么不用第三方库**:
1. **需求简单**: 只需垂直整页滚动 + 导航点，无需横向、视差、视频背景等复杂特性
2. **性能优先**: CSS scroll-snap 由浏览器原生优化，帧率更稳定
3. **维护成本**: 第三方库更新滞后（如 fullPage.js 最后更新 2021 年），自研可完全控制
4. **bundle size**: 每增加 1KB JS 影响首屏加载时间，CSS 方案零成本

**实现里程碑**:
- Phase 1: 实现基础 CSS scroll-snap 布局
- Phase 2: 开发 `useScrollSnap` Hook 支持导航点同步
- Phase 3: 添加键盘导航和 History API 支持

---

### 3. 拖拽库选择 (Drag & Drop - US4-P3)

**研究任务**: 为区域重排功能选择拖拽实现方案

#### 决策: **延后到 Phase 2 (P3 优先级)**

**Rationale**:
1. **优先级低**: US4 (P3) - 自定义布局顺序是高级功能，不影响 MVP
2. **依赖 Phase 1**: 需要先完成基础布局和状态管理，再添加拖拽交互
3. **可选特性**: 根据用户反馈决定是否实现

**候选方案** (当需要实现时):

| 方案 | Bundle Size | 触摸支持 | React 集成 | 可访问性 |
|------|------------|---------|-----------|---------|
| **@dnd-kit/core** | ~15 KB | ✅ 优秀 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **react-beautiful-dnd** | ~30 KB | ⚠️ 一般 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **react-dnd** | ~22 KB | ⚠️ 需插件 | ⭐⭐⭐ | ⭐⭐⭐ |
| **HTML5 Drag API** | 0 KB | ❌ 无触摸 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**推荐**: **@dnd-kit/core** (如需实现 US4)
- 现代化 React Hooks API
- 优秀的触摸设备支持（移动端友好）
- 完善的可访问性（键盘拖拽支持）
- 模块化设计，可按需导入

**暂不决策原因**:
- 避免过早优化
- 保持 bundle size 最小化
- 专注于 P1/P2 高优先级功能

---

## Technology Stack Summary

### 最终技术选型

| 技术领域 | 选定方案 | Bundle 影响 | 理由 |
|---------|---------|------------|------|
| **动画** | CSS Animations | 0 KB | 性能最优，Tailwind 原生支持 |
| **整页滚动** | CSS scroll-snap + 自研 Hook | ~2 KB | 原生性能，灵活控制 |
| **状态管理** | Zustand (已有) | 0 KB | 项目已集成，无额外成本 |
| **可见性检测** | Intersection Observer API | 0 KB | 浏览器原生 API |
| **本地存储** | localStorage API | 0 KB | 浏览器原生 API |
| **拖拽** | 延后决策 (P3) | TBD | 非 MVP 必需 |

**Total Bundle Impact**: **~2 KB** (仅 useScrollSnap Hook，其余零成本)

### 依赖更新

**无需新增 npm 依赖** ✅

所有功能基于：
- 现有依赖：Next.js, React, Tailwind CSS, Zustand
- 浏览器原生 API：scroll-snap, Intersection Observer, localStorage
- 自研轻量 Hook：`useScrollSnap`, `useSectionVisibility`, `useCollapsibleState`

---

## Best Practices Research

### 1. 整页滚动最佳实践

**来源**: MDN Web Docs, web.dev, CSS-Tricks

**关键要点**:
1. **使用 `scroll-behavior: smooth`**: 平滑滚动效果，但注意 `prefers-reduced-motion` 覆盖
2. **`scroll-snap-type` 选择**:
   - `mandatory`: 强制对齐，适合桌面端
   - `proximity`: 接近时才对齐，适合移动端（避免与触摸手势冲突）
3. **避免嵌套滚动冲突**: 子容器设置 `scroll-snap-type: none` 或监听事件暂停父容器对齐
4. **History API 集成**: 使用 `history.replaceState()` 而非 `pushState()`，避免浏览器历史记录污染

**性能优化**:
```typescript
// 使用 throttle 优化滚动事件监听
const handleScroll = useCallback(
  throttle(() => {
    // 更新导航点高亮
  }, 100, { leading: true, trailing: true }),
  []
);
```

**可访问性**:
- 为导航点添加 `role="navigation"` 和 `aria-label="页面导航"`
- 每个导航点包含 `aria-label="跳转到{区域名称}"`
- 支持键盘焦点管理 (Tab 键遍历导航点)

### 2. 折叠动画最佳实践

**来源**: Framer Motion Docs, CSS Animations Performance Guide

**关键要点**:
1. **避免动画 `height` 属性**: 会触发 layout reflow，使用 `max-height` + `overflow: hidden`
2. **优先动画 `transform` 和 `opacity`**: GPU 加速，不触发 repaint
3. **使用 `cubic-bezier` 缓动函数**: `cubic-bezier(0.4, 0, 0.2, 1)` (Material Design 标准)
4. **动画时禁用滚动**: 防止折叠动画与整页滚动冲突

**实现模式**:
```typescript
// 折叠状态管理 Hook
export function useCollapsibleState(sectionId: string) {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    // 从 localStorage 恢复状态
    const saved = localStorage.getItem(`section-${sectionId}-collapsed`);
    return saved === 'true';
  });

  const toggle = useCallback(() => {
    setIsCollapsed(prev => {
      const newState = !prev;
      localStorage.setItem(`section-${sectionId}-collapsed`, String(newState));
      return newState;
    });
  }, [sectionId]);

  return { isCollapsed, toggle };
}
```

### 3. 响应式滚动策略

**来源**: Smashing Magazine, A List Apart

**关键要点**:
1. **桌面端**: 使用容器滚动 (`overflow-y: scroll`)，保留 header/footer
2. **移动端**: 使用 `body` 滚动，避免嵌套滚动问题
3. **断点选择**: 
   - `<768px`: 移动端，使用 `scroll-snap-type: y proximity`
   - `≥768px`: 平板/桌面，使用 `scroll-snap-type: y mandatory`
4. **触摸手势**: 移动端禁用 `touch-action: none`，保留原生滚动惯性

---

## Integration Patterns

### 与现有功能集成

#### 1. WebSocket 实时更新

**问题**: 整页滚动时，区域外的实时数据更新是否会导致性能问题？

**解决方案**:
- 使用 Intersection Observer 检测区域可见性
- 不可见区域暂停实时更新或降低更新频率
- 区域进入视口时恢复正常更新

```typescript
// hooks/useSectionVisibility.ts
export function useSectionVisibility(sectionRef: RefObject<HTMLElement>) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setIsVisible(entry.isIntersecting),
      { threshold: 0.1 } // 10% 可见即认为进入视口
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, [sectionRef]);

  return isVisible;
}
```

#### 2. ErrorBoundary 兼容

**问题**: 折叠区域中的组件错误是否会影响整体布局？

**解决方案**:
- 每个 Section 内部保留独立的 ErrorBoundary
- 折叠状态与错误状态独立管理
- 错误组件不影响折叠动画

#### 3. Skeleton Loading

**问题**: 懒加载组件与整页滚动如何协同？

**解决方案**:
- Skeleton 高度与实际组件高度一致 (使用 `min-height`)
- 避免加载完成后布局偏移导致滚动位置错乱
- 使用 `scroll-margin-top` 补偿动态高度变化

---

## Performance Considerations

### 性能目标验证策略

| 指标 | 目标 | 测量方法 | 优化策略 |
|------|------|---------|---------|
| 滚动帧率 | 60fps | Chrome DevTools Performance | 避免 layout thrashing，使用 transform |
| 触摸响应 | <100ms | User Timing API | 使用 passive event listeners |
| 动画流畅度 | 60fps | `requestAnimationFrame` 监控 | GPU 加速，避免 repaint |
| 首屏加载 | ≤110% baseline | Lighthouse | 代码分割，CSS 内联关键样式 |

### 潜在性能瓶颈

1. **滚动事件监听器**:
   - 风险：频繁触发导致主线程阻塞
   - 缓解：使用 `throttle` (100ms) + `passive: true`

2. **Intersection Observer 多实例**:
   - 风险：每个区域创建独立 Observer 消耗内存
   - 缓解：使用单个 Observer 观察所有区域

3. **localStorage 频繁读写**:
   - 风险：同步 I/O 阻塞主线程
   - 缓解：状态更新时 debounce 写入，读取时一次性加载

4. **折叠动画重排**:
   - 风险：动画 `height` 触发 layout
   - 缓解：使用 `max-height` + `transform: scaleY()`

---

## Risk Mitigation

### 技术风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|-------|------|---------|
| 浏览器不支持 scroll-snap | 低 (5%) | 中 | 降级为标准滚动 + JS 检测 |
| 移动端手势冲突 | 中 (30%) | 高 | 使用 `scroll-snap-type: proximity` |
| 性能未达 60fps | 中 (40%) | 高 | Phase 1 性能测试，及时调整方案 |
| localStorage 容量限制 | 低 (10%) | 低 | 数据压缩 (<5KB)，异常处理 |
| 折叠动画卡顿 | 中 (25%) | 中 | 使用 `will-change: max-height` |

### 降级策略

```typescript
// 检测 scroll-snap 支持
const supportsScrollSnap = CSS.supports('scroll-snap-type', 'y mandatory');

if (!supportsScrollSnap) {
  // 降级：使用 JS 滚动 + scrollIntoView
  element.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 检测性能
if (navigator.hardwareConcurrency < 4 || navigator.deviceMemory < 4) {
  // 低性能设备：禁用动画，使用 instant 跳转
  document.body.classList.add('reduce-motion');
}
```

---

## Conclusion

### 技术选型总结

✅ **All NEEDS CLARIFICATION items resolved**:

1. **动画库**: CSS Animations (primary), Framer Motion 仅用于 P3 拖拽特性
2. **滚动实现**: CSS scroll-snap + 自研 `useScrollSnap` Hook
3. **拖拽库**: 延后到 Phase 2 (P3 优先级)

### 关键决策原则

1. **性能优先**: 优先选择浏览器原生 API，避免 JS 库增加 bundle size
2. **渐进增强**: 基础功能用 CSS，高级交互用 JS 增强
3. **零依赖目标**: 所有新功能无需新增 npm 依赖
4. **可测试性**: 逻辑封装在 Hooks 中，便于单元测试

### Phase 1 准备就绪

所有技术不确定性已解决，可以进入 Phase 1: Design & Contracts

**Next Steps**:
1. ✅ 创建 `data-model.md` (定义 Section, Preferences 实体)
2. ✅ 生成 `quickstart.md` (用户场景测试脚本)
3. ✅ 更新 Agent Context (无新依赖，跳过)

---

**Version**: 1.0  
**Approved by**: GitHub Copilot  
**Date**: 2025-10-30
