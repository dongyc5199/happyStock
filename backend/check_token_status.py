"""
检查特定令牌的状态
"""
import asyncio
import sys
from tortoise import Tortoise
from models.password_reset_token import PasswordResetToken
from config import TORTOISE_ORM
from datetime import datetime, timezone


async def check_token_status(token_str: str):
    """检查令牌状态"""
    await Tortoise.init(config=TORTOISE_ORM)
    
    token = await PasswordResetToken.get_or_none(token=token_str)
    
    if not token:
        print(f"❌ 令牌不存在: {token_str[:20]}...")
    else:
        print("=" * 70)
        print("🔍 令牌状态详情")
        print("=" * 70)
        print(f"令牌: {token.token[:40]}...")
        print(f"创建时间: {token.created_at}")
        print(f"过期时间: {token.expires_at}")
        print(f"使用时间: {token.used_at if token.used_at else '未使用'}")
        print(f"IP地址: {token.ip_address}")
        
        # 检查过期
        now = datetime.now(timezone.utc).astimezone()
        is_expired = now > token.expires_at
        is_used = token.used_at is not None
        
        print(f"\n状态:")
        if is_used:
            print(f"  ❌ 已使用 (于 {token.used_at})")
        elif is_expired:
            print(f"  ❌ 已过期")
        else:
            print(f"  ✅ 有效")
        print("=" * 70)
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_token_status.py <token>")
        sys.exit(1)
    
    token_str = sys.argv[1]
    asyncio.run(check_token_status(token_str))
