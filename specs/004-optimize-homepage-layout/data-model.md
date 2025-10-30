# Data Model: 首页布局优化与整页滚动

**Feature**: 004-optimize-homepage-layout  
**Date**: 2025-10-30  
**Status**: Phase 1 - Design & Contracts

## Overview

本特性的数据模型专注于**客户端状态管理**，无后端数据存储。所有数据存储在浏览器 localStorage 中，使用 Zustand 管理运行时状态。

## Core Entities

### 1. PageSection (页面区域)

**描述**: 首页上的独立内容区域，每个区域包含一个功能模块（如市场概览、功能展示等）

**属性**:

| 字段 | 类型 | 必需 | 描述 | 示例值 |
|------|------|------|------|--------|
| `id` | `string` | ✅ | 区域唯一标识符 | `"hero"`, `"market-overview"`, `"hot-stocks"` |
| `title` | `string` | ✅ | 区域标题（用于导航点和可访问性） | `"核心价值主张"`, `"实时市场概览"` |
| `component` | `ReactNode` | ✅ | 要渲染的 React 组件 | `<HeroSection />`, `<MarketOverview />` |
| `isCollapsible` | `boolean` | ✅ | 是否支持折叠 | `true` (教育资源), `false` (核心功能) |
| `minHeight` | `string` | ❌ | 最小高度 (CSS 值) | `"100vh"`, `"auto"` |
| `order` | `number` | ✅ | 显示顺序 (用于排序) | `0`, `1`, `2`, ... |
| `category` | `SectionCategory` | ❌ | 区域分类（用于分组） | `"core"`, `"feature"`, `"education"` |

**验证规则**:
- `id` 必须唯一，使用 kebab-case 命名
- `order` 必须为非负整数
- `minHeight` 必须为有效 CSS 长度值

**类型定义**:
```typescript
type SectionCategory = 'core' | 'feature' | 'market' | 'education' | 'social';

interface PageSection {
  id: string;
  title: string;
  component: React.ComponentType;
  isCollapsible: boolean;
  minHeight?: string;
  order: number;
  category?: SectionCategory;
}
```

**示例数据**:
```typescript
const sections: PageSection[] = [
  {
    id: 'hero',
    title: '核心价值主张',
    component: HeroSection,
    isCollapsible: false,
    minHeight: '100vh',
    order: 0,
    category: 'core',
  },
  {
    id: 'market-overview',
    title: '实时市场概览',
    component: MarketOverview,
    isCollapsible: false,
    minHeight: '100vh',
    order: 1,
    category: 'market',
  },
  {
    id: 'hot-stocks',
    title: '热门股票',
    component: HotStockList,
    isCollapsible: false,
    minHeight: 'auto',
    order: 2,
    category: 'market',
  },
  {
    id: 'quick-start',
    title: '快速开始',
    component: QuickStartGuide,
    isCollapsible: true,
    minHeight: 'auto',
    order: 3,
    category: 'feature',
  },
  {
    id: 'feature-showcase',
    title: '核心功能',
    component: FeatureShowcase,
    isCollapsible: true,
    minHeight: 'auto',
    order: 4,
    category: 'feature',
  },
  {
    id: 'education',
    title: '学习资源',
    component: EducationFooter,
    isCollapsible: true,
    minHeight: 'auto',
    order: 5,
    category: 'education',
  },
];
```

---

### 2. NavigationDot (导航点)

**描述**: 侧边导航指示器，对应一个页面区域

**属性**:

| 字段 | 类型 | 必需 | 描述 | 示例值 |
|------|------|------|------|--------|
| `sectionId` | `string` | ✅ | 对应的区域 ID | `"hero"`, `"market-overview"` |
| `label` | `string` | ✅ | 无障碍标签（屏幕阅读器用） | `"跳转到核心价值主张"` |
| `isActive` | `boolean` | ✅ | 是否为当前激活区域 | `true`, `false` |
| `index` | `number` | ✅ | 导航点索引（用于排序和键盘导航） | `0`, `1`, `2`, ... |

**类型定义**:
```typescript
interface NavigationDot {
  sectionId: string;
  label: string;
  isActive: boolean;
  index: number;
}
```

**状态转换**:
- 用户滚动到某区域 → 对应导航点 `isActive = true`，其他 `isActive = false`
- 点击导航点 → 滚动到对应区域 → `isActive = true`

---

### 3. LayoutPreferences (布局偏好设置)

**描述**: 用户个性化配置，存储在 localStorage + Zustand

**属性**:

