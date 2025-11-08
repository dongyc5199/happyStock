"""
密码重置 API 路由
处理忘记密码、验证令牌、重置密码等功能
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from tortoise.exceptions import DoesNotExist
import bcrypt
from datetime import datetime

from schemas.email import (
    ForgotPasswordRequest,
    VerifyResetTokenResponse,
    ResetPasswordRequest,
    SuccessResponse
)
from models.user import User
from services.token_service import TokenService
from services.rate_limit_service import rate_limit_service
from tasks.email_tasks import (
    add_send_password_reset_email,
    add_send_password_reset_success_email
)
from exceptions import (
    InvalidEmailError,
    TokenExpiredError,
    TokenUsedError,
    TokenNotFoundError,
    PasswordMismatchError,
    RateLimitExceededError
)

router = APIRouter(prefix="/api/auth", tags=["密码重置"])


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    req: Request
) -> SuccessResponse:
    """
    请求密码重置
    
    发送密码重置邮件到用户注册邮箱
    
    Args:
        request: 包含邮箱地址的请求
        background_tasks: FastAPI 后台任务
        req: HTTP 请求对象（用于获取IP）
        
    Returns:
        SuccessResponse: 统一的成功响应
        
    注意：为防止邮箱枚举，无论邮箱是否存在都返回相同消息
    """
    email = request.email
    
    # 检查频率限制（5分钟内最多3次）
    allowed, retry_after = await rate_limit_service.check_rate_limit(
        operation="password_reset",
        identifier=email,
        window_seconds=300,
        max_attempts=3
    )
    
    if not allowed:
        raise RateLimitExceededError(
            message=f"请求过于频繁，请{retry_after}秒后重试",
            retry_after=retry_after
        )
    
    try:
        # 查找用户
        user = await User.get(email=email)
        
        # 获取客户端IP
        client_ip = req.client.host if req.client else None
        
        # 创建密码重置令牌
        reset_token = await TokenService.create_password_reset_token(
            user=user,
            ip_address=client_ip
        )
        
        # 后台发送邮件
        add_send_password_reset_email(
            background_tasks,
            user,
            reset_token.token
        )
        
    except DoesNotExist:
        # 用户不存在，但为了安全返回相同消息
        pass
    
    # 统一返回消息（防止邮箱枚举）
    return SuccessResponse(
        success=True,
        message="如果该邮箱已注册，您将收到密码重置邮件"
    )


@router.get("/reset-password/verify", response_model=VerifyResetTokenResponse)
async def verify_reset_token(token: str) -> VerifyResetTokenResponse:
    """
    验证密码重置令牌
    
    在显示重置表单前验证令牌是否有效
    
    Args:
        token: 重置令牌字符串
        
    Returns:
        VerifyResetTokenResponse: 令牌验证结果
        
    Raises:
        HTTPException: 令牌无效、过期或已使用
    """
    valid, error_code, reset_token = await TokenService.verify_password_reset_token(token)
    
    if not valid:
        if error_code == "TOKEN_NOT_FOUND":
            raise HTTPException(status_code=404, detail={
                "code": "TOKEN_NOT_FOUND",
                "message": "重置链接不存在或已失效"
            })
        elif error_code == "TOKEN_EXPIRED":
            raise HTTPException(status_code=410, detail={
                "code": "TOKEN_EXPIRED",
                "message": "重置链接已过期，请重新申请",
                "can_resend": True
            })
        elif error_code == "TOKEN_USED":
            raise HTTPException(status_code=410, detail={
                "code": "TOKEN_USED",
                "message": "重置链接已使用，请重新申请",
                "can_resend": True
            })
    
    return VerifyResetTokenResponse(
        valid=True,
        expires_at=reset_token.expires_at
    )


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(
    request: ResetPasswordRequest,
    background_tasks: BackgroundTasks
) -> SuccessResponse:
    """
    重置密码
    
    使用有效令牌重置用户密码
    
    Args:
        request: 包含令牌和新密码的请求
        background_tasks: FastAPI 后台任务
        
    Returns:
        SuccessResponse: 成功响应
        
    Raises:
        HTTPException: 令牌无效或密码验证失败
    """
    # 验证令牌
    valid, error_code, reset_token = await TokenService.verify_password_reset_token(
        request.token
    )
    
    if not valid:
        if error_code == "TOKEN_NOT_FOUND":
            raise HTTPException(status_code=404, detail={
                "code": "TOKEN_NOT_FOUND",
                "message": "重置链接不存在或已失效"
            })
        elif error_code == "TOKEN_EXPIRED":
            raise HTTPException(status_code=410, detail={
                "code": "TOKEN_EXPIRED",
                "message": "重置链接已过期或已使用"
            })
        elif error_code == "TOKEN_USED":
            raise HTTPException(status_code=410, detail={
                "code": "TOKEN_USED",
                "message": "重置链接已使用"
            })
    
    # 获取用户
    user = reset_token.user
    
    # 更新密码（使用 bcrypt 加密）
    password_bytes = request.new_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    user.password_hash = hashed.decode('utf-8')
    await user.save()
    
    # 标记令牌为已使用
    await TokenService.mark_password_reset_token_used(reset_token)
    
    # 使该用户的其他重置令牌失效
    await TokenService.invalidate_user_password_reset_tokens(user)
    
    # 后台发送密码重置成功邮件
    add_send_password_reset_success_email(background_tasks, user)
    
    return SuccessResponse(
        success=True,
        message="密码重置成功，请使用新密码登录"
    )
