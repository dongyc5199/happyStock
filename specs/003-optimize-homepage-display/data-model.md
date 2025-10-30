# Data Model: Optimize Homepage Display

**Feature**: 003-optimize-homepage-display  
**Phase**: 1 - Design & Contracts  
**Date**: 2025-01-30

## Overview

This document defines the data structures and entities used in the homepage optimization feature. Since this is a frontend-only feature leveraging existing backend APIs, most entities are TypeScript interfaces for client-side state management.

## Core Entities

### 1. MarketOverview (Existing - Reused)

**Source**: `/api/v1/market/overview` endpoint  
**Description**: Aggregated market statistics displayed in the Market Overview section.

```typescript
interface MarketOverview {
  // Stock counts
  total_stocks: number;        // Total number of active stocks
  rising: number;              // Count of stocks with positive change_pct
  falling: number;             // Count of stocks with negative change_pct
  unchanged: number;           // Count of stocks with zero change_pct
  limit_up: number;            // Count of stocks with change_pct >= 9.9%
  limit_down: number;          // Count of stocks with change_pct <= -9.9%
  
  // Trading volume
  total_volume: number;        // Aggregate trading volume (shares)
  total_turnover: number;      // Aggregate turnover (CNY)
  
  // Market state
  market_state: '牛市' | '熊市' | '震荡';  // Bull/Bear/Sideways
  market_trend: number;        // Daily trend indicator
}
```

**Usage**:
- Displayed in "市场概况" section (hero area)
- Updated via initial SSR fetch, no WebSocket needed (static for session)

---

### 2. StockData (Existing - Reused)

**Source**: WebSocket `/ws/market` stream  
**Description**: Real-time data for individual stocks, used for Hot Stock lists.

```typescript
interface StockData {
  symbol: string;              // Stock code (e.g., "000001")
  name: string;                // Stock name (e.g., "开心银行")
  sector: string;              // Sector code (e.g., "FINANCE")
  current_price: number;       // Current price (CNY)
  previous_close: number;      // Previous close price
  change_value: number;        // Absolute price change
  change_pct: number;          // Percentage change (e.g., 5.2 for +5.2%)
  volume: number;              // Trading volume (shares)
  turnover: number;            // Turnover (CNY)
  timestamp: number;           // Unix timestamp (milliseconds)
}
```

**Usage**:
- WebSocket stream provides array: `marketData.stocks: StockData[]`
- Client-side filtering/sorting for Hot Stock lists
- Real-time updates every 1 second (PUSH_INTERVALS.REALTIME on homepage)

---

### 3. HotStock (New - Client-side Derived)

**Source**: Derived from `StockData[]` via client-side sorting  
**Description**: Processed stock data for Top Gainers/Losers/Most Active lists.

```typescript
interface HotStock {
  symbol: string;              // Stock code
  name: string;                // Stock name
  current_price: number;       // Current price
  change_pct: number;          // Percentage change
  change_value: number;        // Absolute change
  volume: number;              // Trading volume
  turnover: number;            // Turnover
  trend: 'up' | 'down' | 'flat';  // Derived from change_pct (>0, <0, ==0)
  sparklineData?: number[];    // Last 20 price points for mini chart (optional)
}

// Sorting utility types
type HotStockCategory = 'gainers' | 'losers' | 'active';

interface HotStockLists {
  gainers: HotStock[];         // Top 5 by change_pct (positive)
  losers: HotStock[];          // Top 5 by change_pct (negative, absolute)
  active: HotStock[];          // Top 10 by turnover
}
```

**Derivation Logic**:
```typescript
function deriveHotStocks(stocks: StockData[]): HotStockLists {
  // Filter valid stocks
  const validStocks = stocks.filter(s => 
    s.volume >= 100 && s.current_price > 0
  );
  
  // Top gainers: sort by change_pct DESC
  const gainers = validStocks
    .filter(s => s.change_pct > 0)
    .sort((a, b) => b.change_pct - a.change_pct)
    .slice(0, 5)
    .map(toHotStock);
  
  // Top losers: sort by change_pct ASC (most negative)
  const losers = validStocks
    .filter(s => s.change_pct < 0)
    .sort((a, b) => a.change_pct - b.change_pct)
    .slice(0, 5)
    .map(toHotStock);
  
  // Most active: sort by turnover DESC
  const active = validStocks
    .sort((a, b) => b.turnover - a.turnover)
    .slice(0, 10)
    .map(toHotStock);
  
  return { gainers, losers, active };
}

function toHotStock(stock: StockData): HotStock {
  return {
    ...stock,
    trend: stock.change_pct > 0 ? 'up' : stock.change_pct < 0 ? 'down' : 'flat',
    sparklineData: undefined, // Populated separately if needed
  };
}
```