| 字段 | 类型 | 必需 | 描述 | 默认值 |
|------|------|------|------|--------|
| `isScrollSnapEnabled` | `boolean` | ✅ | 是否启用整页滚动 | `true` |
| `collapsedSections` | `string[]` | ✅ | 已折叠的区域 ID 列表 | `[]` |
| `sectionOrder` | `string[]` | ❌ | 自定义区域顺序 (US4-P3) | `undefined` |
| `lastVisitedSection` | `string` | ❌ | 上次访问的区域 ID | `undefined` |

**验证规则**:
- `collapsedSections` 中的 ID 必须在 `sections` 中存在且 `isCollapsible = true`
- `sectionOrder` 如存在，必须包含所有区域 ID 且无重复

**类型定义**:
```typescript
interface LayoutPreferences {
  isScrollSnapEnabled: boolean;
  collapsedSections: string[];
  sectionOrder?: string[];
  lastVisitedSection?: string;
}
```

**默认值**:
```typescript
const defaultPreferences: LayoutPreferences = {
  isScrollSnapEnabled: true,
  collapsedSections: [],
  sectionOrder: undefined, // undefined 表示使用默认顺序
  lastVisitedSection: undefined,
};
```

**存储格式** (localStorage):
```json
{
  "happystock.layout.preferences": {
    "isScrollSnapEnabled": true,
    "collapsedSections": ["education", "quick-start"],
    "sectionOrder": ["hero", "hot-stocks", "market-overview", "feature-showcase", "quick-start", "education"],
    "lastVisitedSection": "market-overview"
  }
}
```

**数据大小估算**: ~300-500 bytes (远低于 localStorage 5MB 限制)

---

### 4. ScrollState (滚动状态)

**描述**: 运行时滚动状态，仅存在于内存中（Zustand），不持久化

**属性**:

| 字段 | 类型 | 必需 | 描述 | 示例值 |
|------|------|------|------|--------|
| `currentSectionId` | `string \| null` | ✅ | 当前可见区域 ID | `"market-overview"`, `null` |
| `isScrolling` | `boolean` | ✅ | 是否正在滚动中 | `true`, `false` |
| `scrollDirection` | `'up' \| 'down' \| null` | ✅ | 滚动方向 | `"down"`, `"up"`, `null` |
| `isAnimating` | `boolean` | ✅ | 是否有动画进行中（折叠/展开） | `true`, `false` |

**类型定义**:
```typescript
interface ScrollState {
  currentSectionId: string | null;
  isScrolling: boolean;
  scrollDirection: 'up' | 'down' | null;
  isAnimating: boolean;
}
```

**状态转换**:
- 用户开始滚动 → `isScrolling = true`
- 滚动停止（500ms 后） → `isScrolling = false`
- 区域进入视口 → `currentSectionId` 更新
- 折叠动画开始 → `isAnimating = true`
- 折叠动画结束 → `isAnimating = false`

---

## Relationships (实体关系)

```
PageSection (1) ---- (1) NavigationDot
    ↓ (id)              ↑ (sectionId)
    |
    | (isCollapsible)
    ↓
LayoutPreferences.collapsedSections (many)
    ↓ (contains section ids)
    |
    | (persisted in localStorage)
    ↓
LayoutPreferences.sectionOrder (many, optional)
    ↓ (defines custom order)
    |
    └──> PageSection[] (reordered)

ScrollState.currentSectionId → PageSection.id (reference)
```

**关系说明**:
1. **PageSection → NavigationDot**: 一对一映射，每个区域对应一个导航点
2. **PageSection → LayoutPreferences.collapsedSections**: 多对一，可折叠区域可被添加到折叠列表
3. **PageSection.order → LayoutPreferences.sectionOrder**: 默认顺序 vs 自定义顺序
4. **ScrollState.currentSectionId → PageSection**: 当前可见区域引用

---

## State Management (状态管理)

### Zustand Store 结构

