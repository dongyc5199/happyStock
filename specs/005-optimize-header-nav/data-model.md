# Data Model

**Feature**: 优化首页标题栏导航  
**Date**: 2025-10-31  
**Status**: Phase 1 Design

## 概述

此文档定义前端数据模型和状态结构。由于此功能主要为 UI 优化，数据模型侧重于前端状态管理和 API 响应格式。

---

## 1. 核心实体

### 1.1 User（用户）

**描述**: 代表已认证的用户信息

**字段**:

| 字段名 | 类型 | 必需 | 描述 | 验证规则 |
|--------|------|------|------|----------|
| `id` | string | ✅ | 用户唯一标识符（UUID） | 非空，UUID 格式 |
| `username` | string | ✅ | 用户名 | 3-20 字符，字母数字下划线 |
| `email` | string | ✅ | 邮箱地址 | 有效邮箱格式 |
| `avatar_url` | string \| null | ❌ | 头像 URL | URL 格式或 null |
| `created_at` | string | ✅ | 创建时间 | ISO 8601 日期时间 |

**TypeScript 定义**:

```typescript
export interface User {
  id: string;
  username: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}
```

**示例数据**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "happytrader",
  "email": "trader@example.com",
  "avatar_url": "https://example.com/avatars/user.jpg",
  "created_at": "2025-10-15T08:30:00Z"
}
```

---

### 1.2 AuthSession（认证会话）

**描述**: 用户认证会话信息，包含令牌和过期时间

**字段**:

| 字段名 | 类型 | 必需 | 描述 | 验证规则 |
|--------|------|------|------|----------|
| `user` | User | ✅ | 用户信息对象 | 参见 User 实体 |
| `token` | string | ✅ | JWT 认证令牌 | 非空，JWT 格式 |
| `expires_at` | string | ✅ | 令牌过期时间 | ISO 8601 日期时间 |

**TypeScript 定义**:

```typescript
export interface AuthSession {
  user: User;
  token: string;
  expires_at: string;
}
```

---

### 1.3 NavigationItem（导航项）

**描述**: 导航栏中的单个菜单项

**字段**:

| 字段名 | 类型 | 必需 | 描述 | 验证规则 |
|--------|------|------|------|----------|
| `id` | string | ✅ | 导航项唯一标识 | 非空，唯一 |
| `label` | string | ✅ | 显示文本 | 非空，1-20 字符 |
| `href` | string | ✅ | 链接地址 | 有效路径 |
| `icon` | LucideIcon | ✅ | 图标组件 | Lucide React 图标 |
| `order` | number | ✅ | 显示顺序 | 正整数 |

**TypeScript 定义**:

```typescript
import type { LucideIcon } from 'lucide-react';

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon: LucideIcon;
  order: number;
}
```

**示例数据**:

```typescript
import { Home, TrendingUp, LayoutGrid, Info } from 'lucide-react';

const navigationItems: NavigationItem[] = [
  { id: 'home', label: '首页', href: '/', icon: Home, order: 1 },
  { id: 'market', label: '市场行情', href: '/virtual-market', icon: TrendingUp, order: 2 },
  { id: 'sectors', label: '板块', href: '/sectors', icon: LayoutGrid, order: 3 },
  { id: 'about', label: '关于', href: '/about', icon: Info, order: 4 },
];
```

---

## 2. 前端状态结构（Zustand Store）

### 2.1 AuthStore（认证状态）

**描述**: 管理用户认证状态和相关操作

**状态字段**:

```typescript
export interface AuthState {
  // 状态
  user: User | null;                      // 当前用户，未登录为 null
  token: string | null;                   // JWT 令牌
  isAuthenticated: boolean;               // 是否已认证
  isLoading: boolean;                     // 是否正在加载（登录/注册中）
  error: string | null;                   // 错误信息
  
  // 操作方法
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}
```

**持久化策略**:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      // 操作实现...
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

---

### 2.2 UIStore（UI 状态 - 可选）

**描述**: 管理 UI 交互状态（模态框、菜单等）

**状态字段**:

```typescript
export interface UIState {
  // 模态框状态
  isLoginModalOpen: boolean;
  isRegisterModalOpen: boolean;
  
  // 移动端菜单状态
  isMobileMenuOpen: boolean;
  
  // 用户下拉菜单状态
  isUserMenuOpen: boolean;
  
