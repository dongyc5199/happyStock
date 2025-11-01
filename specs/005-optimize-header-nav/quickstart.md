# Quick Start Guide - Feature 005

**功能**: 优化首页标题栏导航（图标 + 登录/注册）  
**分支**: `005-optimize-header-nav`  
**预计工作量**: 8-12 小时  

## 目录

1. [前置条件](#1-前置条件)
2. [环境准备](#2-环境准备)
3. [架构概览](#3-架构概览)
4. [实现步骤](#4-实现步骤)
5. [测试指南](#5-测试指南)
6. [常见问题](#6-常见问题)

---

## 1. 前置条件

### 1.1 必需知识

- ✅ TypeScript 基础（类型定义、接口）
- ✅ React 19 基础（useState、useEffect）
- ✅ Next.js 15 基础（App Router、路由）
- ✅ Tailwind CSS 基础（响应式设计）

### 1.2 可选知识（推荐学习）

- 📚 Radix UI Dialog（模态框库）
- 📚 Zustand（状态管理）
- 📚 JWT 认证原理

### 1.3 已安装依赖

检查 `frontend/package.json` 确认以下依赖存在：

```json
{
  "dependencies": {
    "next": "^15.4.6",
    "react": "^19.1.0",
    "lucide-react": "^0.468.0",
    "zustand": "^5.0.8",
    "@radix-ui/react-dialog": "^1.1.4"  // 需要新增
  }
}
```

---

## 2. 环境准备

### 2.1 安装新依赖

```bash
cd frontend
npm install @radix-ui/react-dialog
```

### 2.2 启动开发服务器

**前端**:

```bash
cd frontend
npm run dev
# 访问 http://localhost:3000
```

**后端（如果需要测试认证 API）**:

```bash
cd backend
python main.py
# API 运行在 http://localhost:8000
```

### 2.3 切换到功能分支

```bash
git checkout 005-optimize-header-nav
git pull origin 005-optimize-header-nav
```

---

## 3. 架构概览

### 3.1 组件层级结构

```
src/
├── app/
│   └── layout.tsx                    [MODIFY] 添加 Header 组件
│
├── components/
│   ├── layout/
│   │   ├── Header.tsx               [NEW] 主导航栏组件
│   │   ├── NavigationMenu.tsx       [NEW] 导航菜单（桌面端）
│   │   ├── MobileMenu.tsx           [NEW] 移动端汉堡菜单
│   │   └── UserMenu.tsx             [NEW] 用户下拉菜单
│   │
│   └── auth/
│       ├── LoginModal.tsx           [NEW] 登录模态框
│       └── RegisterModal.tsx        [NEW] 注册模态框
│
├── lib/
│   ├── stores/
│   │   ├── authStore.ts            [NEW] Zustand 认证状态
│   │   └── uiStore.ts              [NEW] UI 状态（可选）
│   │
│   └── api/
│       └── auth.ts                  [NEW] 认证 API 调用
│
└── types/
    └── auth.ts                      [NEW] 认证相关类型定义
```

### 3.2 数据流

```
用户交互 → UI 组件 → Zustand Store → API 调用 → 后端
                          ↓
                    localStorage 持久化
```

---

## 4. 实现步骤

### 4.1 Phase 1: 类型定义和 API 客户端（1小时）

#### 1.1 创建类型文件

**文件**: `frontend/src/types/auth.ts`

```typescript
export interface User {
  id: string;
  username: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}

export interface AuthSession {
  user: User;
  token: string;
  expires_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// API 响应类型
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: { field: string };
  };
}
```

#### 1.2 创建 API 客户端

**文件**: `frontend/src/lib/api/auth.ts`

```typescript
import type { 
  LoginCredentials, 
  RegisterData, 
  AuthSession, 
  User,
  ApiResponse 
} from '@/types/auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthSession>> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return response.json();
  },

  async register(data: RegisterData): Promise<ApiResponse<AuthSession>> {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async getCurrentUser(token: string): Promise<ApiResponse<{ user: User }>> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },

  async logout(token: string): Promise<ApiResponse<{ message: string }>> {
    const response = await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
};
```

---

### 4.2 Phase 2: Zustand Store（1-2小时）

**文件**: `frontend/src/lib/stores/authStore.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, LoginCredentials, RegisterData } from '@/types/auth';
import { authApi } from '@/lib/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          if (response.success && response.data) {
            set({
              user: response.data.user,
              token: response.data.token,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            throw new Error(response.error?.message || '登录失败');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '网络错误',
            isLoading: false,
          });
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(data);
          if (response.success && response.data) {
            set({
              user: response.data.user,
              token: response.data.token,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            throw new Error(response.error?.message || '注册失败');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '网络错误',
            isLoading: false,
          });
        }
      },

      logout: async () => {
        const token = get().token;
        if (token) {
          try {
            await authApi.logout(token);
          } catch (error) {
            console.error('Logout API error:', error);
          }
        }
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      fetchCurrentUser: async () => {
        const token = get().token;
        if (!token) return;

        try {
          const response = await authApi.getCurrentUser(token);
          if (response.success && response.data) {
            set({ user: response.data.user, isAuthenticated: true });
          } else {
            // Token 无效，清除状态
            set({ user: null, token: null, isAuthenticated: false });
          }
        } catch (error) {
          set({ user: null, token: null, isAuthenticated: false });
        }
      },

      clearError: () => set({ error: null }),
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

### 4.3 Phase 3: 认证模态框（2-3小时）

#### 3.1 登录模态框

**文件**: `frontend/src/components/auth/LoginModal.tsx`

```typescript
'use client';

import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useAuthStore } from '@/lib/stores/authStore';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToRegister: () => void;
}

export function LoginModal({ isOpen, onClose, onSwitchToRegister }: LoginModalProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login({ username, password });
    if (!useAuthStore.getState().error) {
      onClose(); // 登录成功后关闭模态框
    }
  };

  const handleClose = () => {
    clearError();
    onClose();
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={handleClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg p-6 w-full max-w-md z-50">
          <div className="flex justify-between items-center mb-4">
            <Dialog.Title className="text-2xl font-bold">登录</Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-500 hover:text-gray-700">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded">{error}</div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1">用户名/邮箱</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? '登录中...' : '登录'}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-600">
            还没有账号？
            <button
              onClick={onSwitchToRegister}
              className="text-blue-600 hover:underline ml-1"
            >
              立即注册
            </button>
          </p>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

#### 3.2 注册模态框

**文件**: `frontend/src/components/auth/RegisterModal.tsx`（类似结构，添加邮箱字段和密码确认）

---

### 4.4 Phase 4: 导航组件（3-4小时）

#### 4.1 主 Header 组件

**文件**: `frontend/src/components/layout/Header.tsx`

```typescript
'use client';

import { useState } from 'react';
import { NavigationMenu } from './NavigationMenu';
import { MobileMenu } from './MobileMenu';
import { UserMenu } from './UserMenu';
import { LoginModal } from '../auth/LoginModal';
import { RegisterModal } from '../auth/RegisterModal';
import { useAuthStore } from '@/lib/stores/authStore';
import { LogIn, UserPlus } from 'lucide-react';

export function Header() {
  const { isAuthenticated } = useAuthStore();
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 bg-white border-b z-30">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="text-xl font-bold">happyStock</div>

          {/* 桌面导航 */}
          <div className="hidden md:flex items-center gap-6">
            <NavigationMenu />
            {isAuthenticated ? (
              <UserMenu />
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => setIsLoginOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded"
                >
                  <LogIn className="w-4 h-4" />
                  登录
                </button>
                <button
                  onClick={() => setIsRegisterOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded"
                >
                  <UserPlus className="w-4 h-4" />
                  注册
                </button>
              </div>
            )}
          </div>

          {/* 移动端菜单 */}
          <div className="md:hidden">
            <MobileMenu />
          </div>
        </div>
      </header>

      {/* 模态框 */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onSwitchToRegister={() => {
          setIsLoginOpen(false);
          setIsRegisterOpen(true);
        }}
      />
      <RegisterModal
        isOpen={isRegisterOpen}
        onClose={() => setIsRegisterOpen(false)}
        onSwitchToLogin={() => {
          setIsRegisterOpen(false);
          setIsLoginOpen(true);
        }}
      />
    </>
  );
}
```

#### 4.2 桌面导航菜单

**文件**: `frontend/src/components/layout/NavigationMenu.tsx`

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, TrendingUp, LayoutGrid, Info } from 'lucide-react';

const navItems = [
  { id: 'home', label: '首页', href: '/', icon: Home },
  { id: 'market', label: '市场行情', href: '/virtual-market', icon: TrendingUp },
  { id: 'sectors', label: '板块', href: '/sectors', icon: LayoutGrid },
  { id: 'about', label: '关于', href: '/about', icon: Info },
];

export function NavigationMenu() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-1">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;

        return (
          <Link
            key={item.id}
            href={item.href}
            className={`
              flex items-center gap-2 px-3 py-2 rounded transition-colors
              ${isActive 
                ? 'bg-blue-100 text-blue-700 font-medium' 
                : 'text-gray-700 hover:bg-gray-100'
              }
            `}
          >
            <Icon className="w-4 h-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
```

---

### 4.5 Phase 5: 集成到 Layout（0.5小时）

**文件**: `frontend/src/app/layout.tsx`

```typescript
import { Header } from '@/components/layout/Header';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
```

---

## 5. 测试指南

### 5.1 单元测试（Jest + React Testing Library）

**文件**: `frontend/src/components/auth/__tests__/LoginModal.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginModal } from '../LoginModal';
import { useAuthStore } from '@/lib/stores/authStore';

jest.mock('@/lib/stores/authStore');

describe('LoginModal', () => {
  it('应该显示登录表单', () => {
    render(<LoginModal isOpen={true} onClose={() => {}} onSwitchToRegister={() => {}} />);
    expect(screen.getByLabelText('用户名/邮箱')).toBeInTheDocument();
    expect(screen.getByLabelText('密码')).toBeInTheDocument();
  });

  it('应该在提交时调用 login', async () => {
    const mockLogin = jest.fn();
    (useAuthStore as any).mockReturnValue({ login: mockLogin, isLoading: false, error: null });

    render(<LoginModal isOpen={true} onClose={() => {}} onSwitchToRegister={() => {}} />);
    
    fireEvent.change(screen.getByLabelText('用户名/邮箱'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('密码'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByText('登录'));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({ username: 'testuser', password: 'password123' });
    });
  });
});
```

### 5.2 手动测试清单

#### ✅ 桌面端（≥768px）

- [ ] 导航菜单显示 4 个带图标的菜单项
- [ ] 点击菜单项可正常跳转
- [ ] 当前页面对应的菜单项高亮显示
- [ ] 未登录时显示"登录"和"注册"按钮
- [ ] 点击"登录"弹出登录模态框
- [ ] 点击"注册"弹出注册模态框
- [ ] 成功登录后显示用户名（超过12字符截断）和头像
- [ ] 点击用户名显示下拉菜单（退出登录选项）

#### ✅ 移动端（<768px）

- [ ] 显示汉堡菜单图标
- [ ] 点击汉堡菜单打开全屏/抽屉菜单
- [ ] 菜单内显示导航项 + 登录/注册按钮
- [ ] 点击菜单项自动关闭菜单
- [ ] 滚动页面自动关闭菜单
- [ ] 旋转设备自动关闭菜单

#### ✅ 认证流程

- [ ] 输入有效凭据可成功登录
- [ ] 输入错误密码显示错误提示
- [ ] 注册新用户自动登录
- [ ] 用户名/邮箱已存在显示冲突提示
- [ ] 刷新页面后保持登录状态
- [ ] 点击"退出登录"清除状态

### 5.3 性能测试

- [ ] Header 组件首次渲染 <100ms
- [ ] 模态框打开动画 <300ms
- [ ] 图标加载时间 <50ms
- [ ] API 调用响应时间 <1s（本地）

---

## 6. 常见问题

### Q1: Radix UI Dialog 样式不生效？

**A**: 确保在 `tailwind.config.ts` 中配置了内容路径：

```typescript
export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './node_modules/@radix-ui/**/*.js',  // 添加此行
  ],
};
```

### Q2: localStorage 持久化失败？

**A**: 检查 Zustand persist 配置，确保 `name` 唯一且不与其他 store 冲突：

```typescript
persist(/* ... */, { name: 'auth-storage' })  // 确保此名称唯一
```

### Q3: 移动端菜单不自动关闭？

**A**: 确保在 `MobileMenu` 组件中添加了滚动监听器：

```typescript
useEffect(() => {
  const handleScroll = () => setIsOpen(false);
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

### Q4: Token 过期后如何处理？

**A**: 在 API 客户端中添加拦截器，401 错误时清除状态：

```typescript
if (response.status === 401) {
  useAuthStore.getState().logout();
}
```

### Q5: 如何调试 API 调用？

**A**: 在 `.env.local` 中设置日志级别：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_DEBUG=true
```

然后在 API 客户端中添加日志：

```typescript
if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
  console.log('API Request:', credentials);
}
```

---

## 7. 提交前检查清单

- [ ] 所有 TypeScript 错误已解决（`npm run type-check`）
- [ ] 代码格式化完成（`npm run format`）
- [ ] 单元测试通过（`npm run test`）
- [ ] 手动测试桌面端和移动端
- [ ] 验证响应式设计（Chrome DevTools 模拟器）
- [ ] 检查 Lighthouse 分数（性能 >90）
- [ ] 更新 `CHANGELOG.md`
- [ ] 提交代码并推送到远程分支

---

## 8. 下一步

完成实现后：

1. 运行 `/speckit.tasks` 生成详细任务清单
2. 提交 Pull Request 到主分支
3. 等待代码审查
4. 合并后部署到测试环境

---

**预计完成时间**: 8-12 小时  
**难度**: 中等  
**依赖**: 后端 API 需先完成 `/api/auth/*` 端点

祝开发顺利！🚀
