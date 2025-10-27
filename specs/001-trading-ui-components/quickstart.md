# Quickstart: TradingView 风格交易界面核心组件

**Feature**: 001-trading-ui-components
**Date**: 2025-10-24

## Prerequisites

确保已完成以下步骤：

1. **后端服务运行中**:
   ```bash
   cd backend
   pipenv run python main.py
   # 应该看到: Uvicorn running on http://0.0.0.0:8000
   ```

2. **前端开发服务器运行中**:
   ```bash
   cd frontend
   npm run dev
   # 应该看到: Ready on http://localhost:3000
   ```

3. **已安装依赖**:
   - Lightweight Charts: `npm install lightweight-charts`
   - Zustand: `npm install zustand`
   - Axios: `npm install axios`
   - date-fns: `npm install date-fns`
   - clsx: `npm install clsx`

---

## Development Workflow

### Step 1: 创建组件文件

```bash
cd frontend/src/components/trading
touch CandlestickChart.tsx TradePanel.tsx HoldingsList.tsx TradeHistory.tsx StockSearch.tsx
```

### Step 2: 实现组件（按优先级）

#### Priority P1: K线图表组件

**文件**: `frontend/src/components/trading/CandlestickChart.tsx`

**关键功能**:
- 使用 Lightweight Charts 渲染 K线图
- 支持时间周期切换（日/周/月）
- 鼠标悬停显示详细数据
- 支持拖动和缩放

**开发步骤**:
1. 创建组件骨架
2. 初始化 Lightweight Charts 实例
3. 实现数据加载和更新逻辑
4. 添加交互功能（缩放、拖动）
5. 编写单元测试

---

#### Priority P1: 交易面板组件

**文件**: `frontend/src/components/trading/TradePanel.tsx`

**关键功能**:
- 买入/卖出Tab切换
- 表单输入（股票代码、价格、数量）
- 表单验证
- 交易确认对话框
- 提交交易

**开发步骤**:
1. 创建表单UI
2. 实现表单验证逻辑
3. 连接 Zustand Store
4. 实现确认对话框
5. 处理成功/失败状态
6. 编写单元测试

---

#### Priority P2: 持仓列表组件

**文件**: `frontend/src/components/trading/HoldingsList.tsx`

**关键功能**:
- 显示所有持仓
- 实时计算盈亏
- 颜色区分盈亏状态
- 支持排序
- 点击切换到该股票

**开发步骤**:
1. 创建列表UI
2. 实现盈亏计算逻辑
3. 添加排序功能
4. 实现点击事件
5. 编写单元测试

---

#### Priority P2: 股票搜索组件

**文件**: `frontend/src/components/trading/StockSearch.tsx`

**关键功能**:
- 搜索框输入
- 防抖处理（300ms）
- 实时显示搜索结果
- 点击选择股票

**开发步骤**:
1. 创建搜索UI
2. 实现防抖Hook
3. 连接搜索API
4. 显示搜索结果
5. 编写单元测试

---

#### Priority P3: 交易历史组件

**文件**: `frontend/src/components/trading/TradeHistory.tsx`

**关键功能**:
- 显示交易记录
- 支持筛选（股票、类型）
- 分页加载
- 滚动到底部加载更多

**开发步骤**:
1. 创建列表UI
2. 实现筛选逻辑
3. 实现分页加载
4. 添加无限滚动
5. 编写单元测试

---

### Step 3: 集成到主页面

**文件**: `frontend/src/app/trading/page.tsx`

用实际组件替换占位符：

```tsx
import CandlestickChart from '@/components/trading/CandlestickChart';
import TradePanel from '@/components/trading/TradePanel';
import HoldingsList from '@/components/trading/HoldingsList';
import TradeHistory from '@/components/trading/TradeHistory';
import StockSearch from '@/components/trading/StockSearch';

// 替换占位符...
```

---

### Step 4: 测试

#### 运行单元测试

```bash
npm test -- components/trading
```

#### 运行 E2E 测试

```bash
npm run test:e2e
```

#### 手动测试清单

- [ ] K线图表正确显示
- [ ] 时间周期切换正常
- [ ] 买入交易成功执行
- [ ] 卖出交易成功执行
- [ ] 持仓列表正确显示
- [ ] 盈亏计算准确
- [ ] 搜索功能正常
- [ ] 交易历史正确显示
- [ ] 错误提示友好

---

## Quick Commands

```bash
# 启动开发环境
npm run dev

# 运行测试
npm test

# 类型检查
npm run type-check

# Lint 检查
npm run lint

# 构建生产版本
npm run build
```

---

## Common Issues

### 1. Lightweight Charts 初始化失败

**Solution**: 确保组件使用 `'use client'` 指令，并在 `useEffect` 中初始化图表。

### 2. API 请求失败

**Solution**: 检查后端服务是否运行，检查 CORS 配置。

### 3. 状态更新不生效

**Solution**: 检查 Zustand Store 是否正确使用 selector。

---

## Next Steps

完成组件开发后：

1. 运行 `/speckit.tasks` 生成详细任务清单
2. 按优先级实施任务
3. 持续测试和优化
4. 准备部署

---

## Resources

- [Lightweight Charts 文档](https://tradingview.github.io/lightweight-charts/)
- [Zustand 文档](https://docs.pmnd.rs/zustand/)
- [Next.js 文档](https://nextjs.org/docs)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
