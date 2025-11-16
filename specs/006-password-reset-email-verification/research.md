# Research: 密码重置与邮箱验证

**Date**: 2025-11-01
**Feature**: 006-password-reset-email-verification

## Research Questions & Decisions

### 1. 邮件发送方案选择

**Decision**: 使用 aiosmtplib + 异步任务队列（Redis Queue或Celery）

**Rationale**:
- **aiosmtplib**: 支持异步SMTP，与FastAPI的异步架构完美配合
- **异步任务队列**: 确保邮件发送不阻塞HTTP请求响应
- **灵活性**: 可配置使用第三方SMTP服务（SendGrid、AWS SES、阿里云邮件推送）或自建SMTP服务器

**Alternatives Considered**:
1. **同步发送 (smtplib)**: 
   - ❌ 会阻塞请求，用户体验差
   - ❌ SMTP超时会导致HTTP请求超时
   
2. **第三方SDK (SendGrid SDK, AWS SDK)**: 
   - ❌ 供应商锁定，迁移成本高
   - ❌ 需要学习特定SDK
   - ✅ 但作为SMTP配置选项保留

3. **直接使用FastAPI BackgroundTasks**:
   - ⚠️ 适合轻量任务，但缺乏持久化、重试、监控
   - ⚠️ 服务重启会丢失队列中的任务
   - ✅ 可作为MVP阶段的简化方案

**Implementation Path**: 
- Phase 1: 使用 FastAPI BackgroundTasks（快速MVP）
- Phase 2: 迁移到 Redis Queue（生产环境可靠性）

---

### 2. 令牌生成与存储策略

**Decision**: 使用 secrets.token_urlsafe(32) 生成，存储在数据库并设置过期时间

**Rationale**:
- **secrets模块**: Python标准库，加密安全的随机生成器（CSPRNG）
- **URL安全**: token_urlsafe生成的字符串可直接用于URL，无需额外编码
- **32字节**: 生成43个字符，提供足够的熵（256位安全性）
- **数据库存储**: 支持查询、过期检查、使用状态跟踪

**Alternatives Considered**:
1. **UUID4**:
   - ✅ 简单易用，全局唯一
   - ⚠️ 只有122位随机性，略低于256位标准
   - ⚠️ 格式固定（带连字符），不够灵活

2. **JWT Token**:
   - ❌ 无法撤销（除非维护黑名单）
   - ❌ 令牌内容可解码，可能泄露用户信息
   - ❌ 增加复杂度，不适合一次性验证场景

3. **HMAC签名的时间戳**:
   - ❌ 需要维护密钥
   - ❌ 无法主动撤销
   - ❌ 难以实现"单次使用"限制

**Token Structure**:
```python
token = secrets.token_urlsafe(32)  # 生成43字符URL安全字符串
```

**Database Schema**:
- `token`: 索引字段，用于快速查询
- `user_id`: 关联用户
- `created_at`: 创建时间
- `expires_at`: 过期时间（created_at + 有效期）
- `used_at`: 使用时间（NULL表示未使用）

---

### 3. 频率限制实现方案

**Decision**: 使用 Redis + 滑动窗口计数器

**Rationale**:
- **Redis**: 高性能、支持过期时间、原子操作
- **滑动窗口**: 比固定窗口更精确，避免边界突发流量
- **灵活性**: 可针对不同操作设置不同限制规则

**Alternatives Considered**:
1. **数据库计数**:
   - ❌ 性能差，增加数据库负载
   - ❌ 清理过期记录复杂

2. **内存计数器 (Python dict)**:
   - ❌ 不支持分布式部署
   - ❌ 服务重启丢失数据

3. **固定窗口计数器**:
   - ⚠️ 存在边界突发问题
   - ✅ 实现更简单，可作为简化方案

**Implementation Details**:
```python
# Key格式: ratelimit:password_reset:{email}
# Value: 请求时间戳列表
# TTL: 5分钟（窗口大小）

async def check_rate_limit(operation: str, identifier: str, 
                           window_seconds: int = 300, 
                           max_attempts: int = 3) -> bool:
    key = f"ratelimit:{operation}:{identifier}"
    now = time.time()
    window_start = now - window_seconds
    
    # 移除过期时间戳
    await redis.zremrangebyscore(key, 0, window_start)
    
    # 检查当前窗口内的请求数
    count = await redis.zcard(key)
    if count >= max_attempts:
        return False
    
    # 添加当前请求时间戳
    await redis.zadd(key, {str(now): now})
    await redis.expire(key, window_seconds)
    return True
```

---

### 4. 邮件模板引擎选择

**Decision**: Jinja2

**Rationale**:
- **成熟度**: Python生态中最广泛使用的模板引擎
- **功能**: 支持继承、宏、过滤器、条件判断
- **安全**: 自动转义HTML，防止XSS攻击
- **与FastAPI集成**: 有现成的集成方案

**Alternatives Considered**:
1. **字符串格式化 (f-string/format)**:
   - ❌ 无法实现复杂逻辑
   - ❌ HTML维护困难
   - ❌ 设计师无法独立编辑

