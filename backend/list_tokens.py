"""
列出所有令牌及其状态
"""
import asyncio
from tortoise import Tortoise
from models.password_reset_token import PasswordResetToken
from config import TORTOISE_ORM
from datetime import datetime, timezone


async def list_all_tokens():
    """列出所有令牌"""
    await Tortoise.init(config=TORTOISE_ORM)
    
    tokens = await PasswordResetToken.all().order_by('-created_at').limit(10)
    
    print("=" * 80)
    print("📋 最近10个密码重置令牌")
    print("=" * 80)
    
    now = datetime.now(timezone.utc).astimezone()
    
    for idx, token in enumerate(tokens, 1):
        is_expired = now > token.expires_at
        is_used = token.used_at is not None
        
        if is_used:
            status = "❌ 已使用"
        elif is_expired:
            status = "⏰ 已过期"
        else:
            status = "✅ 有效"
        
        print(f"\n{idx}. {status}")
        print(f"   令牌: {token.token[:40]}...")
        print(f"   创建: {token.created_at}")
        print(f"   过期: {token.expires_at}")
        if token.used_at:
            print(f"   使用: {token.used_at}")
    
    print("\n" + "=" * 80)
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(list_all_tokens())
