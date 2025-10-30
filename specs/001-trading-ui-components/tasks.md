# Tasks: TradingView 风格交易界面核心组件

**Feature**: 001-trading-ui-components
**Status**: Ready for Implementation
**Generated**: 2025-10-24

## Task Organization

任务按用户场景（User Story）组织，每个场景包含实现任务和测试任务。任务优先级继承用户场景优先级。

**Task Format**: `- [ ] [TaskID] [Priority] [Story] Description (file path)`

**Priorities**: P1 (高优先级) → P2 (中优先级) → P3 (低优先级)

---

## Phase 1: Setup & Infrastructure

**已完成**的基础设施任务：

- [x] [SETUP-001] [P1] 安装前端依赖包 (frontend/package.json)
- [x] [SETUP-002] [P1] 创建 TypeScript 类型定义 (frontend/src/types/trading.ts)
- [x] [SETUP-003] [P1] 实现 API 客户端封装 (frontend/src/lib/api/client.ts)
- [x] [SETUP-004] [P1] 实现交易 API 函数 (frontend/src/lib/api/trading.ts)
- [x] [SETUP-005] [P1] 实现格式化工具函数 (frontend/src/lib/utils/format.ts)
- [x] [SETUP-006] [P1] 创建 Zustand 状态管理 Store (frontend/src/stores/tradingStore.ts)
- [x] [SETUP-007] [P1] 实现交易主页基础布局 (frontend/src/app/trading/page.tsx)

---

## Phase 2: User Story 1 - 查看股票实时行情与K线图表 (Priority: P1)

### 实现任务

- [ ] [US1-001] [P1] [US1] 创建 useDebounce 自定义 Hook (frontend/src/hooks/useDebounce.ts)
  - 实现防抖逻辑，支持自定义延迟时间
  - 返回防抖后的值
  - 在 cleanup 时清除定时器

- [ ] [US1-002] [P1] [US1] 创建 useChart 自定义 Hook (frontend/src/hooks/useChart.ts)
  - 封装 Lightweight Charts 初始化逻辑
  - 管理图表实例生命周期（创建、更新、销毁）
  - 支持响应式容器尺寸调整
  - 暴露 addCandlestickSeries 和 addHistogramSeries 方法

- [ ] [US1-003] [P1] [US1] 实现 K线图表组件骨架 (frontend/src/components/trading/CandlestickChart.tsx)
  - 创建 'use client' 组件
  - 定义 Props 接口（assetSymbol, timeframe）
  - 创建图表容器 div（ref 绑定）
  - 使用 useChart Hook 初始化图表

- [ ] [US1-004] [P1] [US1] 实现 K线数据加载逻辑 (frontend/src/components/trading/CandlestickChart.tsx)
  - 使用 useEffect 监听 assetSymbol 和 timeframe 变化
  - 调用 API 获取 K线数据（需后端提供端点）
  - 处理加载状态和错误状态
  - 将数据转换为 Lightweight Charts 格式

- [ ] [US1-005] [P1] [US1] 实现 K线系列和成交量系列渲染 (frontend/src/components/trading/CandlestickChart.tsx)
  - 创建 Candlestick 系列并设置数据
  - 创建 Histogram 系列显示成交量
  - 配置图表样式（深色主题配色）
  - 设置十字光标选项

- [ ] [US1-006] [P1] [US1] 实现时间周期切换功能 (frontend/src/components/trading/CandlestickChart.tsx)
  - 添加时间周期选择器 UI（日K/周K/月K）
  - 实现周期切换事件处理
  - 切换时重新加载对应周期的数据
  - 保持图表缩放和位置状态

- [ ] [US1-007] [P1] [US1] 实现鼠标悬停详细数据显示 (frontend/src/components/trading/CandlestickChart.tsx)
  - 使用 Lightweight Charts 的 Tooltip 或自定义覆盖层
  - 显示当前光标位置的开高低收、成交量
  - 格式化数据显示（货币格式、数量格式）
  - 优化性能（防抖更新）

- [ ] [US1-008] [P1] [US1] 实现图表交互功能 (frontend/src/components/trading/CandlestickChart.tsx)
  - 启用鼠标拖动平移功能
  - 启用滚轮缩放功能
  - 添加重置缩放按钮
  - 优化触摸设备支持

