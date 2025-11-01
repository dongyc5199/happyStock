"""
认证相关的 Pydantic Schema
用于请求验证和响应序列化
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名或邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="密码")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=128, description="密码")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式: 3-20字符,只能包含字母数字下划线"""
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('用户名只能包含字母、数字和下划线,长度3-20字符')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度: 至少8字符,包含字母和数字"""
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d).{8,128}$', v):
            raise ValueError('密码必须至少8个字符,包含字母和数字')
        return v


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2


class AuthSession(BaseModel):
    """认证会话"""
    user: UserResponse
    token: str
    expires_at: datetime


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool = True
    data: AuthSession


class MeResponse(BaseModel):
    """当前用户信息响应"""
    success: bool = True
    data: dict  # { "user": UserResponse }


class LogoutResponse(BaseModel):
    """登出响应"""
    success: bool = True
    message: str = "登出成功"


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: ErrorDetail
