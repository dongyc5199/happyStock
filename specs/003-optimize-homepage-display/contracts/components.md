# Component Contracts: Homepage Optimization

**Feature**: 003-optimize-homepage-display  
**Date**: 2025-01-30

## Overview

This document defines the **interface contracts** for all new and modified components in the homepage optimization feature. Each contract specifies props, behavior, and visual requirements to ensure consistent implementation.

---

## New Components

### 1. HeroSection

**Location**: `frontend/src/components/home/HeroSection.tsx`  
**Type**: Server Component (static content)  
**Purpose**: Primary landing area showcasing platform value proposition and main CTA.

#### Props

```typescript
interface HeroSectionProps {
  // No props - fully static content
}
```

#### Behavior

- **Rendering**: Server-side rendered, no client-side state
- **Layout**: Two-column layout (60% text, 40% visual)
  - **Left**: Headline, subheadline, CTAs
  - **Right**: Live market preview component
- **Responsive**: Stack vertically on mobile (<768px)

#### Visual Requirements

```tsx
<section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-16">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-center">
      {/* Left Column (3/5 width) */}
      <div className="lg:col-span-3 text-center lg:text-left">
        <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-4">
          专业图表工具 + AI模拟交易 + 投资社交平台
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          零风险学习投资，掌握A股交易策略
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
          <PrimaryCTA />
          <SecondaryCTA />
        </div>
        <SocialProof />
      </div>

      {/* Right Column (2/5 width) */}
      <div className="lg:col-span-2">
        <LiveMarketPreview />
      </div>
    </div>
  </div>
</section>
```

#### Testing Requirements

- [ ] Renders headline, subheadline, and CTAs
- [ ] Responsive layout switches at 768px breakpoint
- [ ] CTAs link to correct routes
- [ ] Social proof displays user count

---

### 2. MarketOverview

**Location**: `frontend/src/components/home/MarketOverview.tsx`  
**Type**: Server Component → Client Hydration  
**Purpose**: Display real-time market statistics in a grid layout.

#### Props

```typescript
interface MarketOverviewProps {
  initialData: MarketOverview;  // SSR data from /api/v1/market/overview
  enableRealtime?: boolean;     // Default: false (static for MVP)
}

// MarketOverview type (from data-model.md)
interface MarketOverview {
  total_stocks: number;
  rising: number;
  falling: number;
  unchanged: number;
  limit_up: number;
  limit_down: number;
  total_volume: number;
  total_turnover: number;
  market_state: '牛市' | '熊市' | '震荡';
  market_trend: number;
}
```

#### Behavior

- **Rendering**: SSR with initial data, optional WebSocket updates
- **Layout**: Responsive grid (2 cols mobile, 4 cols tablet, 7 cols desktop)
- **Animations**: Fade-in on mount (300ms)
- **Number Formatting**:
  - Stocks count: No decimals
  - Volume/Turnover: Use `toLocaleString()` for thousands separator

#### Visual Requirements

```tsx
<div className="bg-white rounded-xl shadow-lg p-8 mb-12">
  <h3 className="text-2xl font-bold text-gray-900 mb-6">市场概况</h3>
  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-6">
    <StatCell label="总股票数" value={data.total_stocks} color="gray" />
    <StatCell label="上涨" value={data.rising} color="red" />
    <StatCell label="下跌" value={data.falling} color="green" />
    <StatCell label="平盘" value={data.unchanged} color="gray" />
    <StatCell label="涨停" value={data.limit_up} color="red" />
    <StatCell label="跌停" value={data.limit_down} color="green" />
    <StatCell label="市场状态" value={data.market_state} color="blue" badge />
  </div>
</div>
```

#### Testing Requirements

- [ ] Renders all 7 stats correctly
- [ ] Numbers formatted with thousands separators
- [ ] Colors match specification (red=rising, green=falling)
- [ ] Responsive grid layout works on all breakpoints
- [ ] SSR data hydrates without flicker

---

### 3. HotStockList

**Location**: `frontend/src/components/home/HotStockList.tsx`  
**Type**: Client Component (WebSocket updates)  
**Purpose**: Display top gainers, losers, and most active stocks.

#### Props

```typescript
interface HotStockListProps {
  category: 'gainers' | 'losers' | 'active';  // Which list to display
  limit?: number;                              // Max stocks to show (default: 5 for gainers/losers, 10 for active)
  showSparklines?: boolean;                    // Show mini price charts (default: true)
}
```

#### Behavior

