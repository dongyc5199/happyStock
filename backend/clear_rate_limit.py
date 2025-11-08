#!/usr/bin/env python3
"""
清除频率限制
用于测试后清理Redis中的限流记录
"""
import asyncio
from services.rate_limit_service import rate_limit_service


async def clear_rate_limits():
    """清除所有测试用户的频率限制"""
    emails = [
        'testuser@example.com',
        'test@example.com'
    ]
    
    print("\n" + "=" * 80)
    print("🧹 清除频率限制")
    print("=" * 80)
    
    for email in emails:
        try:
            await rate_limit_service.clear_rate_limit('password_reset', email)
            print(f"✅ 已清除: {email}")
        except Exception as e:
            print(f"❌ 清除失败 {email}: {e}")
    
    await rate_limit_service.close()
    
    print("\n✅ 清除完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(clear_rate_limits())
