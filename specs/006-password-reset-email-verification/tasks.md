# Tasks: 密码重置与邮箱验证

**Feature**: 006-password-reset-email-verification
**Generated**: 2025-11-01
**Input**: Design documents from specs/006-password-reset-email-verification/

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4)
- All paths use forward slashes (/)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and install dependencies

- [ ] T001 Install backend dependencies: aiosmtplib, jinja2, redis in backend/Pipfile
- [ ] T002 Install frontend dependencies: react-hook-form, zod, @hookform/resolvers in frontend/package.json
- [ ] T003 Create backend/templates/emails/ directory structure
- [ ] T004 Create environment variable templates in backend/.env.example (SMTP, Redis config)
- [ ] T005 Setup Redis service (Docker or local installation)
- [ ] T006 Create backend/services/ directory if not exists
- [ ] T007 Create backend/tasks/ directory for background tasks
- [ ] T008 Create backend/tests/ directory structure (unit, integration)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create PasswordResetToken model in backend/models/password_reset_token.py
- [ ] T010 Create EmailVerificationToken model in backend/models/email_verification_token.py
- [ ] T011 Extend User model: add email_verified, email_verified_at fields in backend/models/user.py
- [ ] T012 Create EmailLog model in backend/models/email_log.py
- [ ] T013 Create Pydantic schemas for email requests/responses in backend/schemas/email.py
- [ ] T014 Generate and run database migration for all new models
- [ ] T015 [P] Implement TokenService (generate, validate, cleanup) in backend/services/token_service.py
- [ ] T016 [P] Implement EmailService (SMTP, template rendering) in backend/services/email_service.py
- [ ] T017 [P] Implement RateLimitService (Redis sliding window) in backend/services/rate_limit_service.py
- [ ] T018 Create base email template in backend/templates/emails/base.html
- [ ] T019 [P] Setup SMTP configuration in backend/config.py
- [ ] T020 [P] Create email task queue in backend/tasks/email_tasks.py
- [ ] T021 Create API error codes enum in backend/exceptions.py
- [ ] T022 Create frontend email service API wrapper in frontend/src/services/emailService.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 忘记密码重置流程 (Priority: P1) 🎯 MVP

**Goal**: 用户可以通过邮箱验证重置密码，从请求到登录成功在3分钟内完成

**Independent Test**: 用户点击"忘记密码"链接，输入邮箱，收到邮件，点击链接，设置新密码，成功登录

### Backend Implementation for User Story 1

- [ ] T023 [P] [US1] Create password_reset.html email template in backend/templates/emails/password_reset.html
- [ ] T024 [P] [US1] Create password_reset_success.html email template in backend/templates/emails/password_reset_success.html
- [ ] T025 [US1] Implement POST /api/auth/forgot-password endpoint in backend/routers/password_reset.py
- [ ] T026 [US1] Implement GET /api/auth/reset-password/verify endpoint in backend/routers/password_reset.py
- [ ] T027 [US1] Implement POST /api/auth/reset-password endpoint in backend/routers/password_reset.py
- [ ] T028 [US1] Add password validation rules (min 8 chars, letters + numbers) in backend/schemas/email.py
- [ ] T029 [US1] Implement rate limiting for forgot-password endpoint (3 requests per 5 min)
- [ ] T030 [US1] Add email enumeration prevention logic in forgot-password handler
- [ ] T031 [US1] Implement token cleanup on successful password reset
- [ ] T032 [US1] Add audit logging for all password reset operations in email_logs table

### Frontend Implementation for User Story 1

