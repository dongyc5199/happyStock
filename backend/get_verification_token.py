#!/usr/bin/env python3
"""
获取最新的邮箱验证令牌
用于没有配置SMTP时的测试
"""
import asyncio
from tortoise import Tortoise
from models.email_verification_token import EmailVerificationToken
from models.user import User
from config import TORTOISE_ORM, settings


async def get_verification_token():
    """获取测试用的验证令牌"""
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 获取最新的未使用令牌（任何用户）
    token = await EmailVerificationToken.filter(
        used_at__isnull=True
    ).order_by('-created_at').prefetch_related('user').first()
    
    if not token:
        print("❌ 没有找到未使用的验证令牌！")
        print("\n请先执行以下步骤:")
        print("1. 访问: http://localhost:3000/auth/register")
        print("2. 注册一个新用户")
        print("3. 再次运行此脚本获取令牌")
        await Tortoise.close_connections()
        return
    
    user = token.user
    verification_url = f"{settings.APP_BASE_URL}/auth/verify-email?token={token.token}"
    
    print("=" * 70)
    print("📧 最新的邮箱验证令牌")
    print("=" * 70)
    print(f"用户: {user.username} ({user.email})")
    print(f"已验证: {'是' if user.email_verified else '否'}")
    print(f"创建时间: {token.created_at}")
    print(f"过期时间: {token.expires_at}")
    print(f"\n📋 完整令牌:")
    print(f"{token.token}")
    print(f"\n🔗 验证链接:")
    print(f"{verification_url}")
    print("\n" + "=" * 70)
    print("💡 使用方法:")
    print("1. 复制上面的验证链接")
    print("2. 在浏览器中打开")
    print("3. 验证邮箱")
    print("=" * 70)
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(get_verification_token())
