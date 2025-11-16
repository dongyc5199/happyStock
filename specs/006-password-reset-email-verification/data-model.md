# Data Model: 密码重置与邮箱验证

**Date**: 2025-11-01
**Feature**: 006-password-reset-email-verification

## Entity Definitions

### 1. PasswordResetToken (密码重置令牌)

**Purpose**: 存储用户密码重置请求的验证令牌

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | 主键 |
| token | String(64) | Unique, Indexed, Not Null | URL安全的随机令牌（43字符） |
| user_id | Integer | FK(User.id), Not Null | 关联的用户ID |
| created_at | DateTime | Not Null, Default=now() | 令牌创建时间 |
| expires_at | DateTime | Not Null | 令牌过期时间（创建时间+24小时） |
| used_at | DateTime | Nullable | 令牌使用时间（NULL=未使用） |
| ip_address | String(45) | Nullable | 请求来源IP地址（IPv6支持） |

**Indexes**:
- `idx_token`: UNIQUE on `token` (快速查询验证)
- `idx_user_id`: on `user_id` (查询用户的令牌历史)
- `idx_expires_at`: on `expires_at` (清理过期令牌)

**Validation Rules**:
- `token` 必须是43字符的URL安全字符串
- `expires_at` 必须大于 `created_at`
- `used_at` 如果不为NULL，必须在 `created_at` 和 `expires_at` 之间
- 每个用户可以有多个未过期的令牌，但建议限制数量（如最多3个）

**State Transitions**:
```
[Created] → token生成，used_at=NULL
    ↓
[Valid] → token未过期，used_at=NULL
    ↓
[Used] → token已使用，used_at=时间戳
    OR
[Expired] → 当前时间 > expires_at
```

**Business Rules**:
- 令牌只能使用一次
- 令牌使用后立即标记 `used_at`
- 过期令牌无法使用
- 密码重置成功后，该用户的所有其他令牌应失效

---

### 2. EmailVerificationToken (邮箱验证令牌)

**Purpose**: 存储用户邮箱验证请求的验证令牌

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | 主键 |
| token | String(64) | Unique, Indexed, Not Null | URL安全的随机令牌（43字符） |
| user_id | Integer | FK(User.id), Not Null | 关联的用户ID |
| email | String(255) | Not Null | 待验证的邮箱地址 |
| created_at | DateTime | Not Null, Default=now() | 令牌创建时间 |
| expires_at | DateTime | Not Null | 令牌过期时间（创建时间+48小时） |
| used_at | DateTime | Nullable | 令牌使用时间（NULL=未使用） |
| token_type | Enum | Not Null | 令牌类型：'registration', 'email_change' |

**Indexes**:
- `idx_token`: UNIQUE on `token`
- `idx_user_id`: on `user_id`
- `idx_email`: on `email` (查询特定邮箱的验证状态)
- `idx_expires_at`: on `expires_at`

**Validation Rules**:
- `email` 必须是有效的邮箱格式
- `token` 必须是43字符的URL安全字符串
- `expires_at` 必须大于 `created_at`
- `token_type` 必须是 'registration' 或 'email_change'
- 同一用户的同一邮箱只能有一个有效的验证令牌

**State Transitions**:
```
[Created] → token生成，used_at=NULL，email_verified=False
    ↓
[Pending] → 等待用户点击验证链接
    ↓
[Verified] → used_at=时间戳，User.email_verified=True
    OR
[Expired] → 当前时间 > expires_at
```

**Business Rules**:
- 令牌只能使用一次
- 验证成功后，更新 User.email_verified 和 User.email_verified_at
- 如果是邮箱更改验证，成功后更新 User.email
- 发送新令牌时，之前的未使用令牌应失效

---

### 3. User (用户 - 扩展现有模型)

**Purpose**: 存储用户账户信息

**New Fields** (添加到现有模型):
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| email_verified | Boolean | Not Null, Default=False | 邮箱是否已验证 |
| email_verified_at | DateTime | Nullable | 邮箱验证时间 |

**Existing Fields** (引用):
- id (Integer, PK)
- username (String)
- email (String, Unique)
- password_hash (String)
- avatar_url (String, Nullable)
- created_at (DateTime)
- updated_at (DateTime)

**Validation Rules**:
- `email_verified_at` 只有在 `email_verified=True` 时才能有值
- 邮箱更改时，`email_verified` 重置为 False

**Business Rules**:
- 注册时，`email_verified` 默认为 False
- 邮箱验证成功后，设置 `email_verified=True` 和 `email_verified_at`
- 更改邮箱时，发送验证邮件到新邮箱，验证成功后更新 email 和重置验证状态

---

### 4. EmailLog (邮件发送日志)

**Purpose**: 记录所有邮件发送操作，用于审计和故障排查

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | 主键 |
| user_id | Integer | FK(User.id), Nullable | 关联的用户ID（可选） |
| recipient_email | String(255) | Not Null, Indexed | 收件人邮箱 |
| email_type | Enum | Not Null | 邮件类型：'password_reset', 'email_verification', 'password_reset_success', 'email_change_notice' |
| subject | String(255) | Not Null | 邮件主题 |
| sent_at | DateTime | Not Null, Default=now() | 发送时间 |
| status | Enum | Not Null | 发送状态：'pending', 'sent', 'failed' |
| error_message | Text | Nullable | 错误信息（如果发送失败） |
| smtp_message_id | String(255) | Nullable | SMTP消息ID |

