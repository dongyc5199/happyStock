"""
邮件发送后台任务
使用 FastAPI BackgroundTasks 实现异步邮件发送
"""
from fastapi import BackgroundTasks
from typing import Optional

from models.user import User
from services.email_service import EmailService
from services.token_service import TokenService


async def send_password_reset_email_task(
    user: User,
    reset_token: str
) -> None:
    """
    后台任务：发送密码重置邮件
    
    Args:
        user: 用户对象
        reset_token: 重置令牌
    """
    email_service = EmailService()
    success, error = await email_service.send_password_reset_email(user, reset_token)
    
    if not success:
        print(f"Failed to send password reset email to {user.email}: {error}")


async def send_password_reset_success_email_task(
    user: User
) -> None:
    """
    后台任务：发送密码重置成功通知邮件
    
    Args:
        user: 用户对象
    """
    email_service = EmailService()
    success, error = await email_service.send_password_reset_success_email(user)
    
    if not success:
        print(f"Failed to send password reset success email to {user.email}: {error}")


async def send_email_verification_email_task(
    user: User,
    verification_token: str
) -> None:
    """
    后台任务：发送邮箱验证邮件
    
    Args:
        user: 用户对象
        verification_token: 验证令牌
    """
    email_service = EmailService()
    success, error = await email_service.send_email_verification_email(user, verification_token)
    
    if not success:
        print(f"Failed to send email verification email to {user.email}: {error}")


async def send_email_change_notice_task(
    old_email: str,
    new_email: str,
    username: str
) -> None:
    """
    后台任务：发送邮箱更改通知邮件
    
    Args:
        old_email: 旧邮箱地址
        new_email: 新邮箱地址
        username: 用户名
    """
    email_service = EmailService()
    success, error = await email_service.send_email_change_notice(old_email, new_email, username)
    
    if not success:
        print(f"Failed to send email change notice to {old_email}: {error}")


def add_send_password_reset_email(
    background_tasks: BackgroundTasks,
    user: User,
    reset_token: str
) -> None:
    """
    添加发送密码重置邮件任务到后台队列
    
    Args:
        background_tasks: FastAPI BackgroundTasks 对象
        user: 用户对象
        reset_token: 重置令牌
    """
    background_tasks.add_task(send_password_reset_email_task, user, reset_token)


def add_send_password_reset_success_email(
    background_tasks: BackgroundTasks,
    user: User
) -> None:
    """
    添加发送密码重置成功邮件任务到后台队列
    
    Args:
        background_tasks: FastAPI BackgroundTasks 对象
        user: 用户对象
    """
    background_tasks.add_task(send_password_reset_success_email_task, user)


def add_send_email_verification_email(
    background_tasks: BackgroundTasks,
    user: User,
    verification_token: str
) -> None:
    """
    添加发送邮箱验证邮件任务到后台队列
    
    Args:
        background_tasks: FastAPI BackgroundTasks 对象
        user: 用户对象
        verification_token: 验证令牌
    """
    background_tasks.add_task(send_email_verification_email_task, user, verification_token)


def add_send_email_change_notice(
    background_tasks: BackgroundTasks,
    old_email: str,
    new_email: str,
    username: str
) -> None:
    """
    添加发送邮箱更改通知任务到后台队列
    
    Args:
        background_tasks: FastAPI BackgroundTasks 对象
        old_email: 旧邮箱地址
        new_email: 新邮箱地址
        username: 用户名
    """
    background_tasks.add_task(send_email_change_notice_task, old_email, new_email, username)