**Usage**:
- Displayed in "涨跌幅榜" and "活跃股票" sections
- Re-derived every 3 seconds (cached between WebSocket updates)

---

### 4. CoreIndex (Existing - Reused)

**Source**: `/api/v1/indices?type=CORE` endpoint  
**Description**: Data for the three core market indices.

```typescript
interface CoreIndex {
  code: string;                // Index code (e.g., "HAPPY300")
  name: string;                // Index name (e.g., "开心300")
  current_value: number;       // Current index value
  change_value: number;        // Absolute change
  change_pct: number;          // Percentage change
  volume: number;              // Aggregate volume of constituents
  turnover: number;            // Aggregate turnover
  constituent_count: number;   // Number of constituent stocks
  timestamp: number;           // Unix timestamp
}
```

**Usage**:
- Displayed in "核心指数" section (3 cards with mini charts)
- Fetched via SSR on initial load
- Optional: WebSocket updates for real-time values (future enhancement)

---

### 5. FeatureCard (New - Static Data)

**Source**: Hardcoded in component  
**Description**: Metadata for the three core platform features.

```typescript
interface FeatureCard {
  id: string;                  // Unique identifier (e.g., "chart-tool")
  title: string;               // Feature name (e.g., "专业图表工具")
  description: string;         // Brief description (1-2 sentences)
  icon: React.ComponentType;   // Icon component (e.g., BarChart3 from lucide-react)
  primaryAction: {
    label: string;             // CTA text (e.g., "立即体验")
    href: string;              // Navigation URL (e.g., "/virtual-market")
  };
  secondaryAction?: {
    label: string;             // Link text (e.g., "📖 学习K线图基础")
    href: string;              // Documentation URL
  };
  color: string;               // Tailwind color class (e.g., "blue")
}
```

**Example Data**:
```typescript
const features: FeatureCard[] = [
  {
    id: 'chart-tool',
    title: '专业图表工具',
    description: 'K线图、趋势线、技术指标，打造专业级交易分析平台',
    icon: BarChart3,
    primaryAction: { label: '立即体验', href: '/virtual-market' },
    secondaryAction: { label: '📖 学习K线图基础', href: '/docs/kline-basics' },
    color: 'blue',
  },
  {
    id: 'ai-trading',
    title: 'AI模拟交易',
    description: '智能选股、策略回测、风险评估，AI助力投资决策',
    icon: Brain,
    primaryAction: { label: '开始交易', href: '/virtual-market' },
    color: 'purple',
  },
  {
    id: 'social-platform',
    title: '投资社交平台',
    description: '分享策略、跟踪高手、学习交流，共同成长进步',
    icon: Users,
    primaryAction: { label: '加入社区', href: '/social' },
    color: 'green',
  },
];
```

**Usage**:
- Displayed in "三大核心功能" section
- Static data (no API calls needed)

---

### 6. EducationResource (New - Static Data)

**Source**: Hardcoded in component (future: CMS)  
**Description**: Educational content links for user onboarding.

```typescript
interface EducationResource {
  id: string;                  // Unique identifier
  title: string;               // Article title
  description: string;         // Brief summary (1 sentence)
  category: 'beginner' | 'intermediate' | 'advanced' | 'faq';
  readingTime: number;         // Estimated reading time (minutes)
  url: string;                 // Internal route or external link
  relatedFeature?: 'chart' | 'ai' | 'social';  // For contextual linking
}
```

**Example Data**:
```typescript
const educationResources: EducationResource[] = [
  {
    id: 'kline-basics',
    title: 'K线图入门教程',
    description: '5分钟掌握阴阳线、趋势判断',
    category: 'beginner',
    readingTime: 5,
    url: '/docs/kline-basics',
    relatedFeature: 'chart',
  },
  {
    id: 'first-trade',
    title: '如何下第一单?',
    description: '新手交易流程详解',
    category: 'beginner',
    readingTime: 3,
    url: '/docs/first-trade',
    relatedFeature: 'ai',
  },
  // ... more resources
];
```

**Usage**:
- Displayed in footer "新手指南" section
- Contextual links within feature cards

---

## Data Flow Architecture

### Initial Page Load (SSR)