- **Data Source**: `useHotStocks()` custom hook (derived from WebSocket)
- **Update Frequency**: Every 3 seconds (aligned with WebSocket push)
- **Sorting**: Client-side (see data-model.md for algorithm)
- **Animations**:
  - **Flash Effect**: 200ms background flash on price change (red for up, green for down)
  - **Row Transition**: Smooth position change when ranks update (300ms)
- **Interaction**: Click stock row → Navigate to `/virtual-market/stocks/{symbol}`

#### Visual Requirements

```tsx
<div className="bg-white rounded-xl shadow-lg p-6">
  <h3 className="text-xl font-bold text-gray-900 mb-4">
    {category === 'gainers' ? '涨幅榜' : category === 'losers' ? '跌幅榜' : '活跃股票'}
  </h3>
  
  <div className="space-y-2">
    {hotStocks.map((stock, index) => (
      <HotStockRow
        key={stock.symbol}
        stock={stock}
        rank={index + 1}
        showSparkline={showSparklines}
      />
    ))}
  </div>
  
  {hotStocks.length === 0 && (
    <p className="text-gray-500 text-center py-8">暂无数据</p>
  )}
</div>
```

#### Testing Requirements

- [ ] Sorts stocks correctly by category
- [ ] Limits results to specified count
- [ ] Flash animation triggers on price change
- [ ] Sparklines render when enabled
- [ ] Click navigates to stock detail page
- [ ] Empty state shows when no data
- [ ] React.memo prevents unnecessary re-renders

---

### 4. HotStockRow (Sub-component)

**Location**: `frontend/src/components/home/HotStockRow.tsx`  
**Type**: Client Component (memoized)  
**Purpose**: Single row in HotStockList, optimized for performance.

#### Props

```typescript
interface HotStockRowProps {
  stock: HotStock;             // Stock data (see data-model.md)
  rank: number;                // Display rank (1-10)
  showSparkline?: boolean;     // Show mini chart (default: true)
}

interface HotStock {
  symbol: string;
  name: string;
  current_price: number;
  change_pct: number;
  change_value: number;
  volume: number;
  turnover: number;
  trend: 'up' | 'down' | 'flat';
  sparklineData?: number[];    // Last 20 price points
}
```

#### Behavior

- **Memoization**: Wrapped in `React.memo()` with custom comparison
- **Flash Animation**: CSS transition on `.price-flash` class
- **Hover Effect**: Subtle background color change + cursor pointer
- **Sparkline**: SVG path, 60x30px, last 20 data points

#### Visual Requirements

```tsx
<Link
  href={`/virtual-market/stocks/${stock.symbol}`}
  className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
>
  {/* Rank */}
  <div className="text-sm font-bold text-gray-500 w-6">
    {rank}
  </div>

  {/* Stock Info */}
  <div className="flex-1 min-w-0">
    <div className="font-semibold text-gray-900 truncate">{stock.name}</div>
    <div className="text-xs text-gray-500">{stock.symbol}</div>
  </div>

  {/* Sparkline (optional) */}
  {showSparkline && stock.sparklineData && (
    <MiniSparkline data={stock.sparklineData} trend={stock.trend} />
  )}

  {/* Price */}
  <div className="text-right">
    <div className="font-bold text-gray-900 price-flash">
      ¥{stock.current_price.toFixed(2)}
    </div>
    <div className={`text-sm flex items-center gap-1 ${
      stock.trend === 'up' ? 'text-red-600' : 'text-green-600'
    }`}>
      {stock.trend === 'up' ? '▲' : stock.trend === 'down' ? '▼' : '━'}
      {stock.change_pct > 0 ? '+' : ''}{stock.change_pct.toFixed(2)}%
    </div>
  </div>
</Link>
```

#### CSS (Flash Animation)

```css
.price-flash {
  transition: background-color 200ms ease-out;
}

.price-flash.flash-up {
  background-color: rgba(220, 38, 38, 0.1); /* red-600 with 10% opacity */
}

.price-flash.flash-down {
  background-color: rgba(22, 163, 74, 0.1); /* green-600 with 10% opacity */
}

@media (prefers-reduced-motion: reduce) {
  .price-flash {
    transition: none;
  }
}
```

#### Testing Requirements

- [ ] Memoization prevents re-render when props unchanged
- [ ] Flash animation triggers on price update
- [ ] Hover effect works correctly
- [ ] Sparkline renders with correct data
- [ ] Directional arrow matches trend
- [ ] Link navigates to stock detail page

---

### 5. CoreIndexCards

**Location**: `frontend/src/components/home/CoreIndexCards.tsx`  
**Type**: Server Component  
**Purpose**: Display three core market indices with mini trend charts.

#### Props

