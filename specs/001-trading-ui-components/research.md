# Research: TradingView 风格交易界面核心组件

**Feature**: 001-trading-ui-components
**Date**: 2025-10-24
**Status**: Complete

## Phase 0: Technical Research & Decision Log

### 1. K线图表库选择

**Decision**: Lightweight Charts 4.x

**Rationale**:
- TradingView 官方开源图表库，与需求完全匹配
- 性能优异，使用 Canvas 渲染，支持大数据量
- 内置金融图表功能（K线、成交量、技术指标）
- TypeScript 支持完善
- 活跃维护，文档完整

**Alternatives Considered**:
- **Recharts**: React 原生图表库，但性能不足以处理大量金融数据
- **Chart.js**: 通用图表库，金融图表支持不够专业
- **D3.js**: 功能强大但学习曲线陡峭，开发成本高
- **ECharts**: 功能全面但包体积大，且非专门为金融场景设计

**Implementation Notes**:
- 使用 `'use client'` 指令确保客户端渲染
- 通过 `useEffect` Hook 管理图表生命周期
- 创建自定义 Hook (`useChart`) 封装图表逻辑

---

### 2. 状态管理方案

**Decision**: Zustand 4.x

**Rationale**:
- 轻量级（< 1KB gzipped）
- API 简洁直观，学习成本低
- TypeScript 支持优秀
- 不需要 Provider 包裹，使用更灵活
- 性能优异，支持选择性订阅

**Alternatives Considered**:
- **Redux Toolkit**: 功能强大但复杂度高，对于本功能过度设计
- **Jotai**: 原子化状态管理，但对于集中式交易状态不够直观
- **Valtio**: 基于 Proxy 的响应式状态，但生态不如 Zustand 成熟
- **React Context**: 原生方案但性能问题明显，不适合频繁更新的场景

**Implementation Notes**:
- 已实现 `tradingStore.ts`，包含账户、持仓、交易历史状态
- 使用 `create` 函数创建 Store
- 通过 selector 优化性能，避免不必要的重渲染

---

### 3. HTTP 客户端

**Decision**: Axios 1.x

**Rationale**:
- 浏览器和 Node.js 双端支持
- 请求/响应拦截器便于统一处理
- 自动 JSON 转换
- 支持请求取消和超时设置
- 错误处理机制完善

**Alternatives Considered**:
- **Fetch API**: 原生 API 但功能有限，缺少拦截器
- **ky**: 现代化但生态不如 Axios 成熟
- **SWR/React Query**: 数据获取库，但需要与 Axios 配合，增加复杂度

**Implementation Notes**:
- 已实现 `lib/api/client.ts`，配置了拦截器
- 已实现 `lib/api/trading.ts`，封装了所有交易相关 API
- 使用 TypeScript 类型确保类型安全

---

### 4. 日期处理库

**Decision**: date-fns 3.x

**Rationale**:
- 函数式 API，Tree-shakable，只打包使用的函数
- TypeScript 原生支持
- 不可变数据处理，避免副作用
- 性能优于 Moment.js

**Alternatives Considered**:
- **Moment.js**: 体积大且已停止维护
- **Day.js**: 轻量但功能不如 date-fns 全面
- **Luxon**: 强大但体积较大

**Implementation Notes**:
- 主要用于交易时间、K线时间戳的格式化
- 已在 `lib/utils/format.ts` 中实现 `formatDateTime` 函数

---

### 5. 样式方案

**Decision**: Tailwind CSS 4

**Rationale**:
- Utility-first，开发效率高
- JIT 模式，按需生成样式
- 响应式设计内置支持
- 深色模式支持优秀
- 与 Next.js 集成良好

**Alternatives Considered**:
- **CSS Modules**: 需要手写大量 CSS，开发效率低
- **Styled-components**: 运行时性能开销，与 Next.js App Router 兼容性问题
- **Emotion**: 同样有运行时开销

**Implementation Notes**:
- 已配置 Tailwind CSS 4
- 使用深色主题配色（TradingView 风格）：
  - 背景: `#0a0e14`
  - 面板: `#131722`
  - 边框: `#2a2e39`

---

### 6. 组件架构模式

**Decision**: 函数组件 + React Hooks + Composition

