# Quick Start Guide: Homepage Optimization

**Feature**: 003-optimize-homepage-display  
**Date**: 2025-01-30  
**For**: Developers implementing the homepage optimization feature

## Prerequisites

### Required Knowledge
- Next.js 15 (App Router, Server Components, Streaming)
- React 19 (useMemo, useCallback, memo)
- TypeScript 5.0+
- Tailwind CSS v4
- WebSocket fundamentals

### Required Tools
- Node.js 18+ with npm/pnpm/yarn
- VS Code with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript and JavaScript Language Features
- Chrome DevTools (for performance profiling)

### Environment Setup
```bash
# Navigate to frontend directory
cd e:\work\code\happyStock\frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

---

## Project Structure Overview

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                         # 🔧 PRIMARY FILE TO MODIFY
│   │   └── layout.tsx                       # Already has WebSocketProvider
│   ├── components/
│   │   ├── home/                            # 🆕 NEW DIRECTORY
│   │   │   ├── HeroSection.tsx              # New component
│   │   │   ├── MarketOverview.tsx           # New component
│   │   │   ├── HotStockList.tsx             # New component
│   │   │   ├── HotStockRow.tsx              # New component
│   │   │   ├── CoreIndexCards.tsx           # New component
│   │   │   ├── FeatureShowcase.tsx          # New component
│   │   │   └── QuickStartGuide.tsx          # New component
│   │   ├── trading/
│   │   │   └── CandlestickChart.tsx         # ✅ EXISTING - Can reuse
│   │   └── ui/
│   │       ├── Badge.tsx                    # 🔧 ENHANCE
│   │       ├── Card.tsx                     # ✅ EXISTING
│   │       └── Button.tsx                   # ✅ EXISTING
│   ├── contexts/
│   │   └── WebSocketContext.tsx             # ✅ EXISTING - Already set up
│   ├── hooks/
│   │   ├── useWebSocket.ts                  # ✅ EXISTING
│   │   ├── useHotStocks.ts                  # 🆕 NEW HOOK
│   │   └── useStockSparkline.ts             # 🆕 NEW HOOK
│   ├── lib/
│   │   ├── api/
│   │   │   └── virtual-market.ts            # ✅ EXISTING - Has market/indices APIs
│   │   ├── formatters.ts                    # 🔧 ENHANCE - Add price/percentage formatters
│   │   └── constants.ts                     # 🔧 ADD - Homepage config
│   └── types/
│       └── virtual-market.ts                # ✅ EXISTING - Has MarketOverview, Index types
```

---

## Step-by-Step Implementation

### Phase 1: Setup Data Layer (30 minutes)

#### 1.1 Create Custom Hooks

**File**: `src/hooks/useHotStocks.ts`

```typescript
import { useMemo } from 'react';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import type { StockData } from '@/contexts/WebSocketContext';

export interface HotStock {
  symbol: string;
  name: string;
  current_price: number;
  change_pct: number;
  change_value: number;
  volume: number;
  turnover: number;
  trend: 'up' | 'down' | 'flat';
}

export interface HotStockLists {
  gainers: HotStock[];
  losers: HotStock[];
  active: HotStock[];
}

function toHotStock(stock: StockData): HotStock {
  return {
    symbol: stock.symbol,
    name: stock.name,
    current_price: stock.current_price,
    change_pct: stock.change_pct,
    change_value: stock.change_value,
    volume: stock.volume,
    turnover: stock.turnover,
    trend: stock.change_pct > 0 ? 'up' : stock.change_pct < 0 ? 'down' : 'flat',
  };
}

export function useHotStocks(): HotStockLists | null {
  const { marketData } = useWebSocketContext();

  return useMemo(() => {
    if (!marketData?.stocks) return null;

    // Filter valid stocks
    const validStocks = marketData.stocks.filter(
      (s) => s.volume >= 100 && s.current_price > 0
    );

    // Top gainers
    const gainers = validStocks
      .filter((s) => s.change_pct > 0)
      .sort((a, b) => b.change_pct - a.change_pct)
      .slice(0, 5)
      .map(toHotStock);

    // Top losers
    const losers = validStocks
      .filter((s) => s.change_pct < 0)
      .sort((a, b) => a.change_pct - b.change_pct)
      .slice(0, 5)
      .map(toHotStock);

    // Most active
    const active = validStocks
      .sort((a, b) => b.turnover - a.turnover)
      .slice(0, 10)
      .map(toHotStock);

    return { gainers, losers, active };
  }, [marketData?.stocks]);
}
```

