# P4/P5 后端 API 就绪状态检查报告

## 检查时间
2025年11月1日

## 检查范围
- P4: 用户登录/注册功能
- P5: 用户菜单功能

## API 需求清单

根据 `contracts/auth-api.yaml`，需要以下 4 个端点:

### 1. POST /api/auth/login
- **功能**: 用户登录
- **请求**: `{ username, password }`
- **响应**: `{ success, data: { user, token, expires_at } }`
- **状态**: ❌ **未实现**

### 2. POST /api/auth/register
- **功能**: 用户注册
- **请求**: `{ username, email, password }`
- **响应**: `{ success, data: { user, token, expires_at } }`
- **状态**: ❌ **未实现**

### 3. GET /api/auth/me
- **功能**: 获取当前用户信息
- **认证**: Bearer JWT Token
- **响应**: `{ success, data: { user } }`
- **状态**: ❌ **未实现**

### 4. POST /api/auth/logout
- **功能**: 用户登出
- **认证**: Bearer JWT Token
- **响应**: `{ success, message }`
- **状态**: ❌ **未实现**

## 数据库状态

### 用户表 (users)
- **表定义**: ✅ 存在于 `sql_scripts/create_user_table.sql`
- **模型定义**: ✅ 存在于 `backend/models/user.py`
- **字段**:
  - `id` INT (主键)
  - `username` VARCHAR(50) UNIQUE
  - `email` VARCHAR(100) UNIQUE
  - `password_hash` VARCHAR(255)
  - `created_at` TIMESTAMP
  - `updated_at` TIMESTAMP

### 用户资料表 (user_profiles)
- **表定义**: ✅ 存在于 SQL 脚本
- **字段**:
  - `user_id` INT (外键)
  - `full_name` VARCHAR(100)
  - `avatar_url` VARCHAR(255)
  - `bio` TEXT

**注意**: 模型中缺少 `avatar_url` 字段,但 API 契约需要该字段

## 后端实现状态

### 路由 (Routers)
**检查路径**: `backend/routers/`
- ✅ `accounts.py` - 账户管理
- ✅ `assets.py` - 资产管理
- ✅ `holdings.py` - 持仓管理
- ✅ `klines.py` - K线数据
- ✅ `trades.py` - 交易管理
- ❌ **缺少 `auth.py`** - 认证路由

### API 端点
**检查路径**: `backend/api/`
- ✅ `indices.py` - 指数API
- ✅ `market.py` - 市场API
- ✅ `schemas.py` - 数据模型
- ✅ `sectors.py` - 板块API
- ✅ `stocks.py` - 股票API
- ✅ `websocket.py` - WebSocket API
- ❌ **缺少认证相关 API**

### main.py 注册
**检查结果**: 
- 已注册路由: `accounts`, `assets`, `trades`, `holdings`, `klines`, 虚拟市场APIs, WebSocket
- ❌ **未注册认证路由**

## 依赖包检查

### JWT 相关依赖
**检查文件**: `backend/Pipfile.lock`
- ❌ **未找到 `python-jose`** (JWT 编码/解码)
- ❌ **未找到 `passlib`** (密码哈希)
- ❌ **未找到 `bcrypt`** (密码加密算法)

### 需要安装的依赖
```bash
pipenv install python-jose[cryptography]
pipenv install passlib[bcrypt]
```

## 缺失组件清单

### 1. 认证路由 (backend/routers/auth.py)
需要实现:
- `POST /api/v1/auth/login` - 登录
- `POST /api/v1/auth/register` - 注册
- `GET /api/v1/auth/me` - 获取当前用户
- `POST /api/v1/auth/logout` - 登出

### 2. 认证服务 (backend/services/auth_service.py)
需要实现:
- `hash_password()` - 密码哈希
- `verify_password()` - 密码验证
- `create_access_token()` - 生成 JWT
- `decode_access_token()` - 解析 JWT
- `authenticate_user()` - 用户认证
- `register_user()` - 用户注册

### 3. 认证 Schema (backend/schemas/auth.py)
需要实现:
- `LoginRequest` - 登录请求
- `RegisterRequest` - 注册请求
- `AuthResponse` - 认证响应
- `UserResponse` - 用户信息响应

### 4. JWT 中间件/依赖
需要实现:
- `get_current_user()` - FastAPI Depends 函数
- JWT token 验证逻辑