- [ ] T033 [P] [US1] Create /auth/forgot-password page in frontend/src/app/auth/forgot-password/page.tsx
- [ ] T034 [P] [US1] Create /auth/reset-password page in frontend/src/app/auth/reset-password/page.tsx
- [ ] T035 [US1] Create ForgotPasswordForm component with React Hook Form in frontend/src/components/auth/ForgotPasswordForm.tsx
- [ ] T036 [US1] Create ResetPasswordForm component with validation in frontend/src/components/auth/ResetPasswordForm.tsx
- [ ] T037 [US1] Create Zod schema for password validation in frontend/src/components/auth/ResetPasswordForm.tsx
- [ ] T038 [US1] Add "Forgot Password?" link to login page in frontend/src/app/auth/login/page.tsx
- [ ] T039 [US1] Implement forgotPassword API call in frontend/src/services/emailService.ts
- [ ] T040 [US1] Implement verifyResetToken API call in frontend/src/services/emailService.ts
- [ ] T041 [US1] Implement resetPassword API call in frontend/src/services/emailService.ts
- [ ] T042 [US1] Add error handling and user feedback messages for all forms
- [ ] T043 [US1] Add loading states and disable submit buttons during API calls
- [ ] T044 [US1] Add success redirect to login page after password reset

### Testing for User Story 1

- [ ] T045 [P] [US1] Write unit tests for TokenService in backend/tests/test_token_service.py
- [ ] T046 [P] [US1] Write unit tests for EmailService in backend/tests/test_email_service.py
- [ ] T047 [P] [US1] Write unit tests for RateLimitService in backend/tests/test_rate_limit_service.py
- [ ] T048 [US1] Write integration test for forgot-password endpoint in backend/tests/test_password_reset_api.py
- [ ] T049 [US1] Write integration test for reset-password flow in backend/tests/test_password_reset_api.py
- [ ] T050 [US1] Write integration test for token expiry in backend/tests/test_password_reset_api.py
- [ ] T051 [US1] Write integration test for rate limiting in backend/tests/test_password_reset_api.py
- [ ] T052 [P] [US1] Write component test for ForgotPasswordForm in frontend/tests/auth/ForgotPasswordForm.test.tsx
- [ ] T053 [P] [US1] Write component test for ResetPasswordForm in frontend/tests/auth/ResetPasswordForm.test.tsx

**Checkpoint**: User Story 1 (密码重置) should be fully functional and testable independently

---

## Phase 4: User Story 2 - 注册时邮箱验证 (Priority: P2)

**Goal**: 新用户注册后自动收到验证邮件，验证后账户标记为已验证

**Independent Test**: 用户注册后收到验证邮件，点击链接，验证成功，账户状态更新

### Backend Implementation for User Story 2

- [ ] T054 [P] [US2] Create email_verification.html template in backend/templates/emails/email_verification.html
- [ ] T055 [US2] Implement POST /api/auth/verify-email endpoint in backend/routers/email_verification.py
- [ ] T056 [US2] Implement GET /api/auth/email-status endpoint in backend/routers/email_verification.py
- [ ] T057 [US2] Extend registration endpoint to send verification email in backend/routers/auth.py
- [ ] T058 [US2] Implement token validation logic for email verification (48-hour expiry)
- [ ] T059 [US2] Update User.email_verified and User.email_verified_at on successful verification
- [ ] T060 [US2] Mark EmailVerificationToken as used on successful verification
- [ ] T061 [US2] Add audit logging for email verification events

### Frontend Implementation for User Story 2

- [ ] T062 [P] [US2] Create /auth/verify-email page in frontend/src/app/auth/verify-email/page.tsx
- [ ] T063 [P] [US2] Create EmailVerificationBanner component in frontend/src/components/auth/EmailVerificationBanner.tsx
- [ ] T064 [US2] Implement verifyEmail API call in frontend/src/services/emailService.ts
- [ ] T065 [US2] Implement getEmailStatus API call in frontend/src/services/emailService.ts
- [ ] T066 [US2] Add EmailVerificationBanner to main layout for unverified users in frontend/src/app/layout.tsx
- [ ] T067 [US2] Update registration success page to show verification prompt
- [ ] T068 [US2] Add error handling for expired/invalid tokens with resend option
- [ ] T069 [US2] Add success message and redirect after verification

### Testing for User Story 2

- [ ] T070 [P] [US2] Write unit tests for email verification token generation
- [ ] T071 [US2] Write integration test for verify-email endpoint in backend/tests/test_email_verification_api.py
- [ ] T072 [US2] Write integration test for registration flow with email sending
- [ ] T073 [US2] Write integration test for token expiry (48 hours)
- [ ] T074 [P] [US2] Write component test for EmailVerificationBanner in frontend/tests/auth/EmailVerificationBanner.test.tsx

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - 重新发送验证邮件 (Priority: P3)

