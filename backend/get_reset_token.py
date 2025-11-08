"""
获取最新的密码重置令牌
用于没有配置SMTP时的测试
"""
import asyncio
from tortoise import Tortoise
from models.password_reset_token import PasswordResetToken
from models.user import User
from config import TORTOISE_ORM, settings


async def get_test_token():
    """获取测试用的重置令牌"""
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 获取最新的未使用令牌（任何用户）
    token = await PasswordResetToken.filter(
        used_at__isnull=True
    ).order_by('-created_at').prefetch_related('user').first()
    
    if not token:
        print("❌ 没有找到未使用的令牌！")
        print("\n请先执行以下步骤:")
        print("1. 访问: http://localhost:3000/auth/forgot-password")
        print("2. 输入任意注册用户的邮箱（如: testuser@example.com 或 test@example.com）")
        print("3. 点击'发送重置邮件'")
        print("4. 再次运行此脚本获取令牌")
        await Tortoise.close_connections()
        return
    
    user = token.user
    
    reset_url = f"{settings.APP_BASE_URL}/auth/reset-password?token={token.token}"
    print("=" * 70)
    print("🔑 最新的密码重置令牌")
    print("=" * 70)
    print(f"用户: {user.username} ({user.email})")
    print(f"创建时间: {token.created_at}")
    print(f"过期时间: {token.expires_at}")
    print(f"\n📋 完整令牌:")
    print(f"{token.token}")
    print(f"\n🔗 重置链接:")
    print(f"{reset_url}")
    print("\n" + "=" * 70)
    print("💡 使用方法:")
    print("1. 复制上面的重置链接")
    print("2. 在浏览器中打开")
    print("3. 设置新密码")
    print("=" * 70)
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(get_test_token())