- [ ] [US1-009] [P1] [US1] 添加图表加载状态和错误处理 (frontend/src/components/trading/CandlestickChart.tsx)
  - 显示 Loading 指示器（骨架屏或加载动画）
  - 显示"暂无数据"占位符
  - 显示错误提示信息
  - 提供重试按钮

### 测试任务

- [ ] [US1-TEST-001] [P1] [US1] 编写 CandlestickChart 组件单元测试 (frontend/__tests__/components/trading/CandlestickChart.test.tsx)
  - 测试组件正确渲染
  - 测试时间周期切换功能
  - 测试 assetSymbol 变化时重新加载数据
  - 测试加载状态和错误状态显示
  - Mock Lightweight Charts API

- [ ] [US1-TEST-002] [P1] [US1] 编写 useChart Hook 单元测试 (frontend/__tests__/hooks/useChart.test.ts)
  - 测试图表实例创建
  - 测试容器尺寸变化时图表自动调整
  - 测试组件卸载时图表正确销毁
  - 验证无内存泄漏

- [ ] [US1-E2E-001] [P1] [US1] 编写 K线图表 E2E 测试 (frontend/__tests__/e2e/candlestick-chart.spec.ts)
  - 测试用户选择股票后图表显示
  - 测试时间周期切换交互
  - 测试鼠标悬停显示详细数据
  - 测试图表拖动和缩放功能

---

## Phase 3: User Story 2 - 快速执行买入/卖出交易 (Priority: P1)

### 实现任务

- [ ] [US2-001] [P1] [US2] 创建 useTrade 自定义 Hook (frontend/src/hooks/useTrade.ts)
  - 封装买入/卖出交易逻辑
  - 连接 Zustand Store 的 executeBuy/executeSell
  - 处理交易成功/失败状态
  - 提供表单验证辅助函数

- [ ] [US2-002] [P1] [US2] 实现交易确认对话框组件 (frontend/src/components/trading/TradeConfirmDialog.tsx)
  - 创建模态对话框 UI
  - 显示交易详情（股票、数量、价格、总金额）
  - 提供"确认"和"取消"按钮
  - 支持 Esc 键关闭、Enter 键确认
  - 添加加载状态（提交中）

- [ ] [US2-003] [P1] [US2] 实现交易面板组件骨架 (frontend/src/components/trading/TradePanel.tsx)
  - 创建 'use client' 组件
  - 定义 Props 接口（selectedAsset, currentAccount）
  - 创建买入/卖出 Tab 切换 UI
  - 创建表单布局（股票代码、价格、数量输入框）

- [ ] [US2-004] [P1] [US2] 实现表单状态管理 (frontend/src/components/trading/TradePanel.tsx)
  - 使用 useState 管理表单字段（side, assetSymbol, price, quantity）
  - 使用 useState 管理验证错误状态
  - 实现自动填充逻辑（从 selectedAsset 填充代码和价格）
  - 实现表单重置功能

- [ ] [US2-005] [P1] [US2] 实现表单验证逻辑 (frontend/src/components/trading/TradePanel.tsx)
  - 验证 assetSymbol 非空
  - 验证 price > 0 且为有效数字
  - 验证 quantity > 0 且为有效数字
  - 买入时验证 price * quantity <= 账户余额
  - 卖出时验证 quantity <= 持仓数量
  - 实时显示验证错误信息

- [ ] [US2-006] [P1] [US2] 实现交易提交流程 (frontend/src/components/trading/TradePanel.tsx)
  - 实现"确认买入"/"确认卖出"按钮点击处理
  - 显示交易确认对话框
  - 用户确认后调用 useTrade Hook 执行交易
  - 交易成功后显示成功提示并重置表单
  - 交易失败后显示错误信息

- [ ] [US2-007] [P1] [US2] 实现预估金额计算和显示 (frontend/src/components/trading/TradePanel.tsx)
  - 实时计算 price * quantity
  - 显示预估交易金额
  - 买入时显示"需要资金"，卖出时显示"预计收入"
  - 余额不足时高亮提示

- [ ] [US2-008] [P1] [US2] 优化交互体验 (frontend/src/components/trading/TradePanel.tsx)
  - Tab 切换时清空或保留表单数据（根据 UX 决定）
  - 支持键盘快捷操作（Enter 提交、Esc 取消）
  - 输入框自动聚焦
  - 提交时禁用表单防止重复提交

### 测试任务