**Goal**: 用户可以请求重新发送验证邮件，处理邮件未送达或过期的情况

**Independent Test**: 未验证用户点击"重新发送验证邮件"按钮，收到新邮件，点击验证成功

### Backend Implementation for User Story 3

- [ ] T075 [US3] Implement POST /api/auth/resend-verification endpoint in backend/routers/email_verification.py
- [ ] T076 [US3] Add rate limiting for resend-verification endpoint (3 requests per 5 min)
- [ ] T077 [US3] Implement logic to invalidate old tokens when sending new ones
- [ ] T078 [US3] Add check to prevent resending if email already verified
- [ ] T079 [US3] Add audit logging for resend operations

### Frontend Implementation for User Story 3

- [ ] T080 [US3] Add "Resend Verification Email" button to EmailVerificationBanner
- [ ] T081 [US3] Implement resendVerification API call in frontend/src/services/emailService.ts
- [ ] T082 [US3] Add cooldown timer display (5 minutes) after resend
- [ ] T083 [US3] Add success/error messages for resend operation
- [ ] T084 [US3] Disable resend button during cooldown period

### Testing for User Story 3

- [ ] T085 [US3] Write integration test for resend-verification endpoint
- [ ] T086 [US3] Write integration test for rate limiting on resend
- [ ] T087 [US3] Write integration test for old token invalidation
- [ ] T088 [US3] Write component test for resend button functionality

**Checkpoint**: All three user stories should work independently

---

## Phase 6: User Story 4 - 更改邮箱地址 (Priority: P4)

**Goal**: 已登录用户可以更改账户邮箱地址，通过验证新邮箱

**Independent Test**: 用户在设置页面输入新邮箱和密码，收到验证邮件，验证后邮箱更新

### Backend Implementation for User Story 4

- [ ] T089 [P] [US4] Create email_change_notice.html template in backend/templates/emails/email_change_notice.html
- [ ] T090 [US4] Implement POST /api/auth/change-email endpoint in backend/routers/email_verification.py
- [ ] T091 [US4] Implement POST /api/auth/confirm-email-change endpoint in backend/routers/email_verification.py
- [ ] T092 [US4] Add password verification in change-email endpoint
- [ ] T093 [US4] Add check to prevent duplicate email (already in use by another user)
- [ ] T094 [US4] Create EmailVerificationToken with type='email_change'
- [ ] T095 [US4] Send verification email to new email address
- [ ] T096 [US4] Update User.email on successful confirmation
- [ ] T097 [US4] Send security notice email to old email address
- [ ] T098 [US4] Reset User.email_verified status on email change
- [ ] T099 [US4] Add rate limiting for change-email endpoint (3 requests per 5 min)
- [ ] T100 [US4] Add audit logging for email change operations

### Frontend Implementation for User Story 4

- [ ] T101 [P] [US4] Create ChangeEmailForm component in frontend/src/components/settings/ChangeEmailForm.tsx
- [ ] T102 [US4] Add ChangeEmailForm to settings page in frontend/src/app/settings/page.tsx
- [ ] T103 [US4] Create Zod schema for email change validation (email + password)
- [ ] T104 [US4] Implement changeEmail API call in frontend/src/services/emailService.ts
- [ ] T105 [US4] Implement confirmEmailChange API call in frontend/src/services/emailService.ts
- [ ] T106 [US4] Add error handling for duplicate email
- [ ] T107 [US4] Add error handling for incorrect password
- [ ] T108 [US4] Add success message showing verification email sent
- [ ] T109 [US4] Display current email and pending email status

### Testing for User Story 4

- [ ] T110 [US4] Write integration test for change-email endpoint
- [ ] T111 [US4] Write integration test for confirm-email-change endpoint
- [ ] T112 [US4] Write integration test for duplicate email prevention
- [ ] T113 [US4] Write integration test for password verification
- [ ] T114 [US4] Write integration test for old email notification
- [ ] T115 [P] [US4] Write component test for ChangeEmailForm