**Indexes**:
- `idx_user_id`: on `user_id`
- `idx_recipient_email`: on `recipient_email`
- `idx_email_type`: on `email_type`
- `idx_sent_at`: on `sent_at` (按时间查询)
- `idx_status`: on `status` (查询失败记录)

**Validation Rules**:
- `recipient_email` 必须是有效的邮箱格式
- `email_type` 必须是枚举值之一
- `status` 必须是 'pending', 'sent', 'failed' 之一
- 如果 `status='failed'`，`error_message` 应该有值

**Business Rules**:
- 每次尝试发送邮件都创建一条记录
- 初始状态为 'pending'
- 发送成功后更新为 'sent' 并记录 `smtp_message_id`
- 发送失败后更新为 'failed' 并记录 `error_message`
- 日志保留期：建议90天（可配置）

---

## Entity Relationships

```
User (1) ───< (*) PasswordResetToken
User (1) ───< (*) EmailVerificationToken
User (1) ───< (*) EmailLog
```

**Relationship Details**:

1. **User → PasswordResetToken** (One-to-Many)
   - 一个用户可以有多个密码重置令牌（历史记录）
   - 但同时只应有少量未过期的令牌

2. **User → EmailVerificationToken** (One-to-Many)
   - 一个用户可以有多个邮箱验证令牌
   - 同一邮箱地址只应有一个有效令牌

3. **User → EmailLog** (One-to-Many, Optional)
   - 一个用户可以收到多封邮件
   - EmailLog 可以不关联用户（如发送到未注册邮箱的情况）

---

## Data Lifecycle

### Password Reset Token Lifecycle

```
1. 用户请求重置
   └─> 创建 PasswordResetToken (used_at=NULL)
   └─> 创建 EmailLog (status='pending')
   └─> 发送邮件
       ├─> 成功: EmailLog.status='sent'
       └─> 失败: EmailLog.status='failed'

2. 用户点击链接
   └─> 验证 token (是否存在、是否过期、是否已用)
       ├─> 有效: 显示重置表单
       └─> 无效: 显示错误提示 + 重新发送选项

3. 用户提交新密码
   └─> 更新 User.password_hash
   └─> 更新 PasswordResetToken.used_at
   └─> 使该用户的其他未使用令牌失效
   └─> 发送确认邮件 (EmailLog)
```

### Email Verification Token Lifecycle

```
1. 用户注册 / 请求重新发送
   └─> 创建 EmailVerificationToken (used_at=NULL)
   └─> 创建 EmailLog (status='pending')
   └─> 发送验证邮件

2. 用户点击验证链接
   └─> 验证 token
       ├─> 有效:
       │   └─> 更新 User.email_verified=True
       │   └─> 更新 User.email_verified_at
       │   └─> 更新 EmailVerificationToken.used_at
       │   └─> 显示成功页面
       └─> 无效: 显示错误 + 重新发送选项
```

### Email Change Lifecycle

```
1. 用户提交新邮箱
   └─> 创建 EmailVerificationToken (email=新邮箱, type='email_change')
   └─> 发送验证邮件到新邮箱

2. 用户点击新邮箱中的验证链接
   └─> 验证 token
       ├─> 有效:
       │   └─> 更新 User.email=新邮箱
       │   └─> 更新 User.email_verified=True
       │   └─> 更新 EmailVerificationToken.used_at
       │   └─> 发送通知邮件到旧邮箱 (EmailLog)
       └─> 无效: 显示错误
```

---

## Data Cleanup Strategy

### Automated Cleanup

1. **过期令牌清理** (每天执行):
   ```sql
   -- 删除30天前过期的密码重置令牌
   DELETE FROM password_reset_tokens 
   WHERE expires_at < NOW() - INTERVAL 30 DAY;
   
   -- 删除30天前过期的邮箱验证令牌
   DELETE FROM email_verification_tokens 
   WHERE expires_at < NOW() - INTERVAL 30 DAY;
   ```

2. **邮件日志归档** (每周执行):
   ```sql
   -- 删除90天前的成功发送日志
   DELETE FROM email_logs 
   WHERE status = 'sent' 
   AND sent_at < NOW() - INTERVAL 90 DAY;
   
   -- 保留失败日志更长时间（180天）用于分析
   DELETE FROM email_logs 
   WHERE status = 'failed' 
   AND sent_at < NOW() - INTERVAL 180 DAY;
   ```

### Manual Operations

1. **用户删除**: 级联删除相关令牌和日志
2. **安全事件**: 可手动撤销所有未使用的令牌
3. **邮箱更改回滚**: 保留旧令牌记录用于审计

---

## Database Indexes Summary

### Performance-Critical Indexes

1. **Token Lookup** (最频繁操作):
   - `password_reset_tokens.token` (UNIQUE)
   - `email_verification_tokens.token` (UNIQUE)

2. **User Operations**:
   - `password_reset_tokens.user_id`
   - `email_verification_tokens.user_id`
   - `email_logs.user_id`

3. **Cleanup Operations**:
   - `password_reset_tokens.expires_at`
   - `email_verification_tokens.expires_at`
   - `email_logs.sent_at`

4. **Monitoring & Analytics**:
   - `email_logs.status`
   - `email_logs.email_type`

---

## Next Steps

数据模型设计完成，下一步：
1. 创建 API 契约文档 (contracts/)
2. 创建快速开始指南 (quickstart.md)
3. 更新代理上下文 (copilot-instructions.md)
