"""
令牌服务
负责生成、验证和管理密码重置令牌和邮箱验证令牌
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from tortoise.exceptions import DoesNotExist

from models.password_reset_token import PasswordResetToken
from models.email_verification_token import EmailVerificationToken, TokenType
from models.user import User
from config import settings


def get_current_time() -> datetime:
    """
    获取当前时间
    返回timezone-aware datetime以匹配Tortoise ORM的行为
    """
    from datetime import timezone
    return datetime.now(timezone.utc).astimezone()


class TokenService:
    """令牌服务类"""

    @staticmethod
    def generate_token() -> str:
        """
        生成加密安全的随机令牌
        使用 secrets.token_urlsafe(32) 生成43个字符的URL安全字符串
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_password_reset_token(
        user: User,
        ip_address: Optional[str] = None
    ) -> PasswordResetToken:
        """
        创建密码重置令牌
        
        Args:
            user: 用户对象
            ip_address: 请求来源IP地址
            
        Returns:
            PasswordResetToken: 创建的令牌对象
        """
        token = TokenService.generate_token()
        expires_at = get_current_time() + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_EXPIRY)

        reset_token = await PasswordResetToken.create(
            token=token,
            user=user,
            expires_at=expires_at,
            ip_address=ip_address
        )
        return reset_token

    @staticmethod
    async def verify_password_reset_token(token: str) -> Tuple[bool, Optional[str], Optional[PasswordResetToken]]:
        """
        验证密码重置令牌
        
        Args:
            token: 令牌字符串
            
        Returns:
            Tuple[bool, Optional[str], Optional[PasswordResetToken]]:
                (是否有效, 错误消息, 令牌对象)
        """
        try:
            reset_token = await PasswordResetToken.get(token=token).prefetch_related('user')
        except DoesNotExist:
            return False, "TOKEN_NOT_FOUND", None

        # 检查是否已使用
        if reset_token.used_at is not None:
            return False, "TOKEN_USED", reset_token

        # 检查是否过期
        if get_current_time() > reset_token.expires_at:
            return False, "TOKEN_EXPIRED", reset_token

        return True, None, reset_token

    @staticmethod
    async def mark_password_reset_token_used(token: PasswordResetToken) -> None:
        """
        标记密码重置令牌为已使用
        
        Args:
            token: 令牌对象
        """
        token.used_at = get_current_time()
        await token.save()

    @staticmethod
    async def invalidate_user_password_reset_tokens(user: User) -> int:
        """
        使用户的所有未使用的密码重置令牌失效
        
        Args:
            user: 用户对象
            
        Returns:
            int: 失效的令牌数量
        """
        count = await PasswordResetToken.filter(
            user=user,
            used_at__isnull=True,
            expires_at__gt=get_current_time()
        ).update(used_at=get_current_time())
        return count

    @staticmethod
    async def create_email_verification_token(
        user: User,
        email: str,
        token_type: str = TokenType.REGISTRATION
    ) -> EmailVerificationToken:
        """
        创建邮箱验证令牌
        
        Args:
            user: 用户对象
            email: 待验证的邮箱地址
            token_type: 令牌类型 ('registration' 或 'email_change')
            
        Returns:
            EmailVerificationToken: 创建的令牌对象
        """
        token = TokenService.generate_token()
        expires_at = get_current_time() + timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY)

        # 使该用户该邮箱的旧令牌失效
        await EmailVerificationToken.filter(
            user=user,
            email=email,
            used_at__isnull=True
        ).update(used_at=get_current_time())

        verification_token = await EmailVerificationToken.create(
            token=token,
            user=user,
            email=email,
            token_type=token_type,
            expires_at=expires_at
        )
        return verification_token

    @staticmethod
    async def verify_email_verification_token(token: str) -> Tuple[bool, Optional[str], Optional[EmailVerificationToken]]:
        """
        验证邮箱验证令牌
        
        Args:
            token: 令牌字符串
            
        Returns:
            Tuple[bool, Optional[str], Optional[EmailVerificationToken]]:
                (是否有效, 错误消息, 令牌对象)
        """
        try:
            verification_token = await EmailVerificationToken.get(token=token).prefetch_related('user')
        except DoesNotExist:
            return False, "TOKEN_NOT_FOUND", None

        # 检查是否已使用
        if verification_token.used_at is not None:
            return False, "TOKEN_USED", verification_token

        # 检查是否过期
        if get_current_time() > verification_token.expires_at:
            return False, "TOKEN_EXPIRED", verification_token

        return True, None, verification_token

    @staticmethod
    async def mark_email_verification_token_used(token: EmailVerificationToken) -> None:
        """
        标记邮箱验证令牌为已使用
        
        Args:
            token: 令牌对象
        """
        token.used_at = get_current_time()
        await token.save()

    @staticmethod
    async def cleanup_expired_tokens() -> Tuple[int, int]:
        """
        清理过期的令牌（30天前过期的）
        
        Returns:
            Tuple[int, int]: (清理的密码重置令牌数, 清理的邮箱验证令牌数)
        """
        cutoff_date = get_current_time() - timedelta(days=30)

        password_reset_count = await PasswordResetToken.filter(
            expires_at__lt=cutoff_date
        ).delete()

        email_verification_count = await EmailVerificationToken.filter(
            expires_at__lt=cutoff_date
        ).delete()

        return password_reset_count, email_verification_count
