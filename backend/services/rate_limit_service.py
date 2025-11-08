"""
频率限制服务
使用 Redis 实现滑动窗口频率限制
"""
import time
from typing import Optional
import redis.asyncio as redis
from config import settings


class RateLimitService:
    """频率限制服务类"""

    def __init__(self):
        """初始化 Redis 连接"""
        self.redis_client: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        """获取 Redis 连接"""
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        return self.redis_client

    async def check_rate_limit(
        self,
        operation: str,
        identifier: str,
        window_seconds: int = 300,
        max_attempts: int = 3
    ) -> tuple[bool, Optional[int]]:
        """
        检查频率限制（滑动窗口算法）
        
        Args:
            operation: 操作类型 (如 'password_reset', 'email_verification')
            identifier: 标识符 (如 email, user_id)
            window_seconds: 时间窗口（秒）
            max_attempts: 最大尝试次数
            
        Returns:
            tuple[bool, Optional[int]]: (是否允许, 剩余冷却时间秒数)
        """
        redis_conn = await self.get_redis()
        key = f"ratelimit:{operation}:{identifier}"
        now = time.time()
        window_start = now - window_seconds

        try:
            # 使用 Redis 事务
            pipe = redis_conn.pipeline()

            # 移除过期的时间戳
            pipe.zremrangebyscore(key, 0, window_start)

            # 获取当前窗口内的请求数
            pipe.zcard(key)

            # 执行事务
            results = await pipe.execute()
            count = results[1]

            if count >= max_attempts:
                # 获取最早的请求时间戳
                oldest = await redis_conn.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_timestamp = oldest[0][1]
                    retry_after = int(window_seconds - (now - oldest_timestamp))
                    return False, retry_after
                return False, window_seconds

            # 添加当前请求时间戳
            await redis_conn.zadd(key, {str(now): now})
            await redis_conn.expire(key, window_seconds)

            return True, None

        except redis.RedisError as e:
            # Redis 错误时，为了不阻塞用户，允许请求通过
            # 但应该记录日志
            print(f"Redis error in rate limiting: {e}")
            return True, None

    async def get_remaining_cooldown(
        self,
        operation: str,
        identifier: str,
        window_seconds: int = 300
    ) -> int:
        """
        获取剩余冷却时间
        
        Args:
            operation: 操作类型
            identifier: 标识符
            window_seconds: 时间窗口（秒）
            
        Returns:
            int: 剩余冷却时间（秒），0表示无冷却
        """
        redis_conn = await self.get_redis()
        key = f"ratelimit:{operation}:{identifier}"
        now = time.time()

        try:
            # 获取最早的请求时间戳
            oldest = await redis_conn.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_timestamp = oldest[0][1]
                cooldown = int(window_seconds - (now - oldest_timestamp))
                return max(0, cooldown)
            return 0

        except redis.RedisError:
            return 0

    async def clear_rate_limit(
        self,
        operation: str,
        identifier: str
    ) -> None:
        """
        清除频率限制（用于测试或管理员操作）
        
        Args:
            operation: 操作类型
            identifier: 标识符
        """
        redis_conn = await self.get_redis()
        key = f"ratelimit:{operation}:{identifier}"
        await redis_conn.delete(key)

    async def close(self) -> None:
        """关闭 Redis 连接"""
        if self.redis_client:
            await self.redis_client.close()


# 创建全局实例
rate_limit_service = RateLimitService()
