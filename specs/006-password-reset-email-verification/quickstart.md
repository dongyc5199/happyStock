# Quick Start: 密码重置与邮箱验证

**Feature**: 006-password-reset-email-verification
**Date**: 2025-11-01

## 概述

本指南帮助开发者快速了解并开始实施密码重置与邮箱验证功能。

## 功能简介

### 核心功能
1. **密码重置**: 用户通过邮箱验证重置忘记的密码
2. **邮箱验证**: 注册后验证邮箱地址的有效性
3. **邮箱更改**: 已登录用户可以更改绑定的邮箱
4. **重新发送**: 处理邮件未送达或令牌过期的情况

### 用户流程示意

```
┌─ 密码重置流程 ─────────────────────────────────┐
│ 1. 用户点击"忘记密码"                           │
│ 2. 输入注册邮箱                                 │
│ 3. 收到包含重置链接的邮件                       │
│ 4. 点击链接，打开重置表单                       │
│ 5. 输入并确认新密码                             │
│ 6. 密码重置成功，使用新密码登录                 │
└─────────────────────────────────────────────────┘

┌─ 邮箱验证流程 ─────────────────────────────────┐
│ 1. 用户完成注册                                 │
│ 2. 系统自动发送验证邮件                         │
│ 3. 用户收到邮件，点击验证链接                   │
│ 4. 验证成功，账户标记为已验证                   │
│ 5. （可选）登录后可重新发送验证邮件             │
└─────────────────────────────────────────────────┘
```

## 技术架构

### 后端技术栈
- **Framework**: FastAPI 0.100+
- **ORM**: Tortoise-ORM
- **Email**: aiosmtplib (异步SMTP)
- **Templates**: Jinja2
- **Cache**: Redis (频率限制)
- **Queue**: FastAPI BackgroundTasks → Redis Queue (生产环境)

### 前端技术栈
- **Framework**: Next.js 15.4+ (App Router)
- **UI**: React 19+, Radix UI, Tailwind CSS
- **Forms**: React Hook Form + Zod
- **State**: Zustand

## 开发路线图

### Phase 1: 密码重置 (P1 - 核心功能)

**Backend Tasks**:
1. 创建数据模型 (`PasswordResetToken`, 扩展 `User`)
2. 实现令牌服务 (`TokenService`)
3. 实现邮件服务 (`EmailService`)
4. 创建密码重置API路由
5. 创建邮件模板
6. 编写单元测试和集成测试

**Frontend Tasks**:
1. 创建"忘记密码"页面 (`/auth/forgot-password`)
2. 创建密码重置表单页面 (`/auth/reset-password`)
3. 实现表单验证（React Hook Form + Zod）
4. 集成API调用
5. 添加错误处理和用户反馈

**Acceptance Criteria**:
- ✅ 用户可以请求密码重置
- ✅ 用户收到包含重置链接的邮件
- ✅ 令牌有效期为24小时
- ✅ 用户可以使用新密码登录
- ✅ 频率限制正常工作（5分钟3次）

---

### Phase 2: 邮箱验证 (P2)

**Backend Tasks**:
1. 创建 `EmailVerificationToken` 模型
2. 扩展注册API，发送验证邮件
3. 实现邮箱验证API
4. 创建验证邮件模板
5. 添加验证状态API
6. 编写测试

**Frontend Tasks**:
1. 创建邮箱验证页面 (`/auth/verify-email`)
2. 实现验证提醒横幅组件
3. 集成重新发送验证邮件功能
4. 更新注册流程，提示用户检查邮箱

**Acceptance Criteria**:
- ✅ 注册后自动发送验证邮件
- ✅ 用户可以通过链接验证邮箱
- ✅ 令牌有效期为48小时
- ✅ 未验证用户看到提醒横幅
- ✅ 用户可以重新发送验证邮件

---

### Phase 3: 重新发送机制 (P3)

**Backend Tasks**:
1. 实现重新发送API
2. 添加频率限制
3. 处理旧令牌失效逻辑
4. 编写测试

**Frontend Tasks**:
1. 在验证提醒横幅添加"重新发送"按钮
2. 实现冷却时间倒计时
3. 显示发送成功/失败提示

**Acceptance Criteria**:
- ✅ 用户可以请求重新发送验证邮件
- ✅ 频率限制生效（5分钟3次）
- ✅ 新令牌使旧令牌失效
- ✅ 显示剩余冷却时间

---

### Phase 4: 邮箱更改 (P4)

**Backend Tasks**:
1. 实现更改邮箱API
2. 实现确认更改API
3. 创建通知邮件模板
4. 编写测试

**Frontend Tasks**:
1. 在账户设置页面添加更改邮箱表单
2. 实现密码验证
3. 显示更改流程指引

**Acceptance Criteria**:
- ✅ 用户可以请求更改邮箱
- ✅ 新邮箱收到验证邮件
- ✅ 验证成功后更新邮箱
- ✅ 旧邮箱收到安全通知

---

## 环境配置

### 后端环境变量

```bash
# SMTP配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@happystock.com
SMTP_FROM_NAME=快乐股票

# Redis配置 (频率限制)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 应用配置
APP_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000

# 令牌有效期（秒）
PASSWORD_RESET_TOKEN_EXPIRY=86400  # 24小时
EMAIL_VERIFICATION_TOKEN_EXPIRY=172800  # 48小时
```

### 前端环境变量

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 快速开始

### 1. 安装依赖

**Backend**:
```bash
cd backend
pipenv install aiosmtplib jinja2 redis
```

**Frontend**:
```bash
cd frontend
npm install react-hook-form zod @hookform/resolvers
```