2. **Mako**:
   - ⚠️ 更灵活，但学习曲线陡峭
   - ⚠️ 社区支持不如Jinja2

**Template Structure**:
```
templates/emails/
├── base.html              # 基础模板（品牌、样式）
├── password_reset.html    # 密码重置邮件
├── email_verification.html # 邮箱验证邮件
├── password_reset_success.html # 重置成功通知
└── email_change_notice.html    # 邮箱更改通知
```

---

### 5. 前端路由设计

**Decision**: 使用 Next.js App Router，查询参数传递令牌

**Rationale**:
- **App Router**: 现有项目使用App Router，保持一致性
- **查询参数**: 令牌较长，使用查询参数而非路径参数更易处理
- **安全性**: HTTPS确保令牌传输安全

**Routes**:
```typescript
/auth/forgot-password       // 请求密码重置
/auth/reset-password?token={token}  // 重置密码表单
/auth/verify-email?token={token}    // 邮箱验证
/settings                   // 账户设置（包含更改邮箱）
```

**Alternatives Considered**:
1. **路径参数** (`/reset-password/:token`):
   - ⚠️ 令牌出现在URL路径中，可能被日志记录
   - ⚠️ Next.js 动态路由处理略复杂

2. **POST表单提交令牌**:
   - ❌ 用户无法通过邮件直接点击链接
   - ❌ 用户体验差

---

### 6. 安全最佳实践

**Decisions**:

1. **防止邮箱枚举**:
   - 无论邮箱是否存在，返回相同的成功消息
   - 不在错误消息中泄露"用户不存在"信息

2. **令牌安全**:
   - 使用HTTPS传输
   - 令牌足够长（43字符）
   - 一次性使用（used_at字段）
   - 明确过期时间（24/48小时）

3. **频率限制**:
   - 按邮箱地址限制（5分钟3次）
   - 按IP地址限制（可选，防止分布式攻击）

4. **审计日志**:
   - 记录所有敏感操作
   - 记录邮件发送状态
   - 记录令牌使用情况

5. **密码策略**:
   - 最小8字符
   - 必须包含字母和数字
   - 重置后可选：使现有会话失效

---

### 7. 错误处理策略

**Decision**: 分层错误处理 + 用户友好提示

**Error Handling Layers**:

1. **SMTP错误**:
   ```python
   try:
       await send_email(...)
   except SMTPException as e:
       logger.error(f"SMTP error: {e}")
       # 不向用户暴露技术细节
       return "如果该邮箱存在，您将收到重置链接"
   ```

2. **令牌验证错误**:
   ```python
   if token.expires_at < now:
       return {"error": "链接已过期", "can_resend": True}
   if token.used_at:
       return {"error": "链接已使用", "can_resend": True}
   ```

3. **频率限制错误**:
   ```python
   if not await check_rate_limit(...):
       remaining = get_cooldown_remaining(...)
       return {"error": f"请求过于频繁，请{remaining}秒后重试"}
   ```

**User-Facing Messages**:
- ✅ 清晰说明问题
- ✅ 提供解决方案（如"重新发送"按钮）
- ✅ 避免技术术语
- ❌ 不泄露系统内部信息

---

### 8. 测试策略

**Test Coverage**:

1. **单元测试**:
   - 令牌生成和验证逻辑
   - 频率限制算法
   - 邮件模板渲染

2. **集成测试**:
   - 密码重置完整流程
   - 邮箱验证完整流程
   - API端点行为

3. **E2E测试**:
   - 用户从请求到完成重置的全流程
   - 邮箱验证从注册到验证成功

**Test Doubles**:
- **SMTP Mock**: 使用 aiosmtpd 或 Mock对象
- **Redis Mock**: 使用 fakeredis
- **Time Mock**: 使用 freezegun 测试过期逻辑

---

## Technology Stack Summary

### Backend
- **Framework**: FastAPI 0.100+
- **ORM**: Tortoise-ORM 0.19+
- **Email**: aiosmtplib 2.0+
- **Templates**: Jinja2 3.1+
- **Cache/Queue**: Redis 7.0+
- **Rate Limiting**: Redis + Sorted Sets
- **Testing**: pytest, pytest-asyncio, fakeredis

### Frontend
- **Framework**: Next.js 15.4+, React 19+
- **State**: Zustand 5.0+
- **UI**: Radix UI, Tailwind CSS
- **Forms**: React Hook Form + Zod
- **Testing**: Jest, React Testing Library

### Infrastructure
- **SMTP**: 支持任何SMTP服务（Gmail, SendGrid, AWS SES, 阿里云等）
- **Storage**: SQLite (dev), PostgreSQL (prod)
- **Cache**: Redis 7.0+

---

## Next Steps

Phase 0 研究完成，可以进入 Phase 1：
1. 设计数据模型 (data-model.md)
2. 定义API契约 (contracts/)
3. 创建快速开始指南 (quickstart.md)