- [ ] [US2-TEST-001] [P1] [US2] 编写 TradePanel 组件单元测试 (frontend/__tests__/components/trading/TradePanel.test.tsx)
  - 测试买入/卖出 Tab 切换
  - 测试表单输入和验证
  - 测试自动填充功能
  - 测试余额不足/持仓不足验证
  - Mock useTrade Hook

- [ ] [US2-TEST-002] [P1] [US2] 编写 TradeConfirmDialog 组件单元测试 (frontend/__tests__/components/trading/TradeConfirmDialog.test.tsx)
  - 测试对话框显示和关闭
  - 测试确认和取消按钮
  - 测试键盘快捷键
  - 测试交易详情正确显示

- [ ] [US2-TEST-003] [P1] [US2] 编写 useTrade Hook 单元测试 (frontend/__tests__/hooks/useTrade.test.ts)
  - 测试买入交易执行
  - 测试卖出交易执行
  - 测试交易成功后状态更新
  - 测试交易失败错误处理
  - Mock Zustand Store

- [ ] [US2-E2E-001] [P1] [US2] 编写交易执行 E2E 测试 (frontend/__tests__/e2e/trade-execution.spec.ts)
  - 测试完整买入流程（填写表单 → 确认 → 成功提示）
  - 测试完整卖出流程
  - 测试余额不足时阻止交易
  - 测试持仓不足时阻止交易
  - 测试交易后账户余额和持仓更新

---

## Phase 4: User Story 5 - 搜索并选择股票 (Priority: P2)

### 实现任务

- [ ] [US5-001] [P2] [US5] 实现股票搜索组件骨架 (frontend/src/components/trading/StockSearch.tsx)
  - 创建搜索框 UI（输入框 + 搜索图标）
  - 定义 Props 接口（onSelectStock 回调）
  - 创建搜索结果列表容器

- [ ] [US5-002] [P2] [US5] 实现搜索状态管理 (frontend/src/components/trading/StockSearch.tsx)
  - 使用 useState 管理搜索关键词
  - 使用 useDebounce Hook 防抖处理（300ms）
  - 使用 useState 管理搜索结果和加载状态

- [ ] [US5-003] [P2] [US5] 实现搜索 API 调用 (frontend/src/components/trading/StockSearch.tsx)
  - 使用 useEffect 监听 debouncedQuery 变化
  - 调用 searchAssets API 函数
  - 处理空查询（清空结果）
  - 处理搜索失败

- [ ] [US5-004] [P2] [US5] 实现搜索结果显示 (frontend/src/components/trading/StockSearch.tsx)
  - 渲染搜索结果列表（股票代码、名称、当前价格）
  - 高亮匹配的关键词
  - 显示"无搜索结果"提示
  - 限制显示数量（最多 20 条）

- [ ] [US5-005] [P2] [US5] 实现股票选择逻辑 (frontend/src/components/trading/StockSearch.tsx)
  - 实现列表项点击事件
  - 调用 onSelectStock 回调传递选中的股票
  - 清空搜索框和搜索结果
  - 更新 Zustand Store 的 selectedAsset

- [ ] [US5-006] [P2] [US5] 实现股票列表项组件 (frontend/src/components/trading/StockListItem.tsx)
  - 显示股票代码、名称
  - 显示当前价格和涨跌幅
  - 使用颜色区分涨跌（绿色/红色）
  - 选中状态高亮
  - 悬停效果

- [ ] [US5-007] [P2] [US5] 集成股票搜索到主页 (frontend/src/app/trading/page.tsx)
  - 在左侧面板顶部添加 StockSearch 组件
  - 实现 onSelectStock 回调，更新 selectedAsset
  - 同步更新图表和交易面板
  - 保持搜索框和列表的状态独立

### 测试任务

- [ ] [US5-TEST-001] [P2] [US5] 编写 StockSearch 组件单元测试 (frontend/__tests__/components/trading/StockSearch.test.tsx)
  - 测试搜索输入防抖
  - 测试搜索结果显示
  - 测试空查询清空结果
  - 测试选择股票后清空搜索框
  - Mock searchAssets API

- [ ] [US5-TEST-002] [P2] [US5] 编写 StockListItem 组件单元测试 (frontend/__tests__/components/trading/StockListItem.test.tsx)
  - 测试股票信息正确显示
  - 测试涨跌颜色显示
  - 测试点击事件触发
  - 测试选中状态样式

