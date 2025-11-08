"""
邮件发送日志模型
记录所有邮件发送操作，用于审计和故障排查
"""
from tortoise import fields
from tortoise.models import Model


class EmailType(str):
    """邮件类型枚举"""
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    EMAIL_CHANGE_NOTICE = "email_change_notice"


class EmailStatus(str):
    """邮件发送状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailLog(Model):
    """
    邮件发送日志表模型
    记录所有邮件发送操作
    """

    id = fields.IntField(pk=True, description="日志ID")
    user = fields.ForeignKeyField(
        "models.User",
        related_name="email_logs",
        on_delete=fields.SET_NULL,
        null=True,
        description="关联用户（可选）"
    )
    recipient_email = fields.CharField(max_length=255, index=True, description="收件人邮箱")
    email_type = fields.CharField(max_length=30, index=True, description="邮件类型")
    subject = fields.CharField(max_length=255, description="邮件主题")
    sent_at = fields.DatetimeField(auto_now_add=True, index=True, description="发送时间")
    status = fields.CharField(max_length=10, index=True, description="发送状态")
    error_message = fields.TextField(null=True, description="错误信息")
    smtp_message_id = fields.CharField(max_length=255, null=True, description="SMTP消息ID")

    class Meta:
        table = "email_logs"
        table_description = "邮件发送日志表"
        indexes = [
            ("user_id",),
            ("recipient_email",),
            ("email_type",),
            ("sent_at",),
            ("status",),
        ]

    def __str__(self):
        return f"EmailLog(to={self.recipient_email}, type={self.email_type}, status={self.status})"

    def __repr__(self):
        return f"<EmailLog {self.recipient_email} {self.email_type}>"
