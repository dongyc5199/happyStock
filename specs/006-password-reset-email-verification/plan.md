# Implementation Plan: 密码重置与邮箱验证

**Branch**: `006-password-reset-email-verification` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-password-reset-email-verification/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

实现用户密码重置和邮箱验证功能，包括：
1. 通过邮箱验证的密码重置流程（24小时有效期）
2. 注册后的邮箱验证功能（48小时有效期）
3. 邮箱验证提醒和重新发送机制
4. 邮箱地址更改功能
5. 安全的令牌管理和频率限制

技术方案采用：后端生成安全令牌并存储，通过SMTP发送HTML邮件，前端提供用户友好的交互界面，异步任务队列处理邮件发送，Redis实现频率限制。

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.0+ / JavaScript ES2022+ (frontend)
**Primary Dependencies**: 
- Backend: FastAPI, Tortoise-ORM, python-jose (JWT), bcrypt, aiosmtplib, jinja2, redis
- Frontend: Next.js 15.4+, React 19+, Zustand (state), Radix UI (components)

**Storage**: SQLite (development), 支持 PostgreSQL (production)
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web application (Linux/Windows server + modern browsers)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: 
- 邮件发送延迟 < 1分钟 (95%)
- 密码重置流程完成时间 < 3分钟
- 支持 1000次/小时 密码重置请求
- 令牌验证响应时间 < 100ms

**Constraints**: 
- 令牌必须加密安全（至少32字符）
- 频率限制：5分钟内最多3次请求
- 邮件发送必须异步处理，不阻塞主流程
- 所有敏感操作必须记录审计日志
- 防止邮箱枚举攻击

**Scale/Scope**: 
- 预计用户规模：10,000+ 注册用户
- 日均密码重置请求：50-100次
- 邮箱验证率目标：70%+
- 4个用户故事，32个功能需求

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (No constitution file found - using industry best practices)

Since no project-specific constitution exists, this plan follows general web application development best practices:

- ✅ **Security-first**: Secure token generation, HTTPS, frequency limiting
- ✅ **Testability**: All components independently testable, clear interfaces
- ✅ **Maintainability**: Modular design, clear separation of concerns
- ✅ **Observability**: Comprehensive logging for all email operations and security events
- ✅ **Scalability**: Async email processing, Redis-based rate limiting

**Re-evaluation after Phase 1**: Will verify design adherence to these principles

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
backend/
├── models/
│   ├── user.py                          # 扩展: email_verified, email_verified_at
│   ├── password_reset_token.py          # 新增: 密码重置令牌模型
│   ├── email_verification_token.py      # 新增: 邮箱验证令牌模型
│   └── email_log.py                     # 新增: 邮件发送日志模型
├── schemas/
│   └── email.py                         # 新增: 邮件相关请求/响应模型
├── services/
│   ├── email_service.py                 # 新增: 邮件发送服务
│   ├── token_service.py                 # 新增: 令牌生成和验证服务
│   └── rate_limit_service.py            # 新增: 频率限制服务
├── routers/
│   └── password_reset.py                # 新增: 密码重置API路由
│   └── email_verification.py            # 新增: 邮箱验证API路由
├── templates/
│   └── emails/
│       ├── password_reset.html          # 新增: 密码重置邮件模板
│       ├── email_verification.html      # 新增: 邮箱验证邮件模板
│       ├── password_reset_success.html  # 新增: 密码重置成功通知
│       └── email_change_notice.html     # 新增: 邮箱更改通知
├── tasks/
│   └── email_tasks.py                   # 新增: 异步邮件发送任务
├── tests/
│   ├── test_email_service.py            # 新增: 邮件服务测试
│   ├── test_token_service.py            # 新增: 令牌服务测试
│   ├── test_password_reset_api.py       # 新增: 密码重置API测试
│   └── test_email_verification_api.py   # 新增: 邮箱验证API测试
└── config.py                            # 更新: 添加SMTP配置

frontend/
├── src/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── forgot-password/
│   │   │   │   └── page.tsx            # 新增: 忘记密码页面
│   │   │   ├── reset-password/
│   │   │   │   └── page.tsx            # 新增: 密码重置表单页面
│   │   │   └── verify-email/
│   │   │       └── page.tsx            # 新增: 邮箱验证页面
│   │   └── settings/
│   │       └── page.tsx                 # 更新: 添加邮箱更改功能
│   ├── components/
│   │   ├── auth/
│   │   │   ├── ForgotPasswordForm.tsx  # 新增: 忘记密码表单
│   │   │   ├── ResetPasswordForm.tsx   # 新增: 重置密码表单
│   │   │   └── EmailVerificationBanner.tsx # 新增: 验证提醒横幅
│   │   └── settings/
│   │       └── ChangeEmailForm.tsx      # 新增: 更改邮箱表单
│   └── services/
│       └── emailService.ts              # 新增: 邮箱相关API调用
└── tests/
    ├── auth/
    │   ├── ForgotPasswordForm.test.tsx
    │   └── ResetPasswordForm.test.tsx
    └── settings/
        └── ChangeEmailForm.test.tsx
```

**Structure Decision**: Web application structure selected (Option 2). This feature extends the existing authentication system (Feature 005) by adding email-based password recovery and verification capabilities. Backend uses FastAPI with Tortoise-ORM for data persistence, async tasks for email sending, and Redis for rate limiting. Frontend uses Next.js App Router with React components following the existing pattern.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations - complexity is justified by security and reliability requirements.

All architectural decisions align with industry best practices:
- Async email processing: Required to avoid blocking user requests
- Redis rate limiting: Essential for preventing abuse attacks
- Token-based verification: Standard security practice for email workflows
- Separate email templates: Improves maintainability and user experience

---

## Implementation Status

### Phase 0: Research ✅ COMPLETE
- [x] Email sending strategy decided (aiosmtplib + Background tasks)
- [x] Token generation strategy decided (secrets.token_urlsafe)
- [x] Rate limiting implementation decided (Redis + sliding window)
- [x] Email templates engine decided (Jinja2)
- [x] Frontend routing designed
- [x] Security best practices documented
- [x] Error handling strategy defined
- [x] Testing strategy defined

**Output**: [research.md](./research.md)

### Phase 1: Design & Contracts ✅ COMPLETE
- [x] Data models designed (4 entities)
- [x] Entity relationships defined
- [x] Validation rules documented
- [x] State transitions mapped
- [x] API contracts defined (8 endpoints)
- [x] Request/response schemas documented
- [x] Error codes standardized
- [x] Rate limiting rules specified
- [x] Quick start guide created
- [x] Agent context updated

**Outputs**: 
- [data-model.md](./data-model.md)
- [contracts/api-endpoints.md](./contracts/api-endpoints.md)
- [quickstart.md](./quickstart.md)

### Phase 2: Tasks (PENDING)
Run `/speckit.tasks` command to generate implementation tasks.

---

## Next Steps

✅ **Phase 0 & 1 Complete** - Ready for task breakdown

Run the following command to generate implementation tasks:
```
/speckit.tasks
```

This will create `tasks.md` with detailed implementation subtasks organized by priority.
