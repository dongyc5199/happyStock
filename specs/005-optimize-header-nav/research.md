# Research & Technology Decisions

**Feature**: 优化首页标题栏导航  
**Date**: 2025-10-31  
**Status**: Phase 0 Complete

## 目的

解决技术上下文中的 NEEDS CLARIFICATION 项，并为关键技术选型提供依据。

---

## 1. 模态框组件库选择

### 决策：使用 Radix UI Dialog

### 理由

1. **无样式组件**：Radix UI 提供完整的可访问性和交互逻辑，但不强制样式，完美契合项目已有的 Tailwind CSS 样式系统
2. **可访问性**：内置 ARIA 属性、焦点管理、键盘导航（Esc 关闭）、焦点陷阱（Focus Trap）
3. **轻量级**：@radix-ui/react-dialog 体积小（~5KB gzipped），tree-shakeable
4. **与 Next.js 兼容**：支持 SSR，无客户端渲染问题
5. **行业认可**：被 Vercel、Tailwind Labs 等顶级团队使用

### 对比的替代方案

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **Radix UI Dialog** | 可访问性好、无样式、轻量 | 需要自己写样式 | ✅ **选择** |
| Headless UI Dialog | 官方 Tailwind 团队、简单 | 功能较少、API 不如 Radix 灵活 | ❌ 功能略显基础 |
| React Modal | 成熟、社区大 | 样式耦合、体积大、可访问性需手动实现 | ❌ 过时，不符合现代实践 |
| 自定义实现 | 完全控制 | 开发成本高、可访问性难保证、需处理边界情况 | ❌ 投入产出比低 |

### 实现要点

```typescript
import * as Dialog from '@radix-ui/react-dialog';

// 示例结构
<Dialog.Root open={isOpen} onOpenChange={setIsOpen}>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/50" />
    <Dialog.Content className="fixed top-1/2 left-1/2 ...">
      <Dialog.Title>登录</Dialog.Title>
      <Dialog.Description>请输入您的账号和密码</Dialog.Description>
      {/* 表单内容 */}
      <Dialog.Close>关闭</Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

---

## 2. 认证 API 端点和数据格式

### 决策：定义标准 REST API 契约

### 理由

基于项目已有的后端结构（`backend/api/`）和 FastAPI 技术栈（推测），定义清晰的 REST API 契约以确保前后端协作顺畅。

### API 契约定义

#### 2.1 用户登录

**端点**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "string",     // 或 "email" 
  "password": "string"
}
```

**成功响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "avatar_url": "string | null",
      "created_at": "string (ISO 8601)"
    },
    "token": "string (JWT)",
    "expires_at": "string (ISO 8601)"
  }
}
```

**失败响应** (401 Unauthorized):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "用户名或密码错误"
  }
}
```

#### 2.2 用户注册

**端点**: `POST /api/auth/register`

**请求体**:
```json
{
  "username": "string (3-20字符)",
  "email": "string",
  "password": "string (8-128字符)"
}
```

**成功响应** (201 Created):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "avatar_url": null
    },
    "token": "string (JWT)",
    "expires_at": "string (ISO 8601)"
  }
}
```

**失败响应** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "USERNAME_TAKEN | EMAIL_TAKEN | VALIDATION_ERROR",
    "message": "该用户名已被使用",
    "details": {
      "field": "username"
    }
  }
}
```

#### 2.3 获取当前用户信息

**端点**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "avatar_url": "string | null"
    }
  }
}
```

#### 2.4 退出登录

**端点**: `POST /api/auth/logout`

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "已成功退出登录"
}
```

### 前端存储策略

1. **Token 存储**：使用 Zustand persist 中间件存储到 localStorage
2. **用户信息缓存**：存储在 Zustand store 中，页面刷新时从 localStorage 恢复
3. **Token 过期处理**：在 API 调用拦截器中检查 401，自动清除状态并提示重新登录

### 替代方案考虑

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **REST + JWT** | 简单、无状态、已有项目标准 | Token 存储安全需注意 | ✅ **选择** |
| Session Cookie | 更安全（HttpOnly） | 需要服务端会话管理 | ❌ 增加后端复杂度 |
| OAuth2 | 标准化、支持第三方登录 | 过度设计（Out of Scope） | ❌ 不在范围内 |

---

## 3. E2E 测试工具选择

### 决策：可选 - 优先单元测试和集成测试，E2E 测试延后

### 理由

1. **MVP 优先**：登录/注册流程可通过单元测试（组件交互）和集成测试（API mock）充分覆盖
2. **成本收益**：E2E 测试维护成本高，对于此功能的投入产出比不如单元测试
3. **灵活性**：若后续需要，可快速引入 Playwright（项目已有成熟的测试基础设施）

### 如果实施 E2E 测试的推荐方案

| 工具 | 优点 | 缺点 |
|------|------|------|
| **Playwright** | 快速、跨浏览器、官方支持好 | 配置略复杂 |
| Cypress | 开发者体验好、调试方便 | 仅支持 Chromium 系浏览器（v10+） |

