# WebSocket 分级推送使用指南

## 📋 方案概述

**方案A: 分级推送** - 后端高频推送(3秒),前端智能节流

### 核心特性

- ✅ **后端**: 3秒推送一次 (符合A股行情习惯)
- ✅ **前端**: 根据页面场景自动调整接收频率
- ✅ **智能降频**: 页面失焦自动切换到60秒
- ✅ **全局共享**: 单个WebSocket连接,多组件共享数据

---

## 🎯 推送频率分级

| 频率级别 | 间隔 | 适用场景 | 说明 |
|---------|------|---------|------|
| **REALTIME** | 1秒 | 交易页面、下单页 | 需要实时响应用户交易操作 |
| **NORMAL** | 3秒 | 市场页面、行情列表 | 默认频率,符合A股习惯 |
| **SLOW** | 10秒 | K线图、详情页 | 图表刷新不需要太频繁 |
| **LAZY** | 60秒 | 后台/失焦状态 | 节省资源 |

---

## 🚀 快速开始

### 1. 在 `_app.tsx` 中配置 Provider

```tsx
// frontend/src/pages/_app.tsx (Pages Router)
// 或 frontend/src/app/layout.tsx (App Router)

import { WebSocketProvider } from '@/contexts/WebSocketContext';

export default function App({ Component, pageProps }) {
  return (
    <WebSocketProvider 
      autoConnect={true}           // 自动连接
      autoAdjustThrottle={true}    // 根据路径自动调整频率
    >
      <Component {...pageProps} />
    </WebSocketProvider>
  );
}
```

### 2. 在组件中使用 Context

#### 方式一: 使用全局市场数据

```tsx
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export default function MarketPage() {
  const { marketData, isConnected, currentThrottle } = useWebSocketContext();

  if (!isConnected) {
    return <div>连接中...</div>;
  }

  return (
    <div>
      <p>当前刷新频率: {currentThrottle}ms</p>
      <p>股票数量: {marketData?.stocks.length}</p>
      
      <ul>
        {marketData?.stocks.map(stock => (
          <li key={stock.symbol}>
            {stock.name}: ¥{stock.current_price} 
            ({stock.change_pct > 0 ? '+' : ''}{stock.change_pct.toFixed(2)}%)
          </li>
        ))}
      </ul>
    </div>
  );
}
```

#### 方式二: 获取单只股票数据

```tsx
import { useStockData } from '@/contexts/WebSocketContext';

export default function StockCard({ symbol }: { symbol: string }) {
  const stock = useStockData(symbol);

  if (!stock) {
    return <div>加载中...</div>;
  }

  return (
    <div className="stock-card">
      <h3>{stock.name} ({stock.symbol})</h3>
      <p className="price">¥{stock.current_price.toFixed(2)}</p>
      <p className={stock.change_pct >= 0 ? 'up' : 'down'}>
        {stock.change_pct >= 0 ? '↑' : '↓'} {stock.change_pct.toFixed(2)}%
      </p>
    </div>
  );
}
```

#### 方式三: 获取多只股票数据 (自选股)

```tsx
import { useStocksData } from '@/contexts/WebSocketContext';

export default function WatchList() {
  const symbols = ['600001', '000002', '000333']; // 自选股列表
  const stocks = useStocksData(symbols);

  return (
    <div className="watchlist">
      {stocks.map(stock => (
        <div key={stock.symbol}>
          {stock.name}: ¥{stock.current_price}
        </div>
      ))}
    </div>
  );
}
```

---

## ⚙️ 高级用法

### 手动控制节流间隔

```tsx
import { useWebSocketContext, PUSH_INTERVALS } from '@/contexts/WebSocketContext';

export default function TradePage() {
  const { setThrottle } = useWebSocketContext();

  // 进入交易模式时,切换到1秒实时推送
  const handleStartTrading = () => {
    setThrottle(PUSH_INTERVALS.REALTIME);
  };

  // 退出交易模式时,恢复到3秒正常推送
  const handleStopTrading = () => {
    setThrottle(PUSH_INTERVALS.NORMAL);
  };

  return (
    <div>
      <button onClick={handleStartTrading}>开始交易 (1秒)</button>
      <button onClick={handleStopTrading}>观望模式 (3秒)</button>
    </div>
  );
}
```

### 订阅单只股票详情

```tsx
import { useEffect } from 'react';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export default function StockDetailPage({ symbol }: { symbol: string }) {
  const { subscribeStock, unsubscribeStock } = useWebSocketContext();

  useEffect(() => {
    // 进入详情页时订阅
    subscribeStock(symbol);

    // 离开详情页时取消订阅
    return () => {
      unsubscribeStock(symbol);
    };
  }, [symbol, subscribeStock, unsubscribeStock]);

  return <div>股票详情页 - {symbol}</div>;
}
```