### 5. 数据模型更新
需要更新 `backend/models/user.py`:
- 添加 `avatar_url` 字段 (或创建 UserProfile 模型)
- 添加密码验证方法
- 添加序列化方法

## 前端影响评估

### 当前状态
前端已实现:
- ✅ `lib/api/auth.ts` - API 客户端
- ✅ `lib/stores/authStore.ts` - 状态管理
- ✅ `components/auth/*` - UI 组件
- ✅ `types/auth.ts` - TypeScript 类型

### Mock 数据方案
**选项 1: 前端 Mock**
- 在 `lib/api/auth.ts` 中添加 mock 响应
- 优点: 前端独立开发
- 缺点: 无法测试真实后端集成

**选项 2: 使用 MSW (Mock Service Worker)**
- 安装 `msw` 依赖
- 创建 mock handlers
- 优点: 接近真实 HTTP 请求
- 缺点: 需要额外配置

**选项 3: 后端 Mock 端点**
- 在后端创建临时 mock 路由
- 优点: 测试真实 HTTP 通信
- 缺点: 需要修改后端代码

## 建议优先级

### P0 - 立即执行 (MVP 必需)
1. ✅ **安装依赖包**
   ```bash
   cd backend
   pipenv install python-jose[cryptography] passlib[bcrypt]
   ```

2. ✅ **创建认证服务** (`backend/services/auth_service.py`)
   - 实现密码哈希和验证
   - 实现 JWT 生成和解析

3. ✅ **创建认证 Schema** (`backend/schemas/auth.py`)
   - 定义请求/响应模型

4. ✅ **创建认证路由** (`backend/routers/auth.py`)
   - 实现 4 个 API 端点
   - 在 `main.py` 中注册路由

5. ✅ **更新用户模型**
   - 添加 `avatar_url` 字段

### P1 - 短期执行 (完善功能)
6. ⏭️ **Token 黑名单** (可选)
   - 使用 Redis 存储已登出的 token
   - 实现真正的 logout

7. ⏭️ **刷新 Token** (可选)
   - 实现 refresh token 机制
   - 延长用户会话

### P2 - 中期执行 (增强安全)
8. ⏭️ **速率限制**
   - 防止暴力破解
   - 使用 `slowapi` 或 Redis

9. ⏭️ **邮箱验证**
   - 注册后发送验证邮件
   - SMTP 配置

## 时间估算

| 任务 | 工作量 | 说明 |
|-----|-------|-----|
| 安装依赖 | 5分钟 | pipenv install |
| 认证服务 | 2小时 | 核心逻辑实现 |
| 认证Schema | 30分钟 | Pydantic 模型 |
| 认证路由 | 2小时 | 4个端点+错误处理 |
| 用户模型更新 | 30分钟 | 添加字段+迁移 |
| 集成测试 | 1小时 | 测试所有端点 |
| **总计** | **约6小时** | 1个工作日 |

## 临时解决方案 (前端 Mock)

如果需要立即测试前端功能,可以临时在前端添加 mock 数据:

```typescript
// lib/api/auth.ts
export const authApi = {
  async login(credentials: LoginCredentials) {
    // TODO: 移除 mock,连接真实后端
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      success: true,
      data: {
        user: {
          id: '1',
          username: credentials.username,
          email: 'mock@example.com',
          avatar_url: null,
          created_at: new Date().toISOString(),
        },
        token: 'mock-jwt-token-' + Date.now(),
        expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      },
    };
  },
  // ... 其他方法也类似
};
```

## 结论

### 总体状态: ❌ **后端 API 未就绪**

**缺失组件**:
- 4 个认证 API 端点 (100% 未实现)
- JWT 依赖包 (未安装)
- 认证服务层 (未实现)
- 认证中间件 (未实现)

**已就绪组件**:
- ✅ 数据库表结构
- ✅ 用户模型 (部分)
- ✅ FastAPI 基础架构

**推荐方案**:
1. **短期**: 使用前端 Mock 完成 UI 开发和测试
2. **中期**: 实现完整的后端认证 API (约1个工作日)
3. **长期**: 增强安全特性 (速率限制、邮箱验证等)

---

**报告生成时间**: 2025-11-01
**检查人**: GitHub Copilot
**状态**: 待后端实现