**Checkpoint**: All four user stories should work independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [ ] T116 [P] Create API documentation in backend using Swagger/OpenAPI annotations
- [ ] T117 [P] Add responsive design improvements for mobile devices
- [ ] T118 Create automated token cleanup job in backend/tasks/cleanup_tokens.py
- [ ] T119 Setup cron job or scheduler for daily token cleanup
- [ ] T120 Add performance monitoring for email sending latency
- [ ] T121 Add error tracking and alerting for email failures
- [ ] T122 Create deployment guide for SMTP configuration in docs/
- [ ] T123 Create troubleshooting guide for common issues in docs/
- [ ] T124 Update main README.md with new feature documentation
- [ ] T125 Add security headers (CORS, CSP) to API endpoints
- [ ] T126 Implement email template preview tool for development
- [ ] T127 Add end-to-end tests for complete user flows
- [ ] T128 Optimize database queries with proper indexes
- [ ] T129 Configure log aggregation for production
- [ ] T130 Run quickstart.md validation to ensure all steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-6 (User Stories)**: All depend on Phase 2 completion
  - Can proceed in parallel if multiple developers
  - Or sequentially by priority: P1 → P2 → P3 → P4
- **Phase 7 (Polish)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1 - Password Reset)**: Can start after Phase 2 - **MVP candidate**
- **US2 (P2 - Email Verification)**: Can start after Phase 2 - Independent from US1
- **US3 (P3 - Resend)**: Depends on US2 (extends email verification)
- **US4 (P4 - Email Change)**: Can start after Phase 2 - Independent from US1-US3

### Within Each User Story

1. Backend models and services (from Phase 2) must exist
2. Email templates before API endpoints
3. API endpoints before frontend integration
4. Core implementation before error handling
5. Tests throughout (TDD approach recommended)

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run in parallel

**Phase 2 (Foundational)**: 
- T009-T014: All models can be created in parallel
- T015-T022: All services can be created in parallel after models

**Phase 3 (US1)**:
- T023, T024: Email templates in parallel
- T033, T034: Frontend pages in parallel
- T035, T036: Frontend components in parallel
- T045-T047, T052-T053: All tests in parallel

**Phase 4 (US2)**:
- T054: Template standalone
- T062, T063: Frontend components in parallel
- T070, T074: Tests in parallel

**Multiple User Stories**:
- Once Phase 2 completes, US1, US2, and US4 can all start in parallel (different developers)
- US3 must wait for US2 to complete

---

## Parallel Example: Phase 2 (Foundational)

```bash
# All models in parallel:
Task T009: "Create PasswordResetToken model"
Task T010: "Create EmailVerificationToken model"
Task T011: "Extend User model"
Task T012: "Create EmailLog model"

# All services in parallel (after models):
Task T015: "Implement TokenService"
Task T016: "Implement EmailService"
Task T017: "Implement RateLimitService"
Task T019: "Setup SMTP configuration"
Task T020: "Create email task queue"
```

## Parallel Example: User Story 1

