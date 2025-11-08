"""
邮箱验证令牌模型
存储用户邮箱验证请求的验证令牌
"""
from tortoise import fields
from tortoise.models import Model


class TokenType(str):
    """令牌类型枚举"""
    REGISTRATION = "registration"
    EMAIL_CHANGE = "email_change"


class EmailVerificationToken(Model):
    """
    邮箱验证令牌表模型
    用于验证用户邮箱地址的有效性
    """

    id = fields.IntField(pk=True, description="令牌ID")
    token = fields.CharField(max_length=64, unique=True, index=True, description="验证令牌")
    user = fields.ForeignKeyField(
        "models.User",
        related_name="email_verification_tokens",
        on_delete=fields.CASCADE,
        description="关联用户"
    )
    email = fields.CharField(max_length=255, description="待验证的邮箱地址")
    token_type = fields.CharField(
        max_length=20,
        description="令牌类型: registration 或 email_change"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    expires_at = fields.DatetimeField(description="过期时间")
    used_at = fields.DatetimeField(null=True, description="使用时间")

    class Meta:
        table = "email_verification_tokens"
        table_description = "邮箱验证令牌表"
        indexes = [
            ("user_id",),
            ("email",),
            ("expires_at",),
        ]

    def __str__(self):
        return f"EmailVerificationToken(token={self.token[:8]}..., email={self.email})"

    def __repr__(self):
        return f"<EmailVerificationToken {self.token[:8]}... {self.email}>"
