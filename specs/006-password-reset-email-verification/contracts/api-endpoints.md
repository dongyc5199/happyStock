# API Contracts: 密码重置与邮箱验证

**Version**: 1.0.0
**Date**: 2025-11-01
**Base URL**: `/api/auth`

## Overview

本文档定义密码重置和邮箱验证功能的所有API端点。所有端点遵循RESTful设计原则。

### Common Response Format

**Success Response**:
```json
{
  "success": true,
  "data": { /* specific response data */ },
  "message": "操作成功" 
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "用户友好的错误消息",
    "details": {} // Optional, for debugging
  }
}
```

### Common HTTP Status Codes

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权（需要登录）
- `403 Forbidden`: 禁止访问（权限不足）
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

---

## Endpoints

### 1. 请求密码重置

**Endpoint**: `POST /api/auth/forgot-password`

**Description**: 用户请求重置密码，系统发送重置链接到注册邮箱

**Authentication**: None (公开接口)

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Request Schema**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| email | string | Yes | 有效的邮箱格式，最大255字符 |

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "如果该邮箱已注册，您将收到密码重置邮件"
  }
}
```

**Error Responses**:

- **400 Bad Request** (邮箱格式无效):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_EMAIL",
    "message": "请输入有效的邮箱地址"
  }
}
```

- **429 Too Many Requests** (频率超限):
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁，请180秒后重试",
    "details": {
      "retry_after": 180
    }
  }
}
```

**Notes**:
- 为防止邮箱枚举，无论邮箱是否存在，都返回相同的成功消息
- 实际只对存在的邮箱发送邮件
- 频率限制：同一邮箱5分钟内最多3次

---

### 2. 验证重置令牌

**Endpoint**: `GET /api/auth/reset-password/verify?token={token}`

**Description**: 验证密码重置令牌的有效性（在显示重置表单前调用）

**Authentication**: None

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| token | string | Yes | 43字符的重置令牌 |

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "valid": true,
    "expires_at": "2025-11-02T15:30:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** (令牌格式无效):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "无效的重置链接"
  }
}
```

- **404 Not Found** (令牌不存在):
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_NOT_FOUND",
    "message": "重置链接不存在或已失效"
  }
}
```

- **410 Gone** (令牌已过期):
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "重置链接已过期，请重新申请",
    "details": {
      "can_resend": true
    }
  }
}
```

- **410 Gone** (令牌已使用):
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_USED",
    "message": "重置链接已使用，请重新申请",
    "details": {
      "can_resend": true
    }
  }
}
```

---

### 3. 重置密码

**Endpoint**: `POST /api/auth/reset-password`

**Description**: 使用有效令牌重置用户密码

**Authentication**: None

**Request Body**:
```json
{
  "token": "abc123...",
  "new_password": "NewSecurePass123",
  "confirm_password": "NewSecurePass123"
}
```

**Request Schema**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| token | string | Yes | 43字符URL安全字符串 |
| new_password | string | Yes | 最少8字符，包含字母和数字 |
| confirm_password | string | Yes | 必须与new_password一致 |

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "密码重置成功，请使用新密码登录"
  }
}
```

**Error Responses**:

- **400 Bad Request** (密码不符合要求):
```json
{
  "success": false,
  "error": {
    "code": "WEAK_PASSWORD",
    "message": "密码必须至少8个字符，包含字母和数字"
  }
}
```

- **400 Bad Request** (密码不一致):
```json
{
  "success": false,
  "error": {
    "code": "PASSWORD_MISMATCH",
    "message": "两次输入的密码不一致"
  }
}
```

- **410 Gone** (令牌无效):
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "重置链接已过期或已使用"
  }
}
```

**Side Effects**:
- 更新用户密码哈希
- 标记令牌为已使用
- 使该用户的其他重置令牌失效
- 发送密码重置成功确认邮件
- 可选：使现有登录会话失效

---

### 4. 重新发送验证邮件

**Endpoint**: `POST /api/auth/resend-verification`

**Description**: 重新发送邮箱验证邮件（需要登录）

**Authentication**: Required (Bearer Token)

**Request Body**: None (从JWT获取用户信息)

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "验证邮件已发送，请检查您的邮箱"
  }
}
```

**Error Responses**:

- **400 Bad Request** (邮箱已验证):
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_ALREADY_VERIFIED",
    "message": "您的邮箱已经验证过了"
  }
}
```

- **429 Too Many Requests**:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁，请120秒后重试",
    "details": {
      "retry_after": 120
    }
  }
}
```

**Notes**:
- 频率限制：同一用户5分钟内最多3次
- 发送新令牌时，旧令牌自动失效

---

### 5. 验证邮箱

**Endpoint**: `POST /api/auth/verify-email`

**Description**: 使用令牌验证用户邮箱

**Authentication**: None

**Request Body**:
```json
{
  "token": "xyz789..."
}
```

**Request Schema**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| token | string | Yes | 43字符URL安全字符串 |

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "邮箱验证成功",
    "email": "user@example.com",
    "verified_at": "2025-11-01T12:00:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** (令牌无效):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "验证链接无效"
  }
}
```

- **410 Gone** (令牌过期):
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "验证链接已过期",
    "details": {
      "can_resend": true,
      "user_id": 123
    }
  }
}
```