```bash
# Email templates in parallel:
Task T023: "Create password_reset.html template"
Task T024: "Create password_reset_success.html template"

# Frontend pages in parallel:
Task T033: "Create /auth/forgot-password page"
Task T034: "Create /auth/reset-password page"

# All tests in parallel (after implementation):
Task T045: "Unit tests for TokenService"
Task T046: "Unit tests for EmailService"
Task T047: "Unit tests for RateLimitService"
Task T052: "Component test for ForgotPasswordForm"
Task T053: "Component test for ResetPasswordForm"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended

1. **Week 1**: Complete Phase 1 (Setup) + Phase 2 (Foundational)
2. **Week 2**: Complete Phase 3 (US1 - Password Reset)
3. **Week 2 End**: VALIDATE independently - Deploy MVP
4. **Decision Point**: Proceed to US2 or iterate on US1 based on feedback

**Timeline**: ~2 weeks for working password reset feature

### Incremental Delivery

1. **Foundation** (Phase 1-2): ~3-5 days → Infrastructure ready
2. **+ US1** (Phase 3): ~3-5 days → MVP: Password reset works ✅
3. **+ US2** (Phase 4): ~2-3 days → Email verification on registration ✅
4. **+ US3** (Phase 5): ~1-2 days → Resend mechanism ✅
5. **+ US4** (Phase 6): ~2-3 days → Email change feature ✅
6. **Polish** (Phase 7): ~2-3 days → Production-ready

**Total Timeline**: 13-21 days (single developer, full-time)

### Parallel Team Strategy (3 developers)

1. **Week 1**: All developers complete Phase 1-2 together
2. **Week 2-3**: 
   - Developer A: US1 (Password Reset) - MVP priority
   - Developer B: US2 (Email Verification)
   - Developer C: US4 (Email Change)
3. **Week 3-4**: 
   - Developer B: US3 (Resend) - extends US2
   - All: Code review and integration
4. **Week 4**: Phase 7 (Polish) together

**Total Timeline**: ~3-4 weeks with 3 developers

---

## Task Summary

### Total Tasks by Phase

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 14 tasks (🔴 Blocking)
- **Phase 3 (US1 - P1)**: 31 tasks ⭐ MVP
- **Phase 4 (US2 - P2)**: 21 tasks
- **Phase 5 (US3 - P3)**: 14 tasks
- **Phase 6 (US4 - P4)**: 27 tasks
- **Phase 7 (Polish)**: 15 tasks

**Total**: 130 tasks

### Tasks by Type

- **Backend**: ~55 tasks (models, services, API endpoints)
- **Frontend**: ~45 tasks (pages, components, API integration)
- **Testing**: ~25 tasks (unit, integration, component)
- **DevOps**: ~5 tasks (deployment, monitoring, documentation)

### Parallel Opportunities

- **Phase 1**: 8 tasks can run in parallel
- **Phase 2**: 10 tasks can run in parallel (after models)
- **User Stories**: US1, US2, US4 can run in parallel (US3 depends on US2)
- **Within Stories**: ~60% of tasks within each story can be parallelized

### MVP Scope (Recommended First Delivery)

**Include**:
- Phase 1: Setup (8 tasks)
- Phase 2: Foundational (14 tasks)
- Phase 3: US1 - Password Reset (31 tasks)

**Total MVP**: 53 tasks (~10-12 days single developer)

**Delivers**: Complete password reset functionality with email verification

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] **SC-001**: Password reset completes in <3 minutes (user testing)
- [ ] **SC-002**: Email verification completes in <2 minutes
- [ ] **SC-003**: 95% emails delivered within 1 minute (monitoring)
- [ ] **SC-004**: System handles 1000 requests/hour (load testing)
- [ ] **SC-005**: 90% first-attempt success rate (analytics)
- [ ] **SC-006**: Support tickets reduced by 80% (tracking)
- [ ] **SC-007**: 70% email verification rate (analytics)
- [ ] **SC-008**: Complete audit logging (verify email_logs table)

### Independent User Story Tests

- [ ] **US1 Test**: User can reset password without any other features working
- [ ] **US2 Test**: User can verify email after registration independently
- [ ] **US3 Test**: User can resend verification email independently
- [ ] **US4 Test**: User can change email address independently

### Security Validation

- [ ] Rate limiting works (try 4 requests in 5 minutes)
- [ ] Email enumeration prevented (same response for existing/non-existing emails)
- [ ] Tokens expire correctly (test with 25-hour-old password reset token)
- [ ] Tokens are one-time use (try using same token twice)
- [ ] HTTPS enforced in production
- [ ] Audit logs capture all operations

### Performance Validation

- [ ] Email sending doesn't block HTTP responses (<200ms response time)
- [ ] Token validation queries are fast (<100ms with indexes)
- [ ] Cleanup job runs successfully without blocking operations
- [ ] Redis rate limiting performs well under load

---

## Notes

- **[P] marker**: Tasks with [P] can run in parallel with other [P] tasks in the same phase
- **[Story] label**: Maps task to specific user story for traceability
- **File paths**: All paths use forward slashes, adjust for Windows if needed
- **Tests**: Write tests first (TDD), ensure they fail before implementation
- **Commits**: Commit after each task or logical group of related tasks
- **Checkpoints**: Stop at checkpoints to validate story works independently
- **MVP**: Phase 3 (US1) is complete MVP - can stop and deploy after this phase

**Last Updated**: 2025-11-01
