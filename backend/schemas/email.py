"""
邮件相关请求和响应模型
使用 Pydantic 进行数据验证
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


# ==================== 密码重置相关 ====================

class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr = Field(..., description="注册邮箱地址")


class VerifyResetTokenResponse(BaseModel):
    """验证重置令牌响应"""
    valid: bool = Field(..., description="令牌是否有效")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str = Field(..., min_length=43, max_length=43, description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., min_length=8, description="确认密码")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码必须至少8个字符')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """验证两次密码输入一致"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


# ==================== 邮箱验证相关 ====================

class VerifyEmailRequest(BaseModel):
    """验证邮箱请求"""
    token: str = Field(..., min_length=43, max_length=43, description="验证令牌")


class VerifyEmailResponse(BaseModel):
    """验证邮箱响应"""
    message: str = Field(..., description="响应消息")
    email: str = Field(..., description="已验证的邮箱")
    verified_at: datetime = Field(..., description="验证时间")


class EmailStatusResponse(BaseModel):
    """邮箱状态响应"""
    email: str = Field(..., description="当前邮箱地址")
    email_verified: bool = Field(..., description="是否已验证")
    email_verified_at: Optional[datetime] = Field(None, description="验证时间")
    can_resend: bool = Field(..., description="是否可以重新发送验证邮件")


# ==================== 更改邮箱相关 ====================

class ChangeEmailRequest(BaseModel):
    """更改邮箱请求"""
    new_email: EmailStr = Field(..., description="新邮箱地址")
    password: str = Field(..., min_length=8, description="当前密码（验证身份）")


class ConfirmEmailChangeRequest(BaseModel):
    """确认邮箱更改请求"""
    token: str = Field(..., min_length=43, max_length=43, description="验证令牌")


class ConfirmEmailChangeResponse(BaseModel):
    """确认邮箱更改响应"""
    message: str = Field(..., description="响应消息")
    new_email: str = Field(..., description="新邮箱地址")


# ==================== 通用响应模型 ====================

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="额外数据")


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(default=False, description="操作是否成功")
    error: dict = Field(..., description="错误信息")

    class ErrorDetail(BaseModel):
        """错误详情"""
        code: str = Field(..., description="错误代码")
        message: str = Field(..., description="错误消息")
        details: Optional[dict] = Field(None, description="额外详情")
