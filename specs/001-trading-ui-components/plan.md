# Implementation Plan: P0 图表核心体验优化

**Branch**: `001-trading-ui-components` | **Date**: 2025-10-27 | **Spec**: [spec.md](./spec.md)
**Input**: P0优先级任务 - K线倒计时功能、动态数据加载优化、线形图

## Summary

本计划专注于三个最高优先级的图表核心体验功能：
1. **K线倒计时**：在最后一根K线上实时显示倒计时，支持所有时间周期
2. **动态数据加载**：监听图表滑动/缩放事件，智能加载历史和最新数据，性能优化
3. **线形图**：添加图表类型切换，支持蜡烛图⇄线形图平滑切换

这三个功能直接提升用户体验和系统性能，是打造专业级K线图表工具的关键。

## Technical Context

**Language/Version**: TypeScript 5+, React 19, Next.js 15.4
**Primary Dependencies**: lightweight-charts 5.x, React Hooks
**Storage**: LocalStorage (用户偏好), IndexedDB (数据缓存)
**Testing**: Jest + React Testing Library
**Target Platform**: Web (Chrome/Firefox/Safari)
**Project Type**: Web application (frontend重点)
**Performance Goals**:
- 倒计时刷新延迟 < 50ms
- 滑动加载响应 < 100ms
- 数据缓存命中率 > 80%
- 图表切换无闪烁

**Constraints**:
- 倒计时必须精确到秒
- 防抖处理避免频繁请求
- 内存占用 < 500MB
- 支持所有时间周期 (5m/15m/30m/60m/120m/1d/1w/1M)

**Scale/Scope**:
- 单个图表最多显示1000根K线
- 缓存最多10只股票的历史数据
- 支持3种图表类型

## Constitution Check

*GATE: 项目宪法文件为模板状态，暂无具体规则需要验证*

**Status**: ✅ PASS (no constitution rules defined yet)

## Project Structure

### Documentation (this feature)

```text
specs/001-trading-ui-components/
├── plan.md              # This file
├── research.md          # Phase 0: 技术方案研究
├── data-model.md        # Phase 1: 数据模型设计
├── quickstart.md        # Phase 1: 快速开始指南
├── contracts/           # Phase 1: API契约
└── tasks.md             # Phase 2: 待生成 (by /speckit.tasks)
```

### Source Code (repository root)

```text
# Web application structure (frontend focused)
frontend/
├── src/
│   ├── components/
│   │   └── trading/
│   │       ├── CandlestickChart.tsx      # 主K线图组件 (需修改)
│   │       ├── MACDChart.tsx             # MACD子图 (已存在)
│   │       └── KlineCountdown.tsx        # 倒计时组件 (新建)
│   ├── hooks/
│   │   ├── useChart.ts                   # 图表Hook (已存在)
│   │   ├── useChartData.ts               # 数据加载Hook (新建)
│   │   └── useCountdown.ts               # 倒计时Hook (新建)
│   ├── lib/
│   │   ├── api/
│   │   │   └── trading.ts                # API调用 (需修改)
│   │   ├── indicators/
│   │   │   ├── ema.ts                    # EMA指标 (已存在)
│   │   │   └── macd.ts                   # MACD指标 (已存在)
│   │   └── utils/
│   │       ├── timeUtils.ts              # 时间工具 (新建)
│   │       └── cacheUtils.ts             # 缓存工具 (新建)
│   └── types/
│       └── chart.ts                      # 图表类型定义 (新建)
└── tests/
    ├── components/
    │   └── trading/
    │       ├── CandlestickChart.test.tsx
    │       └── KlineCountdown.test.tsx
    └── hooks/
        ├── useChartData.test.ts
        └── useCountdown.test.ts

backend/
├── routers/
│   └── klines.py                         # K线API (需修改 - 支持范围查询)
└── tests/
    └── test_klines.py
```

**Structure Decision**: 采用 Web application 结构，前端使用 Next.js + React，后端使用 FastAPI。P0任务主要在前端实现，后端只需扩展API支持时间范围查询。

## Complexity Tracking

> 无宪法违规，此部分留空

## Phase 0: Outline & Research

### Research Tasks

以下是需要研究的技术点，将在 `research.md` 中详细记录：

1. **倒计时实现方案**
   - lightweight-charts 如何在图表上叠加自定义UI元素
   - 使用 Marker、Price Line 还是 Custom Primitive
   - setInterval vs requestAnimationFrame 性能对比
   - 如何确保倒计时与最后一根K线位置对齐

2. **动态数据加载策略**
   - lightweight-charts 的 `subscribeVisibleLogicalRangeChange` API
   - 防抖/节流最佳实践（lodash vs 自实现）
   - IndexedDB vs LocalStorage 缓存方案选择
   - 数据合并策略（新旧数据如何无缝拼接）
   - 边界检测（已到达历史最早/最新数据）

3. **线形图切换**
   - 从 CandlestickSeries 切换到 LineSeries 的最佳实践
   - 如何保留缩放位置和技术指标
   - LocalStorage 用户偏好存储模式
   - 动画过渡效果实现

4. **性能优化**
   - React 组件重渲染优化（useMemo, useCallback）
   - 大数据量图表渲染优化
   - 内存泄漏预防（定时器清理、事件监听器清理）

### Next Steps

1. 创建 `research.md` 文档，记录上述研究结果
2. 完成研究后，进入 Phase 1 设计数据模型和API契约
3. Phase 1 后，运行 `/speckit.tasks` 生成具体实现任务

---

*Created: 2025-10-27 | Status: Phase 0 - Research Pending*