```typescript
// stores/layoutPreferences.ts
interface LayoutStore {
  // State
  preferences: LayoutPreferences;
  sections: PageSection[];
  scrollState: ScrollState;
  
  // Actions
  toggleScrollSnap: () => void;
  toggleSection: (sectionId: string) => void;
  reorderSections: (newOrder: string[]) => void;
  setCurrentSection: (sectionId: string) => void;
  setScrolling: (isScrolling: boolean, direction?: 'up' | 'down') => void;
  setAnimating: (isAnimating: boolean) => void;
  
  // Persistence
  loadPreferences: () => void;
  savePreferences: () => void;
}

// 使用示例
const useLayoutStore = create<LayoutStore>((set, get) => ({
  preferences: defaultPreferences,
  sections: defaultSections,
  scrollState: {
    currentSectionId: null,
    isScrolling: false,
    scrollDirection: null,
    isAnimating: false,
  },
  
  toggleScrollSnap: () => set(state => {
    const newPreferences = {
      ...state.preferences,
      isScrollSnapEnabled: !state.preferences.isScrollSnapEnabled,
    };
    localStorage.setItem('happystock.layout.preferences', JSON.stringify(newPreferences));
    return { preferences: newPreferences };
  }),
  
  toggleSection: (sectionId) => set(state => {
    const { collapsedSections } = state.preferences;
    const newCollapsed = collapsedSections.includes(sectionId)
      ? collapsedSections.filter(id => id !== sectionId)
      : [...collapsedSections, sectionId];
    
    const newPreferences = {
      ...state.preferences,
      collapsedSections: newCollapsed,
    };
    localStorage.setItem('happystock.layout.preferences', JSON.stringify(newPreferences));
    return { preferences: newPreferences };
  }),
  
  // ... 其他 actions
}));
```

---

## Validation Rules (验证规则)

### 1. Section ID 唯一性

```typescript
function validateSectionIds(sections: PageSection[]): boolean {
  const ids = sections.map(s => s.id);
  return ids.length === new Set(ids).size;
}
```

### 2. 折叠状态有效性

```typescript
function validateCollapsedSections(
  collapsedSections: string[],
  sections: PageSection[]
): boolean {
  const collapsibleIds = sections
    .filter(s => s.isCollapsible)
    .map(s => s.id);
  
  return collapsedSections.every(id => collapsibleIds.includes(id));
}
```

### 3. 区域顺序完整性

```typescript
function validateSectionOrder(
  sectionOrder: string[] | undefined,
  sections: PageSection[]
): boolean {
  if (!sectionOrder) return true; // undefined 表示使用默认顺序
  
  const defaultIds = sections.map(s => s.id).sort();
  const customIds = [...sectionOrder].sort();
  
  return JSON.stringify(defaultIds) === JSON.stringify(customIds);
}
```

### 4. localStorage 容量检查

```typescript
function checkLocalStorageSpace(): boolean {
  try {
    const testKey = 'happystock.layout.test';
    localStorage.setItem(testKey, 'x'.repeat(10000)); // 10KB 测试
    localStorage.removeItem(testKey);
    return true;
  } catch (e) {
    console.error('localStorage quota exceeded or unavailable');
    return false;
  }
}
```

---

## Migration Strategy (数据迁移策略)

### 版本控制

```typescript
interface LayoutPreferencesV1 {
  version: 1;
  isScrollSnapEnabled: boolean;
  collapsedSections: string[];
}

interface LayoutPreferencesV2 extends LayoutPreferencesV1 {
  version: 2;
  sectionOrder?: string[];
  lastVisitedSection?: string;
}

function migratePreferences(stored: any): LayoutPreferences {
  if (!stored || !stored.version) {
    // 无版本号 → 使用默认值
    return defaultPreferences;
  }
  
  if (stored.version === 1) {
    // V1 → V2: 添加新字段
    return {
      ...stored,
      version: 2,
      sectionOrder: undefined,
      lastVisitedSection: undefined,
    };
  }
  
  return stored as LayoutPreferences;
}
```

---

## Performance Considerations (性能考量)

### 1. localStorage 读写优化

```typescript
// 使用 debounce 避免频繁写入
import { debounce } from 'lodash-es';

const savePreferencesDebounced = debounce((preferences: LayoutPreferences) => {
  localStorage.setItem('happystock.layout.preferences', JSON.stringify(preferences));
}, 1000); // 1秒内的多次更新合并为一次写入
```

### 2. 状态更新批处理

```typescript
// 使用 Zustand 的 batch 功能
import { batch } from 'zustand';

function handleSectionChange(sectionId: string) {
  batch(() => {
    useLayoutStore.getState().setCurrentSection(sectionId);
    useLayoutStore.getState().setScrolling(false);
  });
}
```

### 3. 内存占用估算

| 数据结构 | 数量 | 单个大小 | 总大小 |
|---------|------|---------|--------|
| PageSection | 6-10 | ~200 bytes | ~2 KB |
| NavigationDot | 6-10 | ~100 bytes | ~1 KB |
| LayoutPreferences | 1 | ~500 bytes | ~500 bytes |
| ScrollState | 1 | ~100 bytes | ~100 bytes |
| **Total** | - | - | **~3.5 KB** |

内存占用极小，对性能无影响。

---

## Error Handling (错误处理)

### localStorage 不可用

