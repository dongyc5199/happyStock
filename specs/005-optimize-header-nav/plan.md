# Implementation Plan: 优化首页标题栏导航

**Branch**: `005-optimize-header-nav` | **Date**: 2025-10-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-optimize-header-nav/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

优化首页导航栏的用户体验，包括三个主要改进：

1. **为导航菜单项添加图标**：为每个导航链接（首页、市场行情、板块等）添加语义化图标，提升视觉识别度和导航效率，预期使新用户找到功能的时间减少30%

2. **添加登录/注册入口**：在导航栏右侧添加醒目的登录和注册按钮，点击后弹出模态框（不跳转页面），预期提升注册转化率20%

3. **已登录用户状态显示**：登录后在导航栏显示用户头像/用户名（最多12字符），点击展开下拉菜单提供个人中心、设置、退出等功能

技术方案：基于 Next.js 15 + React 19 + TypeScript 的前端实现，使用 Lucide React 图标库，Zustand 管理认证状态，模态框组件采用 Radix UI 或自定义实现，响应式设计在移动端（<768px）使用汉堡菜单。

## Technical Context

**Language/Version**: TypeScript 5.0+, JavaScript ES2022+  
**Primary Dependencies**: 
  - Next.js 15.4.6 (App Router)
  - React 19.1.0
  - Lucide React (图标库,已引入)
  - Zustand 5.0.8 (状态管理,已引入)
  - Tailwind CSS v4 (样式系统,已引入)
  - ✅ **已确定**: Radix UI Dialog (@radix-ui/react-dialog) - 模态框组件库
  - ✅ **已确定**: REST API 认证端点 - 详见 `contracts/auth-api.yaml`
  
**Storage**: 
  - 前端:localStorage (用户会话持久化,通过 Zustand persist)
  - 后端:假设已有后端 API (FastAPI/SQLite),存储 User 实体
  
**Testing**: 
  - Jest + React Testing Library (已配置)
  - ✅ **已确定**: E2E 测试为可选项,优先单元测试和集成测试
  
**Target Platform**: 
  - Web 浏览器（Chrome, Firefox, Safari, Edge）
  - 响应式设计：桌面（≥768px）、移动端（<768px）
  
**Project Type**: Web 应用（前端 + 后端分离架构）

**Performance Goals**: 
  - 导航栏渲染时间 <100ms
  - 模态框打开动画 <300ms
  - 图标加载时间 <50ms（图标库通常内联 SVG）
  - 首次交互时间 (FID) <100ms
  
**Constraints**: 
  - 移动端触摸目标最小 44x44px（符合 WCAG 2.1 AA）
  - 用户名显示最多 12 个字符
  - 汉堡菜单在页面滚动或屏幕旋转时自动关闭
  - 保持与现有柔和渐变色系（blue-50/indigo-50/purple-50）一致
  
**Scale/Scope**: 
  - 导航菜单项数量：5-8 个（可扩展）
  - 用户下拉菜单选项：3-5 个
  - 预期并发用户：10,000+（客户端渲染，无服务端压力）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution 文件为模板，项目尚未定义具体的开发原则和约束。基于现有项目结构和最佳实践，进行以下检查：

### 基础质量门禁

| 检查项 | 状态 | 说明 |
|--------|------|------|
| **组件独立性** | ✅ PASS | 导航栏、模态框、菜单组件可独立开发和测试 |
| **测试覆盖** | ⚠️ ADVISORY | 建议为关键交互（模态框打开/关闭、菜单切换）编写单元测试和集成测试 |
| **类型安全** | ✅ PASS | TypeScript 确保类型安全，已定义接口（NavigationItem, UserSession, UserProfile） |
| **性能标准** | ✅ PASS | 性能目标明确（<100ms 渲染，<300ms 动画），可通过 Lighthouse 验证 |
| **可访问性** | ✅ PASS | ARIA 标签、键盘导航、触摸目标尺寸（44x44px）已在规格中要求 |
| **响应式设计** | ✅ PASS | 明确的断点（768px）和移动端适配方案（汉堡菜单） |
| **向后兼容** | ✅ PASS | 仅为 UI 层优化，不影响现有功能和 API |

### 潜在风险

| 风险项 | 严重性 | 缓解措施 |
|--------|--------|----------|
| 认证 API 未定义 | 🟡 MEDIUM | Phase 0 研究中需明确登录/注册 API 契约 |
| 模态框库选择 | 🟢 LOW | Phase 0 研究对比 Radix UI、Headless UI 和自定义方案 |
| E2E 测试策略 | 🟢 LOW | 可选：若时间允许，添加 Playwright 测试关键流程 |

**结论**: ✅ 可以进入 Phase 0 研究阶段

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   └── page.tsx                           # [MODIFY] 更新 Header 组件引用
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header/                        # [NEW] 新建导航栏组件
│   │   │   │   ├── index.tsx                  # 主组件导出
│   │   │   │   ├── Header.tsx                 # 导航栏主组件
│   │   │   │   ├── DesktopNav.tsx            # 桌面端导航项
│   │   │   │   ├── MobileNav.tsx             # 移动端汉堡菜单
│   │   │   │   ├── UserMenu.tsx              # 用户下拉菜单
│   │   │   │   ├── AuthButtons.tsx           # 登录/注册按钮
│   │   │   │   └── Header.module.css         # 样式（或使用 Tailwind）
│   │   └── auth/
│   │       ├── LoginModal/                    # [NEW] 登录模态框
│   │       │   ├── index.tsx
│   │       │   ├── LoginModal.tsx
│   │       │   └── LoginForm.tsx
│   │       └── RegisterModal/                 # [NEW] 注册模态框
│   │           ├── index.tsx
│   │           ├── RegisterModal.tsx
│   │           └── RegisterForm.tsx
│   ├── store/
│   │   └── authStore.ts                       # [NEW] 用户认证状态管理
│   ├── lib/
│   │   └── api/
│   │       └── auth.ts                        # [NEW] 认证 API 调用
│   ├── types/
│   │   └── auth.ts                            # [NEW] 认证相关类型定义
│   └── hooks/
│       ├── useAuth.ts                         # [NEW] 认证状态 Hook
│       └── useMediaQuery.ts                   # [MODIFY] 响应式断点 Hook
└── __tests__/
    ├── components/
    │   ├── Header.test.tsx                    # [NEW] 导航栏单元测试
    │   ├── LoginModal.test.tsx                # [NEW] 登录模态框测试
    │   └── RegisterModal.test.tsx             # [NEW] 注册模态框测试
    └── integration/
        └── auth-flow.test.tsx                 # [NEW] 登录/注册流程集成测试

backend/
├── api/
│   └── [认证相关端点，假设已存在或将并行开发]
```

**Structure Decision**: 

选择 **Web 应用架构（前端 + 后端分离）**，因为：
1. 项目已采用 Next.js (frontend/) 和独立 backend/ 结构
2. 此功能主要为前端 UI 改进，后端仅涉及认证 API 调用
3. 前端新增组件遵循现有的组件化架构（components/layout/, components/auth/）
4. 状态管理使用已引入的 Zustand，保持一致性

## Complexity Tracking

**无复杂度违规**：此功能为标准的前端 UI 优化，不引入额外的架构复杂度。所有新增组件遵循现有的 React 组件模式和项目约定。