- **410 Gone** (令牌已使用):
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_USED",
    "message": "该链接已被使用"
  }
}
```

**Side Effects**:
- 更新 User.email_verified = True
- 更新 User.email_verified_at
- 标记令牌为已使用

---

### 6. 请求更改邮箱

**Endpoint**: `POST /api/auth/change-email`

**Description**: 请求更改账户邮箱地址（需要登录）

**Authentication**: Required (Bearer Token)

**Request Body**:
```json
{
  "new_email": "newemail@example.com",
  "password": "CurrentPassword123"
}
```

**Request Schema**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| new_email | string | Yes | 有效的邮箱格式，最大255字符 |
| password | string | Yes | 用户当前密码（验证身份） |

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "验证邮件已发送到新邮箱，请查收并完成验证"
  }
}
```

**Error Responses**:

- **400 Bad Request** (新邮箱与当前相同):
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_UNCHANGED",
    "message": "新邮箱与当前邮箱相同"
  }
}
```

- **401 Unauthorized** (密码错误):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PASSWORD",
    "message": "当前密码错误"
  }
}
```

- **409 Conflict** (邮箱已被使用):
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_IN_USE",
    "message": "该邮箱已被其他账户使用"
  }
}
```

**Side Effects**:
- 创建新的邮箱验证令牌（type='email_change'）
- 发送验证邮件到新邮箱
- 旧邮箱保持有效，直到新邮箱验证成功

---

### 7. 确认邮箱更改

**Endpoint**: `POST /api/auth/confirm-email-change`

**Description**: 使用令牌确认邮箱更改

**Authentication**: None

**Request Body**:
```json
{
  "token": "pqr456..."
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "邮箱更改成功",
    "new_email": "newemail@example.com"
  }
}
```

**Error Responses**:
同 "验证邮箱" 端点

**Side Effects**:
- 更新 User.email 为新邮箱
- 重置 User.email_verified = True
- 更新 User.email_verified_at
- 标记令牌为已使用
- 发送安全通知邮件到旧邮箱

---

### 8. 获取邮箱验证状态

**Endpoint**: `GET /api/auth/email-status`

**Description**: 获取当前用户的邮箱验证状态（需要登录）

**Authentication**: Required (Bearer Token)

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "email": "user@example.com",
    "email_verified": true,
    "email_verified_at": "2025-11-01T10:00:00Z",
    "can_resend": false
  }
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| email | string | 当前邮箱地址 |
| email_verified | boolean | 是否已验证 |
| email_verified_at | string | 验证时间（ISO 8601），未验证则为null |
| can_resend | boolean | 是否可以重新发送验证邮件（基于频率限制） |

---

## Rate Limiting

### Global Rules

所有端点都受全局速率限制保护：
- 每个IP地址：100请求/分钟
- 超限返回 429 状态码

### Endpoint-Specific Limits

| Endpoint | Limit | Window | Identifier |
|----------|-------|--------|------------|
| POST /forgot-password | 3次 | 5分钟 | email |
| POST /resend-verification | 3次 | 5分钟 | user_id |
| POST /reset-password | 5次 | 10分钟 | IP address |
| POST /verify-email | 10次 | 10分钟 | IP address |
| POST /change-email | 3次 | 5分钟 | user_id |

### Rate Limit Response Headers

```
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 1
X-RateLimit-Reset: 1730467200
```

---

## Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_EMAIL | 400 | 邮箱格式无效 |
| INVALID_TOKEN | 400 | 令牌格式无效或不存在 |
| TOKEN_EXPIRED | 410 | 令牌已过期 |
| TOKEN_USED | 410 | 令牌已被使用 |
| TOKEN_NOT_FOUND | 404 | 令牌不存在 |
| WEAK_PASSWORD | 400 | 密码不符合强度要求 |
| PASSWORD_MISMATCH | 400 | 两次密码输入不一致 |
| EMAIL_ALREADY_VERIFIED | 400 | 邮箱已验证 |
| EMAIL_UNCHANGED | 400 | 新邮箱与当前相同 |
| EMAIL_IN_USE | 409 | 邮箱已被占用 |
| INVALID_PASSWORD | 401 | 密码错误 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| UNAUTHORIZED | 401 | 未授权（需要登录） |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

---

## Security Considerations

1. **HTTPS Only**: 所有端点必须通过HTTPS访问
2. **CORS**: 配置严格的CORS策略
3. **CSRF Protection**: 使用SameSite cookies或CSRF tokens
4. **Input Validation**: 严格验证所有输入参数
5. **Rate Limiting**: 多层速率限制防止滥用
6. **Audit Logging**: 记录所有敏感操作到 email_logs

---

## Testing Checklist

- [ ] 所有端点返回正确的HTTP状态码
- [ ] 错误响应包含用户友好的消息
- [ ] 频率限制正确工作
- [ ] 令牌验证逻辑严格（过期、已使用、不存在）
- [ ] 邮箱枚举防护有效
- [ ] 审计日志正确记录
- [ ] CORS和安全头正确配置

---

## Changelog

### Version 1.0.0 (2025-11-01)
- 初始API设计
- 定义8个核心端点
- 定义统一错误响应格式
- 定义频率限制规则
