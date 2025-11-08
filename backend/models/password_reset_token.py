"""
密码重置令牌模型
存储用户密码重置请求的验证令牌
"""
from tortoise import fields
from tortoise.models import Model


class PasswordResetToken(Model):
    """
    密码重置令牌表模型
    用于验证密码重置请求的有效性
    """

    id = fields.IntField(pk=True, description="令牌ID")
    token = fields.CharField(max_length=64, unique=True, index=True, description="重置令牌")
    user = fields.ForeignKeyField(
        "models.User",
        related_name="password_reset_tokens",
        on_delete=fields.CASCADE,
        description="关联用户"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    expires_at = fields.DatetimeField(description="过期时间")
    used_at = fields.DatetimeField(null=True, description="使用时间")
    ip_address = fields.CharField(max_length=45, null=True, description="请求IP地址")

    class Meta:
        table = "password_reset_tokens"
        table_description = "密码重置令牌表"
        indexes = [
            ("user_id",),
            ("expires_at",),
        ]

    def __str__(self):
        return f"PasswordResetToken(token={self.token[:8]}...)"

    def __repr__(self):
        return f"<PasswordResetToken {self.token[:8]}...>"