```typescript
interface CoreIndexCardsProps {
  indices: CoreIndex[];        // SSR data from /api/v1/indices?type=CORE
  enableRealtime?: boolean;    // Future: WebSocket updates (default: false)
}

interface CoreIndex {
  code: string;
  name: string;
  current_value: number;
  change_value: number;
  change_pct: number;
  volume: number;
  turnover: number;
  constituent_count: number;
  timestamp: number;
}
```

#### Behavior

- **Rendering**: SSR with initial data, no updates (MVP)
- **Layout**: 3-column grid (1 col mobile, 2 cols tablet, 3 cols desktop)
- **Interaction**: Click card → Navigate to `/virtual-market/indices`
- **Mini Chart**: SVG sparkline (optional, show last 7 days trend)

#### Visual Requirements

```tsx
<div className="mb-12">
  <h3 className="text-2xl font-bold text-gray-900 mb-6">核心指数</h3>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {indices.map((index) => (
      <Link
        key={index.code}
        href="/virtual-market/indices"
        className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow group"
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <h4 className="text-lg font-semibold text-gray-900">{index.name}</h4>
            <p className="text-sm text-gray-500">{index.code}</p>
          </div>
          <Badge 
            value={index.change_pct} 
            variant={index.change_pct > 0 ? 'red' : index.change_pct < 0 ? 'green' : 'gray'} 
          />
        </div>
        
        <div className="text-3xl font-bold text-gray-900 mb-2">
          {index.current_value.toFixed(2)}
        </div>
        
        <div className={`text-sm ${
          index.change_pct > 0 ? 'text-red-600' : 'text-green-600'
        }`}>
          {index.change_pct > 0 ? '+' : ''}{index.change_value.toFixed(2)}
        </div>
        
        <svg className="w-6 h-6 text-gray-400 group-hover:translate-x-1 transition-transform absolute top-6 right-6">
          {/* Arrow icon */}
        </svg>
      </Link>
    ))}
  </div>
</div>
```

#### Testing Requirements

- [ ] Renders all 3 indices correctly
- [ ] Numbers formatted to 2 decimal places
- [ ] Badge color matches change_pct sign
- [ ] Hover effect increases shadow
- [ ] Click navigates to indices page
- [ ] Responsive grid works on all breakpoints

---

### 6. FeatureShowcase

**Location**: `frontend/src/components/home/FeatureShowcase.tsx`  
**Type**: Server Component (static content)  
**Purpose**: Display three core platform features with CTAs.

#### Props

```typescript
interface FeatureShowcaseProps {
  features: FeatureCard[];     // Static data (see data-model.md)
}

interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType;
  primaryAction: { label: string; href: string };
  secondaryAction?: { label: string; href: string };
  color: string;  // Tailwind color name (e.g., "blue")
}
```

#### Behavior

- **Rendering**: Server-side rendered, no client state
- **Layout**: 3-column grid (1 col mobile, 2 cols tablet, 3 cols desktop)
- **Icons**: From `lucide-react` (BarChart3, Brain, Users)
- **Interaction**:
  - Primary action: Button link
  - Secondary action: Text link (optional)

#### Visual Requirements

```tsx
<div className="mb-12">
  <h3 className="text-2xl font-bold text-gray-900 text-center mb-6">
    三大核心功能
  </h3>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {features.map((feature) => (
      <div
        key={feature.id}
        className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow"
      >
        <div className={`w-16 h-16 rounded-full bg-${feature.color}-100 flex items-center justify-center mb-4`}>
          <feature.icon className={`w-8 h-8 text-${feature.color}-600`} />
        </div>
        
        <h4 className="text-xl font-semibold text-gray-900 mb-2">
          {feature.title}
        </h4>
        
        <p className="text-gray-600 mb-6">
          {feature.description}
        </p>
        
        <Link
          href={feature.primaryAction.href}
          className={`inline-block px-6 py-3 bg-${feature.color}-600 text-white rounded-lg font-semibold hover:bg-${feature.color}-700 transition-colors`}
        >
          {feature.primaryAction.label}
        </Link>
        
        {feature.secondaryAction && (
          <Link
            href={feature.secondaryAction.href}
            className={`block mt-3 text-${feature.color}-600 hover:text-${feature.color}-700 text-sm`}
          >
            {feature.secondaryAction.label}
          </Link>
        )}
      </div>
    ))}
  </div>
</div>
```

#### Testing Requirements

- [ ] Renders all 3 features correctly
- [ ] Icons display correctly
- [ ] Primary and secondary actions link to correct routes
- [ ] Hover effect works
- [ ] Responsive grid works on all breakpoints

---