**Rationale**:
- React 19 推荐模式
- Hooks 提供更好的逻辑复用
- Composition 模式提高组件灵活性
- 更好的 TypeScript 支持

**Key Patterns**:
1. **Presentational vs Container**: 分离 UI 和逻辑
2. **Custom Hooks**: 封装可复用逻辑（`useChart`, `useTrade`, `useDebounce`）
3. **Controlled Components**: 表单组件使用受控模式
4. **Event Bubbling**: 利用事件冒泡减少事件监听器

**Implementation Notes**:
- 所有组件使用函数组件
- 复杂逻辑提取为自定义 Hook
- 避免 Class 组件和高阶组件（HOC）

---

### 7. 性能优化策略

**Decision**: 虚拟化 + 防抖/节流 + React.memo

**Strategies**:

1. **列表虚拟化** (针对股票列表、交易历史)
   - 使用 `react-window` 或原生实现虚拟滚动
   - 只渲染可见区域的元素

2. **防抖/节流** (针对搜索、滚动)
   - 实现 `useDebounce` Hook
   - 搜索框防抖延迟 300ms

3. **组件缓存** (针对列表项)
   - 使用 `React.memo` 避免不必要的重渲染
   - 使用 `useMemo` 和 `useCallback` 优化子组件 props

4. **数据懒加载** (针对交易历史)
   - 分页加载，每页 20 条记录
   - 滚动到底部时自动加载下一页

**Implementation Notes**:
- K线图表使用 Lightweight Charts 内置优化
- 持仓盈亏计算使用 `useMemo` 缓存结果
- 避免在 render 中创建新函数或对象

---

### 8. 测试策略

**Decision**: Jest + React Testing Library + Playwright

**Test Layers**:

1. **Unit Tests** (Jest + RTL)
   - 组件渲染测试
   - 用户交互测试（点击、输入）
   - 工具函数测试

2. **Integration Tests** (Jest + RTL)
   - 组件组合测试
   - Store 集成测试
   - API Mock 测试

3. **E2E Tests** (Playwright)
   - 完整交易流程测试
   - 跨浏览器测试

**Coverage Goals**:
- Unit Tests: > 80%
- Critical Paths: 100%

**Implementation Notes**:
- 使用 `@testing-library/react` 的 "查询用户看到的内容" 原则
- 使用 MSW (Mock Service Worker) mock API 请求
- E2E 测试覆盖所有用户场景（spec.md 中的 Acceptance Scenarios）

---

### 9. 错误处理和边界情况

**Decision**: Error Boundaries + Toast Notifications + Graceful Degradation

**Strategies**:

1. **Error Boundaries**: 捕获组件树的错误
2. **API 错误**: Axios 拦截器统一处理
3. **Toast Notifications**: 用户友好的错误提示
4. **Fallback UI**: 数据加载失败时显示友好提示

**Edge Cases Covered** (from spec.md):
- 股票价格数据缺失 → 显示 "暂无数据"
- 网络请求失败 → 显示 "加载失败，请稍后重试"
- 并发交易冲突 → 按顺序处理
- 持仓数量为小数 → 支持小数精度
- 极端价格输入 → 表单验证
- 账户余额不足边界情况 → 允许刚好等于余额的交易
- 持仓清零 → 正确移除

---

### 10. 无障碍访问 (Accessibility)

**Decision**: ARIA Labels + Keyboard Navigation + Semantic HTML

**Features**:
- 所有交互元素支持键盘导航
- ARIA labels 用于屏幕阅读器
- 语义化 HTML（button, form, input）
- 焦点管理（对话框打开时自动聚焦）
- 颜色对比度符合 WCAG AA 标准

**Implementation Notes**:
- 交易确认对话框支持 Esc 键关闭
- 表单支持 Enter 键提交
- 列表支持上下方向键导航

---

## Research Summary

所有技术决策已完成，无 "NEEDS CLARIFICATION" 项。技术栈选择基于以下原则：

1. **性能优先**: Lightweight Charts, Zustand, Tailwind CSS
2. **开发效率**: TypeScript, React Hooks, Axios
3. **可维护性**: 函数组件, 自定义 Hooks, 清晰的文件结构
4. **用户体验**: 虚拟化, 防抖/节流, 错误处理

技术选型完全支持 spec.md 中定义的所有功能需求和性能目标。