- [ ] [US5-E2E-001] [P2] [US5] 编写股票搜索 E2E 测试 (frontend/__tests__/e2e/stock-search.spec.ts)
  - 测试输入关键词后搜索结果实时更新
  - 测试点击搜索结果后图表和交易面板更新
  - 测试清空搜索框恢复完整列表
  - 测试搜索结果键盘导航

---

## Phase 5: User Story 3 - 查看持仓列表与盈亏统计 (Priority: P2)

### 实现任务

- [ ] [US3-001] [P2] [US3] 实现盈亏指示器组件 (frontend/src/components/trading/ProfitIndicator.tsx)
  - 接收 profit 和 profitRate 参数
  - 根据正负值显示不同颜色（绿色/红色/灰色）
  - 显示盈亏金额和百分比
  - 添加上涨/下跌图标

- [ ] [US3-002] [P2] [US3] 实现持仓列表组件骨架 (frontend/src/components/trading/HoldingsList.tsx)
  - 创建表格布局（股票代码、名称、数量、成本价、当前价、市值、盈亏）
  - 定义 Props 接口（holdings, onSelectHolding）
  - 使用 Zustand Store 获取 holdings 数据

- [ ] [US3-003] [P2] [US3] 实现持仓数据加载 (frontend/src/components/trading/HoldingsList.tsx)
  - 使用 useEffect 加载持仓数据
  - 处理加载状态和错误状态
  - 显示"暂无持仓"占位符

- [ ] [US3-004] [P2] [US3] 实现盈亏计算逻辑 (frontend/src/components/trading/HoldingsList.tsx)
  - 使用 useMemo 计算每只股票的盈亏
  - 计算总成本、总市值、总盈亏、总盈亏率
  - 格式化货币和百分比显示

- [ ] [US3-005] [P2] [US3] 实现排序功能 (frontend/src/components/trading/HoldingsList.tsx)
  - 添加列标题点击排序
  - 支持按盈亏、市值、数量排序
  - 支持升序/降序切换
  - 显示排序指示器

- [ ] [US3-006] [P2] [US3] 实现持仓行点击切换股票 (frontend/src/components/trading/HoldingsList.tsx)
  - 实现行点击事件
  - 更新 selectedAsset
  - 同步更新图表和交易面板（切换到"卖出"模式）
  - 高亮选中的持仓行

- [ ] [US3-007] [P2] [US3] 实现持仓实时价格更新 (frontend/src/components/trading/HoldingsList.tsx)
  - 定时轮询获取最新价格（每 5 秒）或使用 WebSocket
  - 更新 currentPrice 后自动重新计算盈亏
  - 添加价格变化动画效果
  - 组件卸载时清除定时器

- [ ] [US3-008] [P2] [US3] 集成持仓列表到主页 (frontend/src/app/trading/page.tsx)
  - 在底部"持仓"标签页中渲染 HoldingsList
  - 实现 onSelectHolding 回调
  - 持仓更新后自动刷新列表

### 测试任务

- [ ] [US3-TEST-001] [P2] [US3] 编写 HoldingsList 组件单元测试 (frontend/__tests__/components/trading/HoldingsList.test.tsx)
  - 测试持仓数据正确显示
  - 测试盈亏计算准确性
  - 测试排序功能
  - 测试点击持仓行切换股票
  - Mock holdings 数据

- [ ] [US3-TEST-002] [P2] [US3] 编写 ProfitIndicator 组件单元测试 (frontend/__tests__/components/trading/ProfitIndicator.test.tsx)
  - 测试盈利时绿色显示
  - 测试亏损时红色显示
  - 测试持平时灰色显示
  - 测试数值格式化

- [ ] [US3-E2E-001] [P2] [US3] 编写持仓列表 E2E 测试 (frontend/__tests__/e2e/holdings-list.spec.ts)
  - 测试买入后持仓列表更新
  - 测试卖出全部持仓后从列表移除
  - 测试点击持仓行切换到该股票
  - 测试盈亏实时更新

---

## Phase 6: User Story 4 - 查看交易历史记录 (Priority: P3)

### 实现任务

- [ ] [US4-001] [P3] [US4] 实现交易历史组件骨架 (frontend/src/components/trading/TradeHistory.tsx)
  - 创建表格布局（时间、股票、类型、数量、价格、金额）
  - 定义 Props 接口
  - 使用 Zustand Store 获取 recentTrades 数据