### 7. QuickStartGuide

**Location**: `frontend/src/components/home/QuickStartGuide.tsx`  
**Type**: Server Component (static content)  
**Purpose**: 3-step guide to onboard new users.

#### Props

```typescript
interface QuickStartGuideProps {
  steps: QuickStartStep[];     // Static data
}

interface QuickStartStep {
  id: string;
  number: number;              // Step number (1-3)
  title: string;
  description: string;
  icon: React.ComponentType;
  cta?: { label: string; href: string };
}
```

#### Behavior

- **Rendering**: Server-side rendered
- **Layout**: Horizontal stepper (3 steps)
- **Responsive**: Stack vertically on mobile

#### Visual Requirements

```tsx
<div className="bg-white rounded-xl shadow-lg p-8">
  <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
    三步开启投资之旅
  </h3>
  
  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
    {steps.map((step, index) => (
      <div key={step.id} className="text-center">
        <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl font-bold text-blue-600">{step.number}</span>
        </div>
        
        <h4 className="text-lg font-semibold text-gray-900 mb-2">
          {step.title}
        </h4>
        
        <p className="text-gray-600 mb-4">
          {step.description}
        </p>
        
        {step.cta && (
          <Link
            href={step.cta.href}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm"
          >
            {step.cta.label} →
          </Link>
        )}
        
        {index < steps.length - 1 && (
          <div className="hidden md:block absolute top-8 right-0 w-8 h-0.5 bg-gray-300" />
        )}
      </div>
    ))}
  </div>
</div>
```

#### Testing Requirements

- [ ] Renders all 3 steps correctly
- [ ] Step numbers display correctly
- [ ] Connector lines show on desktop only
- [ ] CTAs link to correct routes
- [ ] Responsive layout works

---

## Modified Components

### 8. page.tsx (Homepage)

**Location**: `frontend/src/app/page.tsx`  
**Type**: Server Component (with client components)  
**Purpose**: Main homepage orchestrating all sections.

#### Structure

```tsx
// app/page.tsx
import { HeroSection } from '@/components/home/HeroSection';
import { MarketOverview } from '@/components/home/MarketOverview';
import { HotStockSection } from '@/components/home/HotStockSection';
import { CoreIndexCards } from '@/components/home/CoreIndexCards';
import { FeatureShowcase } from '@/components/home/FeatureShowcase';
import { QuickStartGuide } from '@/components/home/QuickStartGuide';

export default async function HomePage() {
  // SSR: Fetch initial data
  const [marketOverview, coreIndices] = await Promise.all([
    fetch('http://localhost:8000/api/v1/market/overview', { cache: 'no-store' }).then(r => r.json()),
    fetch('http://localhost:8000/api/v1/indices?type=CORE', { cache: 'no-store' }).then(r => r.json()),
  ]);

  return (
    <div className="min-h-screen bg-gray-50">
      <HeroSection />
      <MarketOverview initialData={marketOverview.data} />
      <HotStockSection /> {/* Client component */}
      <CoreIndexCards indices={coreIndices.data} />
      <FeatureShowcase features={FEATURES} />
      <QuickStartGuide steps={QUICK_START_STEPS} />
    </div>
  );
}
```

#### Testing Requirements

- [ ] SSR completes successfully
- [ ] All sections render in correct order
- [ ] No hydration errors
- [ ] LCP < 3 seconds
- [ ] FCP < 1.5 seconds

---

## Shared UI Components

### 9. Badge

**Location**: `frontend/src/components/ui/Badge.tsx`  
**Type**: Server Component  
**Purpose**: Display percentage change with color coding.

#### Props

```typescript
interface BadgeProps {
  value: number;               // Percentage value (e.g., 5.2)
  variant?: 'red' | 'green' | 'gray' | 'auto';  // Color theme (auto = based on value)
  size?: 'sm' | 'md' | 'lg';   // Size variant
}
```

#### Behavior

- **Auto Variant**: If `variant="auto"`, determine color from value sign
  - Positive → Red
  - Negative → Green
  - Zero → Gray

#### Visual Requirements

```tsx
<span className={`
  inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
  ${variant === 'red' ? 'bg-red-100 text-red-700' : ''}
  ${variant === 'green' ? 'bg-green-100 text-green-700' : ''}
  ${variant === 'gray' ? 'bg-gray-100 text-gray-700' : ''}
  ${size === 'sm' ? 'text-xs px-2 py-0.5' : ''}
  ${size === 'lg' ? 'text-base px-4 py-2' : ''}
`}>
  {value > 0 ? '+' : ''}{value.toFixed(2)}%
</span>
```

---