```typescript
function safeLoadPreferences(): LayoutPreferences {
  try {
    const stored = localStorage.getItem('happystock.layout.preferences');
    if (!stored) return defaultPreferences;
    
    const parsed = JSON.parse(stored);
    return migratePreferences(parsed);
  } catch (error) {
    console.error('Failed to load preferences from localStorage:', error);
    return defaultPreferences; // 降级为默认配置
  }
}

function safeSavePreferences(preferences: LayoutPreferences): void {
  try {
    localStorage.setItem('happystock.layout.preferences', JSON.stringify(preferences));
  } catch (error) {
    console.error('Failed to save preferences to localStorage:', error);
    // 静默失败，不影响用户使用
  }
}
```

### 无效数据处理

```typescript
function sanitizePreferences(preferences: any): LayoutPreferences {
  return {
    isScrollSnapEnabled: typeof preferences.isScrollSnapEnabled === 'boolean'
      ? preferences.isScrollSnapEnabled
      : true,
    collapsedSections: Array.isArray(preferences.collapsedSections)
      ? preferences.collapsedSections.filter(id => typeof id === 'string')
      : [],
    sectionOrder: Array.isArray(preferences.sectionOrder)
      ? preferences.sectionOrder
      : undefined,
    lastVisitedSection: typeof preferences.lastVisitedSection === 'string'
      ? preferences.lastVisitedSection
      : undefined,
  };
}
```

---

## Testing Strategy (测试策略)

### 单元测试

```typescript
// tests/stores/layoutPreferences.test.ts
describe('LayoutStore', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should toggle scroll snap', () => {
    const { result } = renderHook(() => useLayoutStore());
    expect(result.current.preferences.isScrollSnapEnabled).toBe(true);
    
    act(() => result.current.toggleScrollSnap());
    expect(result.current.preferences.isScrollSnapEnabled).toBe(false);
  });

  it('should persist preferences to localStorage', () => {
    const { result } = renderHook(() => useLayoutStore());
    act(() => result.current.toggleSection('education'));
    
    const stored = JSON.parse(localStorage.getItem('happystock.layout.preferences')!);
    expect(stored.collapsedSections).toContain('education');
  });

  it('should validate collapsed sections', () => {
    const sections: PageSection[] = [
      { id: 'hero', isCollapsible: false, ... },
      { id: 'education', isCollapsible: true, ... },
    ];
    
    expect(validateCollapsedSections(['education'], sections)).toBe(true);
    expect(validateCollapsedSections(['hero'], sections)).toBe(false); // 不可折叠
    expect(validateCollapsedSections(['invalid'], sections)).toBe(false); // 不存在
  });
});
```

### 集成测试

```typescript
// tests/e2e/layout-preferences.spec.ts
test('should persist collapsed state across page reload', async ({ page }) => {
  await page.goto('/');
  
  // 折叠教育资源区域
  await page.click('[data-testid="education-collapse-button"]');
  await expect(page.locator('[data-testid="education-content"]')).toBeHidden();
  
  // 刷新页面
  await page.reload();
  
  // 验证折叠状态保持
  await expect(page.locator('[data-testid="education-content"]')).toBeHidden();
});
```

---

## Accessibility (可访问性)

### ARIA 属性映射

| 实体 | ARIA 属性 | 值示例 |
|------|----------|--------|
| PageSection | `role="region"` | - |
| PageSection | `aria-label` | `"核心价值主张区域"` |
| NavigationDot | `role="navigation"` | - |
| NavigationDot | `aria-label` | `"页面导航"` |
| Dot Button | `aria-label` | `"跳转到实时市场概览"` |
| Dot Button | `aria-current` | `"true"` (当前激活) |
| Collapse Button | `aria-expanded` | `"true"` / `"false"` |
| Collapse Button | `aria-controls` | `"education-content"` |

---

## Summary

### 数据模型特点

1. **轻量级**: 总内存占用 ~3.5 KB，localStorage 存储 ~500 bytes
2. **简单性**: 仅 4 个核心实体，关系清晰
3. **可扩展**: 支持版本迁移，易于添加新字段
4. **类型安全**: 完整 TypeScript 类型定义
5. **性能优化**: debounce 写入，batch 更新

### 数据流

```
User Interaction
    ↓
Component Event Handler
    ↓
Zustand Action (toggleSection, setCurrentSection, etc.)
    ↓
State Update + localStorage Sync
    ↓
React Re-render (only affected components)
    ↓
UI Update (CSS Animation)
```

---

**Version**: 1.0  
**Approved by**: GitHub Copilot  
**Date**: 2025-10-30