  // 操作方法
  openLoginModal: () => void;
  closeLoginModal: () => void;
  openRegisterModal: () => void;
  closeRegisterModal: () => void;
  toggleMobileMenu: () => void;
  closeMobileMenu: () => void;
  toggleUserMenu: () => void;
  closeUserMenu: () => void;
  closeAllModals: () => void;
}
```

**注**: 也可以使用 React 本地 state（useState）管理这些 UI 状态，取决于是否需要跨组件共享。

---

## 3. API 请求/响应模型

### 3.1 登录请求

```typescript
export interface LoginCredentials {
  username: string;    // 或 email
  password: string;
}
```

### 3.2 登录响应

```typescript
export interface LoginResponse {
  success: boolean;
  data?: AuthSession;
  error?: {
    code: string;
    message: string;
  };
}
```

### 3.3 注册请求

```typescript
export interface RegisterData {
  username: string;    // 3-20 字符
  email: string;       // 有效邮箱
  password: string;    // 8-128 字符
}
```

### 3.4 注册响应

```typescript
export interface RegisterResponse {
  success: boolean;
  data?: AuthSession;
  error?: {
    code: 'USERNAME_TAKEN' | 'EMAIL_TAKEN' | 'VALIDATION_ERROR';
    message: string;
    details?: {
      field: string;
    };
  };
}
```

### 3.5 获取当前用户响应

```typescript
export interface MeResponse {
  success: boolean;
  data?: {
    user: User;
  };
  error?: {
    code: string;
    message: string;
  };
}
```

---

## 4. 数据验证规则

### 4.1 用户名验证

- **长度**: 3-20 字符
- **字符**: 字母、数字、下划线
- **正则**: `/^[a-zA-Z0-9_]{3,20}$/`
- **错误消息**: "用户名必须为3-20个字符，只能包含字母、数字和下划线"

### 4.2 邮箱验证

- **格式**: 标准邮箱格式
- **正则**: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- **错误消息**: "请输入有效的邮箱地址"

### 4.3 密码验证

- **长度**: 8-128 字符
- **要求**: 至少包含一个字母和一个数字（推荐）
- **正则**: `/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,128}$/`
- **错误消息**: "密码必须至少8个字符，包含字母和数字"

### 4.4 头像 URL 验证

- **格式**: HTTP/HTTPS URL
- **正则**: `/^https?:\/\/.+/`
- **可选**: 允许 null

---

## 5. 状态转换

### 5.1 认证状态机

```
┌─────────────┐
│ 未认证       │ (user = null, isAuthenticated = false)
└──────┬──────┘
       │
       │ login() / register()
       ↓
┌─────────────┐
│ 加载中       │ (isLoading = true)
└──────┬──────┘
       │
       ├─ 成功 ──→ ┌─────────────┐
       │           │ 已认证       │ (user != null, isAuthenticated = true)
       │           └──────┬──────┘
       │                  │
       │                  │ logout()
       │                  ↓
       └─ 失败 ──→ ┌─────────────┐
                   │ 错误         │ (error != null)
                   └──────┬──────┘
                          │
                          │ clearError()
                          ↓
                   ┌─────────────┐
                   │ 未认证       │
                   └─────────────┘
```

### 5.2 模态框状态转换

```
┌─────────────┐
│ 关闭         │ (isModalOpen = false)
└──────┬──────┘
       │
       │ 点击登录/注册按钮
       ↓
┌─────────────┐
│ 打开         │ (isModalOpen = true)
└──────┬──────┘
       │
       ├─ 点击关闭/遮罩 ──→ 关闭
       ├─ 提交成功      ──→ 关闭 + 更新认证状态
       └─ 提交失败      ──→ 保持打开 + 显示错误
```

---

## 6. 数据流图

### 6.1 登录流程数据流

```
用户输入                       前端                        后端API
  │                            │                            │
  │  输入用户名/密码              │                            │
  ├──────────────────────────→│                            │
  │                            │  POST /api/auth/login     │
  │                            ├───────────────────────────→│
  │                            │                            │
  │                            │  ← { success, data/error } │
  │                            │←───────────────────────────┤
  │                            │                            │
  │  ← 显示成功/错误              │  更新 Zustand store:       │
  │←───────────────────────────┤  - user                   │
  │                            │  - token                  │
  │                            │  - isAuthenticated        │
  │                            │  持久化到 localStorage     │
  │                            │  关闭模态框                │
```

### 6.2 页面加载时状态恢复

```
页面加载
  │
  ├─ 从 localStorage 读取 token
  │
  ├─ token 存在？
  │   ├─ 是 → GET /api/auth/me 验证 token
  │   │        ├─ 有效 → 更新 user 状态
  │   │        └─ 无效 → 清除 token + user
  │   └─ 否 → 保持未认证状态
  │
  └─ 渲染导航栏
       ├─ 已认证 → 显示用户菜单
       └─ 未认证 → 显示登录/注册按钮
```

---

## 7. 数据约束总结

| 实体/字段 | 约束 | 验证方式 |
|-----------|------|----------|
| User.id | UUID 格式 | 正则或库验证 |
| User.username | 3-20 字符，字母数字下划线 | 正则 `/^[a-zA-Z0-9_]{3,20}$/` |
| User.email | 有效邮箱格式 | 正则 `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` |
| User.avatar_url | URL 格式或 null | 正则 `/^https?:\/\/.+/` |
| 密码 | 8-128 字符，字母+数字 | 正则 `/^(?=.*[A-Za-z])(?=.*\d).{8,128}$/` |
| NavigationItem.label | 最多 20 字符 | 长度检查 |
| 用户名显示 | 最多 12 字符（截断） | UI 层处理 `substring(0, 12) + '...'` |

---

## 8. 性能考虑

### 8.1 数据缓存策略

- **用户信息**: 登录后缓存在 Zustand store + localStorage，页面刷新时从本地恢复
- **Token 刷新**: 如果后端支持 refresh token，在 token 快过期时自动刷新
- **API 调用频率**: 避免频繁调用 `/api/auth/me`，仅在页面加载时验证一次

### 8.2 数据大小优化

- **Token 存储**: JWT 通常 <1KB，localStorage 限制为 5MB，足够
- **用户信息**: 最小化缓存字段，仅存储必要信息（id, username, email, avatar_url）

---

## 总结

此数据模型定义了：
1. ✅ 3 个核心实体（User, AuthSession, NavigationItem）
2. ✅ 2 个前端状态结构（AuthStore, UIStore）
3. ✅ 4 组 API 请求/响应模型
4. ✅ 完整的验证规则和约束
5. ✅ 状态转换和数据流图

**下一步**: 生成 API 契约（OpenAPI 规范）和快速开始指南。