### 2. 数据库迁移

```bash
cd backend
# 创建迁移文件
pipenv run aerich migrate --name add_email_verification

# 执行迁移
pipenv run aerich upgrade
```

### 3. 配置SMTP

#### 选项1: 使用Gmail (开发环境)
1. 启用Gmail两步验证
2. 生成应用专用密码
3. 配置环境变量

#### 选项2: 使用第三方服务 (推荐生产环境)
- **SendGrid**: 免费额度 100封/天
- **AWS SES**: 按量付费
- **阿里云邮件推送**: 国内推荐

### 4. 启动Redis

```bash
# Windows (使用WSL或Redis for Windows)
redis-server

# macOS
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 5. 运行开发服务器

**Backend**:
```bash
cd backend
pipenv run uvicorn main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm run dev
```

### 6. 测试邮件发送

```bash
cd backend
# 运行邮件发送测试
pipenv run python -m pytest tests/test_email_service.py -v
```

---

## 开发检查清单

### Backend

- [ ] 数据模型创建并迁移
- [ ] 令牌服务实现（生成、验证、清理）
- [ ] 邮件服务实现（发送、模板渲染）
- [ ] 频率限制服务实现
- [ ] API路由实现（8个端点）
- [ ] 邮件模板创建（4个模板）
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试覆盖主要流程
- [ ] API文档更新（Swagger）
- [ ] 错误处理和日志记录

### Frontend

- [ ] 页面组件创建（3个页面）
- [ ] 表单组件实现（带验证）
- [ ] API服务封装
- [ ] 错误处理和用户反馈
- [ ] 响应式设计（移动端适配）
- [ ] 加载状态和禁用状态
- [ ] 成功/错误提示
- [ ] 组件测试

### DevOps

- [ ] 环境变量配置
- [ ] SMTP服务配置
- [ ] Redis部署
- [ ] 监控和告警设置
- [ ] 日志收集配置
- [ ] 备份策略

---

## 常见问题

### Q1: 邮件发送失败怎么办？

**A**: 检查以下几点：
1. SMTP配置是否正确
2. 防火墙是否阻止端口587/465
3. Gmail是否开启"允许不够安全的应用"
4. 查看 `email_logs` 表中的错误信息

### Q2: 如何测试邮件发送？

**A**: 使用以下工具：
1. **Mailtrap**: 邮件测试沙箱（推荐）
2. **MailHog**: 本地SMTP服务器
3. **Mock SMTP**: 单元测试中使用Mock对象

### Q3: 令牌被盗用怎么办？

**A**: 安全措施：
1. 强制HTTPS传输
2. 令牌一次性使用
3. 设置短有效期
4. 监控异常IP访问
5. 密码重置成功后撤销现有会话（可选）

### Q4: 如何清理过期令牌？

**A**: 设置定时任务：
```python
# 每天凌晨3点执行
@cron("0 3 * * *")
async def cleanup_expired_tokens():
    await PasswordResetToken.filter(
        expires_at__lt=datetime.now() - timedelta(days=30)
    ).delete()
```

### Q5: 如何提高邮件送达率？

**A**: 最佳实践：
1. 配置SPF、DKIM、DMARC记录
2. 使用专业的SMTP服务提供商
3. 维护良好的发送信誉
4. 避免触发垃圾邮件过滤器
5. 提供退订链接

---

## 性能优化

### 邮件发送优化
1. **异步发送**: 使用后台任务，不阻塞HTTP响应
2. **批量发送**: 如有多个邮件，批量处理
3. **连接池**: 复用SMTP连接
4. **失败重试**: 实现指数退避重试策略

### 数据库优化
1. **索引**: 为 `token`、`user_id`、`expires_at` 添加索引
2. **定期清理**: 删除过期令牌和旧日志
3. **分区**: 考虑对日志表按时间分区

### Redis优化
1. **滑动窗口**: 使用Sorted Set实现精确的频率限制
2. **过期时间**: 合理设置键的TTL
3. **连接池**: 复用Redis连接

---

## 监控和告警

### 关键指标

1. **邮件发送成功率**: 目标 > 95%
2. **密码重置完成率**: 目标 > 80%
3. **邮箱验证率**: 目标 > 70%
4. **API响应时间**: 目标 < 200ms (p95)
5. **频率限制触发次数**: 监控异常峰值

### 告警规则

```yaml
alerts:
  - name: 邮件发送失败率高
    condition: email_failure_rate > 0.05
    action: 通知开发团队

  - name: Redis连接失败
    condition: redis_connection_errors > 0
    action: 紧急通知运维

  - name: 令牌验证失败率高
    condition: token_validation_failure_rate > 0.2
    action: 通知安全团队
```

---

## 下一步

完成本指南后，您可以：
1. 查看 [API契约文档](./contracts/api-endpoints.md) 了解详细的端点规范
2. 查看 [数据模型文档](./data-model.md) 了解数据库设计
3. 查看 [研究文档](./research.md) 了解技术决策背景
4. 开始实施 Phase 1: 密码重置功能

---

## 参考资源

### 相关文档
- [Feature 005: 用户认证系统](../005-optimize-header-nav/spec.md)
- [API文档: http://localhost:8000/docs](http://localhost:8000/docs)

### 外部资源
- [OWASP密码重置最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [FastAPI后台任务文档](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Jinja2模板文档](https://jinja.palletsprojects.com/)
- [Redis频率限制模式](https://redis.io/docs/manual/patterns/distributed-locks/)

---

**最后更新**: 2025-11-01
**维护者**: Feature 006 开发团队