```
User requests /
    ↓
Next.js Server Component
    ↓
┌─────────────────────────────────┐
│ Parallel Fetch (Server-side):  │
│ 1. /api/v1/market/overview      │
│ 2. /api/v1/indices?type=CORE    │
└─────────────────────────────────┘
    ↓
Render HTML with initial data
    ↓
Send to client
    ↓
Client hydration begins
```

### Real-time Updates (Client-side)

```
WebSocketContext connects to /ws/market
    ↓
Receive marketData.stocks every 3s
    ↓
useMarketData hook processes data
    ↓
┌───────────────────────────────────┐
│ Client-side Processing:           │
│ 1. Filter valid stocks            │
│ 2. Sort by change_pct/turnover    │
│ 3. Derive HotStockLists           │
│ 4. Cache for 3 seconds            │
└───────────────────────────────────┘
    ↓
React state update
    ↓
Re-render HotStockList component
    ↓
CSS transition animations
```

### Component Data Dependencies

```
HomePage (Server Component)
├── HeroSection (Server Component)
│   └── [Static content]
├── MarketOverview (Server Component → Client Hydration)
│   ├── Initial: SSR data from /api/v1/market/overview
│   └── Updates: None (static for session)
├── HotStockSection (Client Component)
│   ├── Data: useMarketData() → deriveHotStocks()
│   └── Updates: WebSocket every 3s
├── CoreIndexCards (Server Component)
│   ├── Initial: SSR data from /api/v1/indices?type=CORE
│   └── Updates: None (future: WebSocket)
├── FeatureShowcase (Server Component)
│   └── Data: Static FeatureCard[]
└── QuickStartGuide (Server Component)
    └── Data: Static EducationResource[]
```

---

## State Management Strategy

### Server State (No Management Needed)
- `MarketOverview`: Fetched once, no updates
- `CoreIndex[]`: Fetched once, no updates
- Static data: Hardcoded in components

### Client State (React Context + Hooks)

```typescript
// WebSocketContext (Existing)
const WebSocketContext = createContext<{
  marketData: { stocks: StockData[] } | null;
  isConnected: boolean;
}>();

// Custom Hook: useHotStocks (New)
function useHotStocks(): HotStockLists | null {
  const { marketData } = useWebSocketContext();
  
  // Memoize to prevent re-calculation on every render
  return useMemo(() => {
    if (!marketData?.stocks) return null;
    return deriveHotStocks(marketData.stocks);
  }, [marketData?.stocks]);
}

// Custom Hook: useStockSparkline (New)
function useStockSparkline(symbol: string): number[] {
  const [priceHistory, setPriceHistory] = useState<number[]>([]);
  const { marketData } = useWebSocketContext();
  
  useEffect(() => {
    const stock = marketData?.stocks.find(s => s.symbol === symbol);
    if (!stock) return;
    
    // Keep last 20 price points
    setPriceHistory(prev => [...prev, stock.current_price].slice(-20));
  }, [marketData, symbol]);
  
  return priceHistory;
}
```

---

## Performance Considerations

### Caching Strategy
- **Hot Stock Lists**: Re-calculate every 3 seconds (align with WebSocket push)
- **Sparkline Data**: Store last 20 points per stock (20 × 100 stocks = 2000 numbers ≈ 8KB memory)
- **Component Memoization**: Use `React.memo()` for `<StockRow>` components

### Data Volume
- **WebSocket Payload**: 100 stocks × ~200 bytes = ~20KB per message
- **Frequency**: Every 3 seconds = ~7KB/s average bandwidth
- **Total Memory**: ~50KB for client state (marketData + derived lists)

### Optimization Techniques
1. **useMemo()**: Cache sort results
2. **useCallback()**: Stable event handlers
3. **React.memo()**: Prevent unnecessary re-renders
4. **Array.slice()**: Avoid mutating original data
5. **Filter early**: Remove invalid stocks before sorting

---

## Future Enhancements (Out of Scope)

- [ ] Historical sparkline data from backend (currently client-side only)
- [ ] WebSocket updates for CoreIndex values (currently SSR only)
- [ ] Persistent cache in LocalStorage for offline viewing
- [ ] Server-side sorting/filtering for large datasets (100+ stocks OK for now)

---

## References

- **API Documentation**: `backend/api/market.py`, `backend/api/indices.py`
- **WebSocket Schema**: `frontend/src/contexts/WebSocketContext.tsx`
- **Type Definitions**: `frontend/src/types/virtual-market.ts` (existing types)