#### 1.2 Add Formatters

**File**: `src/lib/formatters.ts` (create if doesn't exist)

```typescript
/**
 * Format price in CNY (e.g., 123456.78 → ¥123,456.78)
 */
export function formatPrice(value: number, decimals: number = 2): string {
  return `¥${value.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Format percentage (e.g., 5.23 → +5.23%)
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format large numbers with K/M/B suffixes
 */
export function formatNumber(value: number): string {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
}
```

---

### Phase 2: Build UI Components (2-3 hours)

#### 2.1 HeroSection

**File**: `src/components/home/HeroSection.tsx`

```tsx
import Link from 'next/link';

export function HeroSection() {
  return (
    <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-center">
          {/* Left Column (3/5 width) */}
          <div className="lg:col-span-3 text-center lg:text-left">
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-4">
              专业图表工具 + AI模拟交易 + 投资社交平台
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              零风险学习投资,掌握A股交易策略
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link
                href="/virtual-market"
                className="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                开始免费交易
              </Link>
              <button
                className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold text-lg hover:bg-gray-50 transition-colors border-2 border-blue-600"
              >
                查看功能演示
              </button>
            </div>
            <p className="mt-6 text-sm text-gray-500">
              已有 <span className="font-bold text-gray-900">1,250</span> 名用户体验虚拟交易
            </p>
          </div>

          {/* Right Column (2/5 width) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">实时市场状态</h3>
              <div className="text-4xl font-bold text-blue-600 mb-2">牛市</div>
              <div className="text-sm text-gray-500">市场趋势良好</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

#### 2.2 MarketOverview

**File**: `src/components/home/MarketOverview.tsx`

```tsx
import type { MarketOverview as MarketOverviewType } from '@/types/virtual-market';

interface MarketOverviewProps {
  initialData: MarketOverviewType;
}

interface StatCellProps {
  label: string;
  value: number | string;
  color: 'red' | 'green' | 'gray' | 'blue';
  badge?: boolean;
}

function StatCell({ label, value, color, badge = false }: StatCellProps) {
  const colorClasses = {
    red: 'text-red-600',
    green: 'text-green-600',
    gray: 'text-gray-600',
    blue: 'text-blue-600',
  };

  const badgeClasses = {
    red: 'bg-red-100 text-red-700',
    green: 'bg-green-100 text-green-700',
    gray: 'bg-gray-100 text-gray-700',
    blue: 'bg-blue-100 text-blue-700',
  };

  return (
    <div className="text-center">
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      {badge ? (
        <div className={`inline-block px-3 py-1 rounded-full text-xl font-bold ${badgeClasses[color]}`}>
          {value}
        </div>
      ) : (
        <div className={`text-3xl font-bold ${colorClasses[color]}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
      )}
    </div>
  );
}

export function MarketOverview({ initialData }: MarketOverviewProps) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">市场概况</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-6">
          <StatCell label="总股票数" value={initialData.total_stocks} color="gray" />
          <StatCell label="上涨" value={initialData.rising} color="red" />
          <StatCell label="下跌" value={initialData.falling} color="green" />
          <StatCell label="平盘" value={initialData.unchanged} color="gray" />
          <StatCell label="涨停" value={initialData.limit_up} color="red" />
          <StatCell label="跌停" value={initialData.limit_down} color="green" />
          <StatCell label="市场状态" value={initialData.market_state} color="blue" badge />
        </div>
      </div>
    </div>
  );
}
```

#### 2.3 HotStockList

**File**: `src/components/home/HotStockList.tsx`

```tsx
'use client';

import { useHotStocks, type HotStock } from '@/hooks/useHotStocks';
import { HotStockRow } from './HotStockRow';

interface HotStockListProps {
  category: 'gainers' | 'losers' | 'active';
  limit?: number;
}

const titles = {
  gainers: '涨幅榜',
  losers: '跌幅榜',
  active: '活跃股票',
};

export function HotStockList({ category, limit }: HotStockListProps) {
  const hotStockLists = useHotStocks();

  if (!hotStockLists) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">{titles[category]}</h3>
        <p className="text-gray-500 text-center py-8">加载中...</p>
      </div>
    );
  }

  const stocks = hotStockLists[category].slice(0, limit);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">{titles[category]}</h3>
      <div className="space-y-2">
        {stocks.map((stock, index) => (
          <HotStockRow key={stock.symbol} stock={stock} rank={index + 1} />
        ))}
      </div>
      {stocks.length === 0 && (
        <p className="text-gray-500 text-center py-8">暂无数据</p>
      )}
    </div>
  );
}
```

#### 2.4 HotStockRow

**File**: `src/components/home/HotStockRow.tsx`

```tsx
'use client';

import { memo } from 'react';
import Link from 'next/link';
import type { HotStock } from '@/hooks/useHotStocks';
import { formatPrice, formatPercentage } from '@/lib/formatters';

interface HotStockRowProps {
  stock: HotStock;
  rank: number;
}

export const HotStockRow = memo(function HotStockRow({ stock, rank }: HotStockRowProps) {
  const trendIcon = stock.trend === 'up' ? '▲' : stock.trend === 'down' ? '▼' : '━';
  const trendColor = stock.trend === 'up' ? 'text-red-600' : stock.trend === 'down' ? 'text-green-600' : 'text-gray-600';

  return (
    <Link
      href={`/virtual-market/stocks/${stock.symbol}`}
      className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
    >
      {/* Rank */}
      <div className="text-sm font-bold text-gray-500 w-6">{rank}</div>

      {/* Stock Info */}
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-gray-900 truncate">{stock.name}</div>
        <div className="text-xs text-gray-500">{stock.symbol}</div>
      </div>

      {/* Price */}
      <div className="text-right">
        <div className="font-bold text-gray-900">{formatPrice(stock.current_price)}</div>
        <div className={`text-sm flex items-center justify-end gap-1 ${trendColor}`}>
          <span>{trendIcon}</span>
          <span>{formatPercentage(stock.change_pct)}</span>
        </div>
      </div>
    </Link>
  );
});
```

---

### Phase 3: Update Homepage (1 hour)

**File**: `src/app/page.tsx`

```tsx
import { HeroSection } from '@/components/home/HeroSection';
import { MarketOverview } from '@/components/home/MarketOverview';
import { HotStockList } from '@/components/home/HotStockList';
import { marketApi } from '@/lib/api/virtual-market';

export default async function HomePage() {
  // SSR: Fetch initial data
  const marketResponse = await marketApi.getMarketOverview();

  return (
    <div className="min-h-screen bg-gray-50">
      <HeroSection />
      
      {marketResponse.success && marketResponse.data && (
        <MarketOverview initialData={marketResponse.data} />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <HotStockList category="gainers" limit={5} />
          <HotStockList category="losers" limit={5} />
          <HotStockList category="active" limit={10} />
        </div>
      </div>
    </div>
  );
}
```

---

## Testing Your Implementation

### 1. Visual Testing

```bash
# Start dev server
npm run dev

# Open browser
http://localhost:3000
```

**Checklist**:
- [ ] Hero section displays with correct text and CTAs
- [ ] Market overview shows 7 stats
- [ ] Hot stock lists display with real-time updates
- [ ] Layout is responsive (test at 375px, 768px, 1024px, 1440px)

### 2. Performance Testing

```bash
# Build for production
npm run build

# Start production server
npm start

# Run Lighthouse in Chrome DevTools
# Target scores: Performance 90+, Accessibility 95+, Best Practices 90+, SEO 90+
```

### 3. Unit Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

**Example test**: `src/hooks/useHotStocks.test.ts`

```typescript
import { renderHook } from '@testing-library/react';
import { useHotStocks } from './useHotStocks';
import { WebSocketProvider } from '@/contexts/WebSocketContext';

describe('useHotStocks', () => {
  it('should derive hot stock lists from market data', () => {
    const mockMarketData = {
      stocks: [
        { symbol: '000001', name: '开心银行', change_pct: 5.2, turnover: 1000000, volume: 1000, current_price: 10, previous_close: 9.5, change_value: 0.5, sector: 'FINANCE', timestamp: Date.now() },
        { symbol: '000002', name: '快乐地产', change_pct: -3.1, turnover: 800000, volume: 800, current_price: 8, previous_close: 8.3, change_value: -0.3, sector: 'REAL_ESTATE', timestamp: Date.now() },
        // ... more mock data
      ],
      timestamp: Date.now(),
    };

    const wrapper = ({ children }) => (
      <WebSocketProvider autoConnect={false}>
        {children}
      </WebSocketProvider>
    );

    const { result } = renderHook(() => useHotStocks(), { wrapper });

    expect(result.current?.gainers).toHaveLength(1);
    expect(result.current?.losers).toHaveLength(1);
    expect(result.current?.gainers[0].symbol).toBe('000001');
  });
});
```

---

## Common Issues & Troubleshooting

### Issue 1: WebSocket Not Connecting

**Symptom**: Hot stock lists show "加载中..." indefinitely

**Solution**:
1. Check if backend is running: `http://localhost:8000/docs`
2. Verify WebSocketProvider in `app/layout.tsx`:
   ```tsx
   export default function RootLayout({ children }) {
     return (
       <html lang="zh-CN">
         <body>
           <WebSocketProvider>
             {children}
           </WebSocketProvider>
         </body>
       </html>
     );
   }
   ```
3. Check browser console for WebSocket errors

### Issue 2: Hydration Error

**Symptom**: "Text content does not match server-rendered HTML"

**Solution**:
- Ensure all client components use `'use client'` directive
- Don't use `Math.random()` or `Date.now()` in SSR components
- Use `suppressHydrationWarning` for dynamic content:
  ```tsx
  <div suppressHydrationWarning>{new Date().toLocaleString()}</div>
  ```

### Issue 3: Slow Initial Load

**Symptom**: LCP > 3 seconds

**Solution**:
- Enable compression in `next.config.ts`:
  ```typescript
  module.exports = {
    compress: true,
    experimental: {
      optimizePackageImports: ['lucide-react'],
    },
  };
  ```
- Use `next/image` for all images with `priority` on above-fold images
- Check bundle size: `npm run build` → Look for large chunks

---

## Next Steps

After completing this quick start:

1. **Add Remaining Components**:
   - CoreIndexCards
   - FeatureShowcase
   - QuickStartGuide

2. **Enhance Performance**:
   - Add sparklines to HotStockRow
   - Implement flash animations on price changes
   - Add loading skeletons

3. **Add Tests**:
   - Unit tests for all hooks and components
   - E2E tests with Playwright
   - Accessibility tests with axe-core

4. **Deploy**:
   - Run production build: `npm run build`
   - Test production server: `npm start`
   - Deploy to Vercel/Netlify

---

## Resources

- **Next.js 15 Docs**: https://nextjs.org/docs
- **React 19 Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com/docs
- **WebSocket API**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **Lighthouse**: https://developer.chrome.com/docs/lighthouse

---

## Support

For questions or issues:
1. Check this guide first
2. Review `contracts/components.md` for detailed specs
3. Consult `data-model.md` for data structures
4. Ask in team Slack channel or create GitHub issue