- [ ] [US4-002] [P3] [US4] 实现交易历史数据加载 (frontend/src/components/trading/TradeHistory.tsx)
  - 使用 useEffect 加载交易历史
  - 支持分页加载（每页 20 条）
  - 处理加载状态和错误状态
  - 显示"暂无交易记录"占位符

- [ ] [US4-003] [P3] [US4] 实现筛选功能 (frontend/src/components/trading/TradeHistory.tsx)
  - 添加股票代码筛选输入框
  - 添加交易类型筛选（全部/买入/卖出）
  - 实时过滤交易记录
  - 显示筛选结果数量

- [ ] [US4-004] [P3] [US4] 实现无限滚动加载 (frontend/src/components/trading/TradeHistory.tsx)
  - 检测滚动到底部
  - 自动加载下一页数据
  - 显示"加载更多"指示器
  - 处理"没有更多数据"状态

- [ ] [US4-005] [P3] [US4] 实现交易记录样式 (frontend/src/components/trading/TradeHistory.tsx)
  - 买入/卖出类型使用不同颜色标识
  - 格式化时间显示（使用 date-fns）
  - 格式化货币和数量显示
  - 添加悬停效果

- [ ] [US4-006] [P3] [US4] 集成交易历史到主页 (frontend/src/app/trading/page.tsx)
  - 在底部"交易历史"标签页中渲染 TradeHistory
  - 交易成功后自动刷新历史记录

### 测试任务

- [ ] [US4-TEST-001] [P3] [US4] 编写 TradeHistory 组件单元测试 (frontend/__tests__/components/trading/TradeHistory.test.tsx)
  - 测试交易记录正确显示
  - 测试筛选功能
  - 测试分页加载
  - 测试时间格式化
  - Mock recentTrades 数据

- [ ] [US4-E2E-001] [P3] [US4] 编写交易历史 E2E 测试 (frontend/__tests__/e2e/trade-history.spec.ts)
  - 测试交易后历史记录更新
  - 测试筛选功能交互
  - 测试滚动加载更多记录
  - 测试按时间倒序显示

---

## Phase 7: Polish & Cross-Cutting Concerns

### 性能优化任务

- [ ] [POLISH-001] [P2] 优化 K线图表性能 (frontend/src/components/trading/CandlestickChart.tsx)
  - 使用 React.memo 避免不必要的重渲染
  - 使用 useMemo 缓存图表配置
  - 使用 useCallback 缓存事件处理函数
  - 优化大数据量渲染（虚拟化、数据抽样）

- [ ] [POLISH-002] [P2] 优化持仓列表性能 (frontend/src/components/trading/HoldingsList.tsx)
  - 使用 React.memo 缓存列表项组件
  - 使用 useMemo 缓存盈亏计算结果
  - 使用虚拟滚动处理大量持仓（如 > 50 条）

- [ ] [POLISH-003] [P2] 优化交易历史性能 (frontend/src/components/trading/TradeHistory.tsx)
  - 使用 React.memo 缓存列表项组件
  - 使用虚拟滚动处理大量历史记录
  - 优化筛选性能（使用 useMemo）

### 用户体验优化任务

- [ ] [POLISH-004] [P2] 实现全局 Toast 通知系统 (frontend/src/components/ui/Toast.tsx)
  - 创建 Toast 组件和 Context
  - 支持成功/错误/警告/信息类型
  - 自动消失（可配置时长）
  - 支持多个 Toast 堆叠显示

- [ ] [POLISH-005] [P2] 集成 Toast 通知到交易流程
  - 交易成功后显示成功 Toast
  - 交易失败后显示错误 Toast
  - API 请求失败时显示错误 Toast
  - 替换 console.log 为 Toast 通知

- [ ] [POLISH-006] [P2] 实现 Error Boundary (frontend/src/components/ErrorBoundary.tsx)
  - 捕获组件树错误
  - 显示友好的错误页面
  - 提供"重新加载"按钮
  - 记录错误日志（可选）

- [ ] [POLISH-007] [P2] 优化加载状态显示
  - 统一所有组件的 Loading UI（骨架屏）
  - 添加加载动画
  - 避免加载闪烁（debounce loading state）

- [ ] [POLISH-008] [P2] 实现键盘快捷键
  - 全局快捷键：Ctrl/Cmd + K 聚焦搜索框
  - 列表导航：上下方向键选择股票
  - 交易面板：B 键切换买入，S 键切换卖出
  - 记录快捷键帮助文档

