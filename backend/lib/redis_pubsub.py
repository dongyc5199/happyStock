"""
Redis Pub/Sub 模块

负责连接 Redis、订阅频道、接收消息并转发到 WebSocket。
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisPubSub:
    """
    Redis Pub/Sub 处理器
    
    功能:
    - 连接 Redis
    - 订阅多个频道
    - 接收消息并触发回调
    - 发布消息到频道
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        初始化 Redis Pub/Sub 处理器
        
        Args:
            redis_url: Redis 连接 URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.subscribers: Dict[str, List[Callable]] = {}  # channel -> [callback_func, ...]
        self._listen_task: Optional[asyncio.Task] = None
        
        logger.info(f"RedisPubSub initialized (url={redis_url})")
    
    async def connect(self):
        """连接到 Redis"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            
            # 测试连接
            await self.redis_client.ping()
            
            self.pubsub = self.redis_client.pubsub()
            
            logger.info("Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            raise
    
    async def disconnect(self):
        """断开 Redis 连接"""
        if self._listen_task is not None:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            
            self._listen_task = None
        
        if self.pubsub is not None:
            await self.pubsub.close()
            self.pubsub = None
        
        if self.redis_client is not None:
            await self.redis_client.close()
            self.redis_client = None
        
        logger.info("Disconnected from Redis")
    
    async def subscribe(self, channel: str, callback: Callable[[str, dict], None]):
        """
        订阅频道
        
        Args:
            channel: 频道名称 (如 "market:stocks", "market:indices")
            callback: 消息回调函数 callback(channel, message)
        """
        if self.pubsub is None:
            raise RuntimeError("Not connected to Redis")
        
        # 注册回调
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(callback)
        
        # 订阅 Redis 频道
        await self.pubsub.subscribe(channel)
        
        logger.info(f"Subscribed to Redis channel: {channel}")
        
        # 启动监听任务 (如果尚未启动)
        if self._listen_task is None:
            self._listen_task = asyncio.create_task(self._listen_loop())
    
    async def unsubscribe(self, channel: str):
        """
        取消订阅频道
        
        Args:
            channel: 频道名称
        """
        if self.pubsub is None:
            return
        
        # 取消订阅 Redis 频道
        await self.pubsub.unsubscribe(channel)
        
        # 移除回调
        if channel in self.subscribers:
            del self.subscribers[channel]
        
        logger.info(f"Unsubscribed from Redis channel: {channel}")
    
    async def publish(self, channel: str, message: dict):
        """
        发布消息到频道
        
        Args:
            channel: 频道名称
            message: 消息内容 (字典)
        """
        if self.redis_client is None:
            raise RuntimeError("Not connected to Redis")
        
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            await self.redis_client.publish(channel, message_json)
            
            logger.debug(f"Published message to channel '{channel}': {len(message_json)} bytes")
            
        except Exception as e:
            logger.error(f"Failed to publish message to '{channel}': {e}", exc_info=True)
    
    async def _listen_loop(self):
        """监听消息循环"""
        if self.pubsub is None:
            return
        
        logger.info("Redis message listener started")
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    await self._handle_message(message)
        
        except asyncio.CancelledError:
            logger.info("Redis message listener cancelled")
        
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}", exc_info=True)
    
    async def _handle_message(self, raw_message: dict):
        """
        处理接收到的消息
        
        Args:
            raw_message: Redis 原始消息
        """
        channel = raw_message["channel"]
        data = raw_message["data"]
        
        # 解析 JSON
        try:
            message = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from channel '{channel}': {e}")
            return
        
        # 触发回调
        if channel in self.subscribers:
            for callback in self.subscribers[channel]:
                try:
                    # 支持同步和异步回调
                    if asyncio.iscoroutinefunction(callback):
                        await callback(channel, message)
                    else:
                        callback(channel, message)
                
                except Exception as e:
                    logger.error(f"Error in callback for channel '{channel}': {e}", exc_info=True)


# 全局单例
_pubsub: Optional[RedisPubSub] = None


async def get_redis_pubsub() -> RedisPubSub:
    """获取全局 Redis Pub/Sub 实例"""
    global _pubsub
    
    if _pubsub is None:
        _pubsub = RedisPubSub()
        await _pubsub.connect()
    
    return _pubsub


async def close_redis_pubsub():
    """关闭全局 Redis Pub/Sub 实例"""
    global _pubsub
    
    if _pubsub is not None:
        await _pubsub.disconnect()
        _pubsub = None
