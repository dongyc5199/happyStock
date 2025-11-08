"""
邮件服务
负责发送各类邮件（密码重置、邮箱验证等）
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from models.email_log import EmailLog, EmailType, EmailStatus
from models.user import User
from config import settings


class EmailService:
    """邮件服务类"""

    def __init__(self):
        """初始化邮件服务"""
        # 设置 Jinja2 模板环境
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    async def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        email_type: str,
        user: Optional[User] = None
    ) -> tuple[bool, Optional[str]]:
        """
        发送邮件
        
        Args:
            recipient_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            email_type: 邮件类型
            user: 关联用户（可选）
            
        Returns:
            tuple[bool, Optional[str]]: (是否成功, 错误消息)
        """
        # 创建邮件日志记录
        email_log = await EmailLog.create(
            user=user,
            recipient_email=recipient_email,
            email_type=email_type,
            subject=subject,
            status=EmailStatus.PENDING
        )

        try:
            # 创建邮件消息
            message = MIMEMultipart('alternative')
            message['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message['To'] = recipient_email
            message['Subject'] = subject

            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)

            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
            )

            # 更新日志状态为成功
            email_log.status = EmailStatus.SENT
            await email_log.save()

            return True, None

        except Exception as e:
            # 更新日志状态为失败
            email_log.status = EmailStatus.FAILED
            email_log.error_message = str(e)
            await email_log.save()

            return False, str(e)

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染邮件模板
        
        Args:
            template_name: 模板文件名
            context: 模板上下文变量
            
        Returns:
            str: 渲染后的HTML内容
        """
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    async def send_password_reset_email(
        self,
        user: User,
        reset_token: str
    ) -> tuple[bool, Optional[str]]:
        """
        发送密码重置邮件
        
        Args:
            user: 用户对象
            reset_token: 重置令牌
            
        Returns:
            tuple[bool, Optional[str]]: (是否成功, 错误消息)
        """
        reset_url = f"{settings.APP_BASE_URL}/auth/reset-password?token={reset_token}"
        
        context = {
            'username': user.username,
            'reset_url': reset_url,
            'valid_hours': settings.PASSWORD_RESET_TOKEN_EXPIRY // 3600,
            'current_year': datetime.now().year,
        }

        html_content = self.render_template('password_reset.html', context)
        subject = "密码重置请求 - 快乐股票"

        return await self.send_email(
            recipient_email=user.email,
            subject=subject,
            html_content=html_content,
            email_type=EmailType.PASSWORD_RESET,
            user=user
        )

    async def send_password_reset_success_email(
        self,
        user: User
    ) -> tuple[bool, Optional[str]]:
        """
        发送密码重置成功通知邮件
        
        Args:
            user: 用户对象
            
        Returns:
            tuple[bool, Optional[str]]: (是否成功, 错误消息)
        """
        context = {
            'username': user.username,
            'reset_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_year': datetime.now().year,
        }

        html_content = self.render_template('password_reset_success.html', context)
        subject = "密码重置成功通知 - 快乐股票"

        return await self.send_email(
            recipient_email=user.email,
            subject=subject,
            html_content=html_content,
            email_type=EmailType.PASSWORD_RESET_SUCCESS,
            user=user
        )

    async def send_email_verification_email(
        self,
        user: User,
        verification_token: str
    ) -> tuple[bool, Optional[str]]:
        """
        发送邮箱验证邮件
        
        Args:
            user: 用户对象
            verification_token: 验证令牌
            
        Returns:
            tuple[bool, Optional[str]]: (是否成功, 错误消息)
        """
        verification_url = f"{settings.APP_BASE_URL}/auth/verify-email?token={verification_token}"
        
        context = {
            'username': user.username,
            'verification_url': verification_url,
            'valid_hours': settings.EMAIL_VERIFICATION_TOKEN_EXPIRY // 3600,
            'current_year': datetime.now().year,
        }

        html_content = self.render_template('email_verification.html', context)
        subject = "邮箱验证 - 快乐股票"

        return await self.send_email(
            recipient_email=user.email,
            subject=subject,
            html_content=html_content,
            email_type=EmailType.EMAIL_VERIFICATION,
            user=user
        )

    async def send_email_change_notice(
        self,
        old_email: str,
        new_email: str,
        username: str
    ) -> tuple[bool, Optional[str]]:
        """
        发送邮箱更改通知邮件（发送到旧邮箱）
        
        Args:
            old_email: 旧邮箱地址
            new_email: 新邮箱地址
            username: 用户名
            
        Returns:
            tuple[bool, Optional[str]]: (是否成功, 错误消息)
        """
        context = {
            'username': username,
            'old_email': old_email,
            'new_email': new_email,
            'change_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_year': datetime.now().year,
        }

        html_content = self.render_template('email_change_notice.html', context)
        subject = "邮箱更改通知 - 快乐股票"

        return await self.send_email(
            recipient_email=old_email,
            subject=subject,
            html_content=html_content,
            email_type=EmailType.EMAIL_CHANGE_NOTICE,
            user=None  # 邮箱已更改，不关联用户
        )
    
    async def send_verification_email(
        self,
        email: str,
        username: str,
        token: str
    ) -> tuple[bool, Optional[str]]:
        """
        发送邮箱验证邮件（便捷方法）
        
        Args:
            email: 收件人邮箱
            username: 用户名
            token: 验证令牌
            
        Returns:
            tuple[bool, Optional[str]]: (是否成功, 错误消息)
        """
        verification_url = f"{settings.APP_BASE_URL}/auth/verify-email?token={token}"
        
        context = {
            'username': username,
            'email': email,
            'verification_url': verification_url,
            'valid_hours': 48,  # 48小时有效期
            'app_url': settings.APP_BASE_URL,
            'support_email': settings.SMTP_SENDER_EMAIL,
            'current_year': datetime.now().year,
        }

        html_content = self.render_template('email_verification.html', context)
        subject = "验证您的邮箱 - happyStock"

        return await self.send_email(
            recipient_email=email,
            subject=subject,
            html_content=html_content,
            email_type=EmailType.EMAIL_VERIFICATION,
            user=None
        )