### 无障碍访问任务

- [ ] [POLISH-009] [P2] 添加 ARIA 标签
  - 所有交互元素添加 aria-label
  - 表单输入添加 aria-describedby（错误提示）
  - 对话框添加 aria-modal 和 role="dialog"
  - 列表添加 role="list" 和 role="listitem"

- [ ] [POLISH-010] [P2] 优化键盘导航
  - 确保所有交互元素可通过 Tab 键访问
  - 实现焦点陷阱（Focus Trap）在对话框中
  - 添加 :focus-visible 样式
  - 测试屏幕阅读器兼容性

### 代码质量任务

- [ ] [POLISH-011] [P3] 添加 TypeScript 严格模式检查
  - 修复所有 TypeScript 警告
  - 移除所有 @ts-ignore 注释
  - 确保所有 Props 和状态有明确类型

- [ ] [POLISH-012] [P3] 代码审查和重构
  - 提取重复逻辑为自定义 Hook 或工具函数
  - 优化组件结构（拆分过大组件）
  - 统一命名规范
  - 添加代码注释

- [ ] [POLISH-013] [P3] 添加 ESLint 和 Prettier 配置
  - 配置 ESLint 规则
  - 配置 Prettier 格式化
  - 修复所有 Lint 错误
  - 运行格式化

### 文档任务

- [ ] [POLISH-014] [P3] 编写组件文档
  - 为每个组件添加 JSDoc 注释
  - 记录 Props 接口和用法
  - 添加使用示例

- [ ] [POLISH-015] [P3] 更新 README
  - 记录项目启动步骤
  - 记录技术栈和依赖
  - 记录开发工作流
  - 添加截图和演示

---

## Task Dependencies

### 依赖关系图

```
Phase 1 (Setup) [已完成]
  ↓
Phase 2 (US1 - K线图表) [P1]
  ├── US1-001 (useDebounce) ← 被 US5-002 依赖
  ├── US1-002 (useChart) ← 被 US1-003 依赖
  ├── US1-003 (图表骨架) ← 被 US1-004, US1-005 依赖
  ├── US1-004 (数据加载) ← 被 US1-005 依赖
  ├── US1-005 (系列渲染) ← 被 US1-006, US1-007 依赖
  ├── US1-006 (时间周期切换)
  ├── US1-007 (悬停数据显示)
  ├── US1-008 (交互功能)
  └── US1-009 (加载状态)

Phase 3 (US2 - 交易执行) [P1]
  ├── US2-001 (useTrade) ← 被 US2-006 依赖
  ├── US2-002 (确认对话框) ← 被 US2-006 依赖
  ├── US2-003 (交易面板骨架) ← 被 US2-004, US2-005 依赖
  ├── US2-004 (表单状态管理) ← 被 US2-005, US2-006 依赖
  ├── US2-005 (表单验证) ← 被 US2-006 依赖
  ├── US2-006 (交易提交) ← 被 US2-007, US2-008 依赖
  ├── US2-007 (预估金额)
  └── US2-008 (交互优化)

Phase 4 (US5 - 股票搜索) [P2] ← 依赖 US1-001 (useDebounce)
  ├── US5-001 (搜索组件骨架) ← 被 US5-002, US5-003 依赖
  ├── US5-002 (搜索状态管理) ← 被 US5-003 依赖
  ├── US5-003 (搜索 API) ← 被 US5-004 依赖
  ├── US5-004 (搜索结果显示) ← 被 US5-005 依赖
  ├── US5-005 (股票选择逻辑)
  ├── US5-006 (列表项组件)
  └── US5-007 (集成到主页)

Phase 5 (US3 - 持仓列表) [P2]
  ├── US3-001 (盈亏指示器) ← 被 US3-004 依赖
  ├── US3-002 (持仓列表骨架) ← 被 US3-003, US3-004 依赖
  ├── US3-003 (数据加载) ← 被 US3-004 依赖
  ├── US3-004 (盈亏计算) ← 被 US3-005, US3-006 依赖
  ├── US3-005 (排序功能)
  ├── US3-006 (点击切换股票)
  ├── US3-007 (实时价格更新)
  └── US3-008 (集成到主页)

Phase 6 (US4 - 交易历史) [P3]
  ├── US4-001 (历史组件骨架) ← 被 US4-002 依赖
  ├── US4-002 (数据加载) ← 被 US4-003, US4-004 依赖
  ├── US4-003 (筛选功能)
  ├── US4-004 (无限滚动)
  ├── US4-005 (交易记录样式)
  └── US4-006 (集成到主页)

Phase 7 (Polish) [P2/P3]
  ├── POLISH-001~003 (性能优化) ← 依赖对应组件完成
  ├── POLISH-004~005 (Toast 通知)
  ├── POLISH-006 (Error Boundary)
  ├── POLISH-007 (加载状态优化)
  ├── POLISH-008 (键盘快捷键)
  ├── POLISH-009~010 (无障碍访问)
  ├── POLISH-011~013 (代码质量)
  └── POLISH-014~015 (文档)
```