**推荐**: Playwright（如果需要）

---

## 4. 图标语义化映射

### 决策：为每个导航项选择合适的 Lucide 图标

### 理由

Lucide React 已是项目依赖，包含 1000+ 图标，覆盖所有常见场景。遵循视觉一致性和语义化原则。

### 图标映射表

| 导航项 | 图标名称 | Lucide 组件 | 语义 |
|--------|----------|-------------|------|
| 首页 | Home | `<Home />` | 房屋，通用首页标识 |
| 市场行情 | TrendingUp | `<TrendingUp />` | 上升趋势线，代表股票市场 |
| 板块 | LayoutGrid | `<LayoutGrid />` | 网格布局，代表分类/板块 |
| 关于 | Info | `<Info />` | 信息图标，关于/帮助 |
| 登录 | LogIn | `<LogIn />` | 登录箭头 |
| 注册 | UserPlus | `<UserPlus />` | 添加用户 |
| 用户菜单 | User / Avatar | `<User />` | 用户头像图标 |
| 个人中心 | User | `<User />` | 个人资料 |
| 账户设置 | Settings | `<Settings />` | 齿轮图标 |
| 退出登录 | LogOut | `<LogOut />` | 退出箭头 |
| 汉堡菜单 | Menu | `<Menu />` | 三横线 |

### 图标使用最佳实践

```typescript
import { Home, TrendingUp, LayoutGrid, Info } from 'lucide-react';

const navigationItems = [
  { icon: Home, label: '首页', href: '/' },
  { icon: TrendingUp, label: '市场行情', href: '/virtual-market' },
  { icon: LayoutGrid, label: '板块', href: '/sectors' },
  { icon: Info, label: '关于', href: '/about' },
];

// 使用
<nav>
  {navigationItems.map(item => (
    <Link key={item.href} href={item.href}>
      <item.icon className="w-5 h-5" />
      <span>{item.label}</span>
    </Link>
  ))}
</nav>
```

---

## 5. 响应式设计最佳实践

### 决策：采用移动优先 + Tailwind 断点策略

### 理由

项目已使用 Tailwind CSS，利用其内置的响应式断点系统可以快速实现移动适配。

### 断点策略

| 断点 | 屏幕宽度 | Tailwind 前缀 | 导航模式 |
|------|----------|---------------|----------|
| 移动端 | < 768px | `(default)` | 汉堡菜单 |
| 桌面端 | ≥ 768px | `md:` | 水平导航栏 |

### 实现模式

```typescript
// 使用 Tailwind 响应式类
<nav>
  {/* 移动端：汉堡菜单 */}
  <button className="md:hidden">
    <Menu />
  </button>
  
  {/* 桌面端：导航项 */}
  <div className="hidden md:flex gap-4">
    {navigationItems.map(item => (
      <Link href={item.href}>{item.label}</Link>
    ))}
  </div>
</nav>
```

### 汉堡菜单行为

1. **展开方式**：全屏或侧边抽屉（推荐全屏，更简单）
2. **关闭触发**：
   - 点击遮罩层
   - 点击关闭按钮
   - 点击导航项
   - 页面滚动（澄清决策）
   - 屏幕旋转（澄清决策）
3. **动画**：使用 Tailwind transition + transform，300ms 淡入淡出

---

## 6. 性能优化策略

### 决策：代码分割 + 懒加载 + 预加载

### 关键优化点

1. **模态框组件懒加载**：
   ```typescript
   const LoginModal = dynamic(() => import('@/components/auth/LoginModal'), {
     ssr: false,
     loading: () => <div>加载中...</div>
   });
   ```

2. **图标按需导入**：
   ```typescript
   // ✅ 推荐
   import { Home, TrendingUp } from 'lucide-react';
   
   // ❌ 避免
   import * as Icons from 'lucide-react';
   ```

3. **Zustand 状态持久化优化**：
   ```typescript
   // 只持久化必要字段
   persist(
     (set, get) => ({ /* store */ }),
     {
       name: 'auth-storage',
       partialize: (state) => ({ 
         user: state.user, 
         token: state.token 
       })
     }
   )
   ```

4. **避免布局抖动**：
   - 导航栏固定高度（sticky positioning）
   - 骨架屏占位（用户信息加载时）

---

## 总结

### 已解决的 NEEDS CLARIFICATION

| 项目 | 决策 | 文档章节 |
|------|------|----------|
| 模态框组件库 | Radix UI Dialog | §1 |
| 认证 API 契约 | REST + JWT，详细端点定义 | §2 |
| E2E 测试工具 | 可选（优先单元测试） | §3 |
| 图标选择 | Lucide React 语义化映射 | §4 |
| 响应式策略 | 移动优先 + Tailwind 断点 | §5 |
| 性能优化 | 懒加载 + 代码分割 | §6 |

### 下一步：Phase 1 设计

所有技术决策已明确，可以进入 Phase 1：
1. 生成数据模型（data-model.md）
2. 定义 API 契约（contracts/）
3. 编写快速开始指南（quickstart.md）