## Custom Hooks Contracts

### 10. useHotStocks

**Location**: `frontend/src/hooks/useHotStocks.ts`  
**Purpose**: Derive hot stock lists from WebSocket market data.

```typescript
function useHotStocks(): HotStockLists | null {
  const { marketData } = useWebSocketContext();
  
  return useMemo(() => {
    if (!marketData?.stocks) return null;
    return deriveHotStocks(marketData.stocks);
  }, [marketData?.stocks]);
}
```

**Returns**:
```typescript
interface HotStockLists {
  gainers: HotStock[];   // Top 5 by change_pct (positive)
  losers: HotStock[];    // Top 5 by change_pct (negative)
  active: HotStock[];    // Top 10 by turnover
}
```

---

### 11. useStockSparkline

**Location**: `frontend/src/hooks/useStockSparkline.ts`  
**Purpose**: Track last 20 price points for a single stock.

```typescript
function useStockSparkline(symbol: string): number[] {
  const [priceHistory, setPriceHistory] = useState<number[]>([]);
  const { marketData } = useWebSocketContext();
  
  useEffect(() => {
    const stock = marketData?.stocks.find(s => s.symbol === symbol);
    if (!stock) return;
    
    setPriceHistory(prev => [...prev, stock.current_price].slice(-20));
  }, [marketData, symbol]);
  
  return priceHistory;
}
```

**Returns**: Array of last 20 prices (newest last)

---

## Testing Contracts

### Unit Tests

Each component must have:
- [ ] Snapshot test
- [ ] Props validation test
- [ ] Behavior test (user interactions)
- [ ] Accessibility test (aria labels, keyboard navigation)

### Integration Tests

- [ ] Homepage loads with SSR data
- [ ] WebSocket connects and updates HotStockList
- [ ] Navigation links work correctly
- [ ] Responsive layout on all breakpoints

### E2E Tests (Playwright)

```typescript
// tests/e2e/homepage-flow.spec.ts
test('Homepage engagement flow', async ({ page }) => {
  await page.goto('/');
  
  // Hero section loads
  await expect(page.locator('h1')).toContainText('专业图表工具');
  
  // Market overview displays
  await expect(page.locator('text=市场概况')).toBeVisible();
  
  // Hot stocks update (wait 3 seconds)
  await page.waitForTimeout(3000);
  const hotStock = page.locator('[data-testid="hot-stock-row"]').first();
  await expect(hotStock).toBeVisible();
  
  // Click hot stock → Navigate to detail page
  await hotStock.click();
  await expect(page).toHaveURL(/\/virtual-market\/stocks\/\d+/);
  
  // Back to homepage
  await page.goBack();
  
  // Click primary CTA
  await page.click('text=开始免费交易');
  await expect(page).toHaveURL('/virtual-market');
});
```

---

## Performance Contracts

### Metrics Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| LCP (Largest Contentful Paint) | <3s | Lighthouse, WebPageTest |
| FCP (First Contentful Paint) | <1.5s | Lighthouse, Chrome DevTools |
| TTI (Time to Interactive) | <5s | Lighthouse |
| Bundle Size | <100KB (gzipped) | `next build`, `@next/bundle-analyzer` |
| WebSocket Latency | <500ms | Custom timing in useWebSocket |

### Optimization Requirements

- [ ] All images use `next/image` with lazy loading
- [ ] Heavy components use `dynamic()` import
- [ ] Icons tree-shaken (import individually)
- [ ] CSS purged (Tailwind content config)
- [ ] Fonts optimized (next/font)

---

## Accessibility Contracts

### WCAG 2.1 AA Requirements

- [ ] **Color Contrast**: Min 4.5:1 for text, 3:1 for large text
- [ ] **Keyboard Navigation**: All interactive elements focusable
- [ ] **Screen Reader**: `aria-label` on icon buttons, `aria-live` on updates
- [ ] **Motion**: Respect `prefers-reduced-motion` media query
- [ ] **Focus Indicators**: Visible focus rings (not removed with `outline: none`)

### Testing Checklist

- [ ] Run `axe-core` automated tests
- [ ] Manual keyboard navigation test (Tab, Enter, Escape)
- [ ] Screen reader test (NVDA/JAWS on Windows, VoiceOver on Mac)
- [ ] Color blindness simulation (Chrome DevTools)

---

## Notes

- All contracts assume Next.js 15 App Router conventions
- TypeScript strict mode enabled (`strict: true` in tsconfig.json)
- Component file structure follows Atomic Design principles (atoms, molecules, organisms)
- Tailwind CSS v4 used for all styling (no custom CSS except animations)