### 并行执行建议

以下任务可以并行执行（无直接依赖）：

**Phase 2 内并行**:
- US1-006, US1-007, US1-008, US1-009（在 US1-005 完成后）

**Phase 3 内并行**:
- US2-001, US2-002 可并行开发
- US2-007, US2-008（在 US2-006 完成后）

**跨 Phase 并行**:
- Phase 2 (US1) 和 Phase 3 (US2) 的初始任务可并行（US1-001~US1-003 与 US2-001~US2-003）
- Phase 4 (US5) 可在 US1-001 完成后立即开始
- Phase 5 (US3) 和 Phase 6 (US4) 完全独立，可并行开发

---

## Testing Strategy

### 测试覆盖目标

- **单元测试覆盖率**: > 80%
- **关键路径覆盖率**: 100%
- **E2E 测试**: 覆盖所有用户场景

### 测试执行顺序

1. **Phase 2-6**: 每个 Phase 完成实现任务后立即执行对应的测试任务
2. **集成测试**: 所有组件完成后执行完整的集成测试
3. **E2E 测试**: 在本地和 CI 环境中执行

### 关键测试场景

- ✅ 完整交易流程（选股 → 查看图表 → 执行交易 → 查看持仓/历史）
- ✅ 错误处理（余额不足、持仓不足、网络失败）
- ✅ 实时数据更新（价格变化、盈亏计算）
- ✅ 用户交互（搜索、筛选、排序、分页）

---

## Success Criteria Verification

完成所有任务后，验证以下成功标准：

- [ ] SC-001: 交易流程 < 30 秒
- [ ] SC-002: K线图表加载 < 1 秒
- [ ] SC-003: 持仓盈亏更新 < 500 毫秒
- [ ] SC-004: 搜索结果显示 < 300 毫秒
- [ ] SC-005: 交易执行成功率 100%
- [ ] SC-006: 1920x1080 分辨率无布局错乱
- [ ] SC-007: 90% 用户无需帮助即可完成交易
- [ ] SC-008: 支持 50+ 股票列表流畅滚动
- [ ] SC-009: 交易确认 < 2 秒完成
- [ ] SC-010: 交互响应 < 100 毫秒

---

## Task Statistics

- **总任务数**: 79
  - 实现任务: 54
  - 测试任务: 13
  - 性能优化: 3
  - 用户体验优化: 5
  - 无障碍访问: 2
  - 代码质量: 3
  - 文档: 2

- **按优先级统计**:
  - P1: 26 任务（US1 + US2）
  - P2: 38 任务（US3 + US5 + 部分 Polish）
  - P3: 15 任务（US4 + 部分 Polish）

- **预估工作量** (按 Story Points):
  - US1: 13 SP
  - US2: 13 SP
  - US3: 13 SP
  - US4: 10 SP
  - US5: 10 SP
  - Polish: 15 SP
  - **总计**: 74 SP

---

## Notes

1. **已完成的基础设施** (Phase 1) 为后续开发提供了坚实基础，可直接开始组件实现
2. **优先级建议**: 按 P1 → P2 → P3 顺序执行，确保核心功能优先完成
3. **并行开发**: 多个 Phase 可并行开发，参考依赖关系图合理分配任务
4. **测试驱动**: 建议每完成一个组件立即编写测试，而不是等到所有实现完成后
5. **性能优先**: Phase 2 和 Phase 3 (P1 任务) 应优先优化性能，确保满足性能目标
6. **K线数据 API**: 当前后端未提供 K线数据端点，需在实现 US1-004 前确认后端支持或使用 Mock 数据

---

**Last Updated**: 2025-10-24
