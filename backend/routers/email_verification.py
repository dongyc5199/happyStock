"""
邮箱验证路由
处理邮箱验证相关的所有端点
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timezone

from models.user import User
from models.email_verification_token import EmailVerificationToken
from models.email_log import EmailLog
from services.token_service import TokenService
from services.email_service import EmailService
from services.rate_limit_service import rate_limit_service
from schemas.email import SuccessResponse
from routers.auth import get_current_user


router = APIRouter(prefix="/api/auth", tags=["邮箱验证"])
token_service = TokenService()
email_service = EmailService()


# ============================================================================
# Request/Response Models
# ============================================================================

class VerifyEmailRequest(BaseModel):
    """验证邮箱请求"""
    token: str


class EmailStatusResponse(BaseModel):
    """邮箱状态响应"""
    email_verified: bool
    email: str
    username: str


class ResendVerificationRequest(BaseModel):
    """重新发送验证邮件请求"""
    email: EmailStr


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    验证邮箱地址
    
    Args:
        request: 包含验证令牌的请求
        
    Returns:
        SuccessResponse: 验证成功响应
        
    Raises:
        HTTPException: 令牌无效、已使用或已过期
    """
    # 查找令牌
    try:
        token_record = await EmailVerificationToken.filter(
            token=request.token
        ).prefetch_related('user').first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "验证令牌无效"
                    }
                }
            )
        
        # 检查令牌是否已使用
        if token_record.used_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "TOKEN_USED",
                        "message": "此验证令牌已被使用"
                    }
                }
            )
        
        # 检查令牌是否过期 (48小时)
        from services.token_service import get_current_time
        now = get_current_time()
        if token_record.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "TOKEN_EXPIRED",
                        "message": "验证令牌已过期，请重新发送验证邮件"
                    }
                }
            )
        
        # 更新用户邮箱验证状态
        user = token_record.user
        user.email_verified = True
        user.email_verified_at = now
        await user.save()
        
        # 标记令牌为已使用
        token_record.used_at = now
        await token_record.save()
        
        # 记录日志
        await EmailLog.create(
            email=user.email,
            template_name='email_verification',
            status='success',
            sent_at=now
        )
        
        return SuccessResponse(
            success=True,
            message="邮箱验证成功！",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"验证失败: {str(e)}"
                }
            }
        )


@router.get("/email-status", response_model=EmailStatusResponse)
async def get_email_status(current_user: User = Depends(get_current_user)):
    """
    获取当前用户的邮箱验证状态
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        EmailStatusResponse: 邮箱验证状态
    """
    return EmailStatusResponse(
        email_verified=current_user.email_verified or False,
        email=current_user.email,
        username=current_user.username
    )


@router.post("/resend-verification", response_model=SuccessResponse)
async def resend_verification_email(
    request: ResendVerificationRequest
):
    """
    重新发送验证邮件
    
    Args:
        request: 包含邮箱地址的请求
        
    Returns:
        SuccessResponse: 发送成功响应
        
    Raises:
        HTTPException: 邮箱不存在、已验证或请求过于频繁
    """
    # 频率限制检查 (5分钟内最多3次)
    allowed, retry_after = await rate_limit_service.check_rate_limit(
        operation='resend_verification',
        identifier=request.email,
        window_seconds=300,
        max_attempts=3
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"请求过于频繁，请{retry_after}秒后重试",
                    "details": {
                        "retry_after": retry_after
                    }
                }
            }
        )
    
    try:
        # 查找用户
        user = await User.get_or_none(email=request.email)
        
        if not user:
            # 为了防止邮箱枚举，即使用户不存在也返回成功
            return SuccessResponse(
                success=True,
                message="如果该邮箱已注册，您将收到验证邮件",
                data=None
            )
        
        # 检查邮箱是否已验证
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "ALREADY_VERIFIED",
                        "message": "该邮箱已经验证过了"
                    }
                }
            )
        
        # 使所有旧的未使用令牌失效
        from datetime import timedelta
        from services.token_service import get_current_time
        
        await EmailVerificationToken.filter(
            user=user,
            used_at__isnull=True
        ).update(used_at=get_current_time())
        
        # 生成新的验证令牌
        token = token_service.generate_token()
        expires_at = get_current_time() + timedelta(hours=48)
        
        await EmailVerificationToken.create(
            user=user,
            token=token,
            email=user.email,
            expires_at=expires_at
        )
        
        # 发送验证邮件
        await email_service.send_verification_email(
            email=user.email,
            username=user.username,
            token=token
        )
        
        return SuccessResponse(
            success=True,
            message="验证邮件已发送，请查收",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"发送失败: {str(e)}"
                }
            }
        )