### 直接使用 Hook (不使用 Context)

```tsx
import { useWebSocket, PUSH_INTERVALS } from '@/hooks/useWebSocket';

export default function CustomComponent() {
  const { data, isConnected } = useWebSocket('/ws/market', {
    throttle: PUSH_INTERVALS.REALTIME,  // 自定义频率
    autoConnect: true,
    autoSlowDownOnBlur: true,
  });

  return <div>{/* ... */}</div>;
}
```

---

## 🎨 路径自动调整规则

当启用 `autoAdjustThrottle={true}` 时,系统会根据当前路径自动调整推送频率:

| 路径模式 | 频率 | 示例 |
|---------|------|------|
| `/trade/*`, `/order/*` | 1秒 | `/trade/buy`, `/order/list` |
| `/market/*`, `/stocks/*` | 3秒 | `/market`, `/stocks/list` |
| `/chart/*`, `/detail/*` | 10秒 | `/chart/600001`, `/detail/stock` |
| 其他 | 60秒 | `/about`, `/settings` |

---

## 📊 页面可见性自动降频

当页面失焦(切换标签页、最小化窗口)时:
- ✅ 自动切换到 **60秒** 推送
- ✅ 恢复焦点后自动恢复到原始频率
- ✅ 节省服务器和客户端资源

```tsx
// 自动启用,无需手动配置
<WebSocketProvider autoConnect={true}>
  {children}
</WebSocketProvider>
```

---

## 🔍 调试模式

开启调试日志:

```tsx
import { useWebSocket } from '@/hooks/useWebSocket';

const { data } = useWebSocket('/ws/market', {
  debug: true,  // 开启调试日志
});
```

控制台输出示例:
```
[useWebSocket] Connecting to ws://localhost:8000/api/v1/ws/market
[useWebSocket] Connected
[useWebSocket] Heartbeat sent
[useWebSocket] Message received: market_update
[useWebSocket] Data updated (immediate) [100 stocks]
[useWebSocket] Page hidden, switching to LAZY mode
```

---

## 🛠️ 环境变量配置

```bash
# .env.local
NEXT_PUBLIC_WS_HOST=localhost:8000
```

生产环境:
```bash
NEXT_PUBLIC_WS_HOST=api.happystock.com
```

---

## 📈 性能优化建议

### 1. 按需渲染

```tsx
// ✅ 好: 使用 React.memo 避免不必要的重渲染
const StockItem = React.memo(({ stock }) => {
  return <div>{stock.name}: {stock.current_price}</div>;
});

// ❌ 差: 每次数据更新都会重渲染所有子组件
```

### 2. 虚拟列表

```tsx
// 对于100只股票的列表,使用虚拟滚动
import { FixedSizeList } from 'react-window';

const Row = ({ index, style, data }) => (
  <div style={style}>
    {data[index].name}: {data[index].current_price}
  </div>
);

<FixedSizeList
  height={600}
  itemCount={stocks.length}
  itemSize={50}
  itemData={stocks}
>
  {Row}
</FixedSizeList>
```

### 3. 选择性更新

```tsx
// 只订阅关注的股票,而不是全市场
const watchlist = ['600001', '000002', '000333'];
const stocks = useStocksData(watchlist); // 只获取3只股票
```

---

## ✅ 最佳实践

1. **全局使用 Context** - 大多数场景使用 `WebSocketProvider`
2. **按需订阅** - 详情页订阅单只股票,列表页订阅全市场
3. **信任自动降频** - 让系统根据场景自动调整频率
4. **避免重复连接** - 一个应用只需一个 WebSocket 连接
5. **性能优化** - 大列表使用虚拟滚动,组件使用 memo

---

## 🐛 常见问题

### Q1: 为什么连接不上?

检查后端是否启动:
```bash
curl http://localhost:8000/health
```

检查 WebSocket 端口:
```bash
curl http://localhost:8000/api/v1/ws/stats
```

### Q2: 数据不更新?

1. 检查 `isConnected` 状态
2. 查看控制台是否有错误
3. 开启 `debug: true` 查看详细日志

### Q3: 如何测试不同频率?

```tsx
const { setThrottle } = useWebSocketContext();

// 测试1秒推送
setThrottle(1000);

// 测试10秒推送
setThrottle(10000);
```

---

## 📦 完整示例

查看完整示例代码:
- `frontend/src/app/market/page.tsx` - 市场页面
- `frontend/src/components/StockList.tsx` - 股票列表
- `frontend/src/components/StockCard.tsx` - 股票卡片

---

**更新时间**: 2025-10-29  
**方案版本**: A - 分级推送  
**状态**: ✅ 已实现
