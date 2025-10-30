"""
WebSocket 连接管理器

负责管理 WebSocket 连接的生命周期、订阅管理、心跳检测和消息广播。
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Connection:
    """WebSocket 连接信息"""
    websocket: WebSocket
    client_id: str
    connected_at: float
    last_heartbeat: float
    subscriptions: Set[str] = field(default_factory=set)
    filters: Dict[str, Any] = field(default_factory=dict)


class ConnectionManager:
    """
    WebSocket 连接管理器
    
    功能:
    - 连接注册/注销
    - 订阅管理 (频道 + 过滤器)
    - 心跳检测 (30秒超时)
    - 消息广播
    """
    
    def __init__(self, heartbeat_interval: int = 30):
        """
        初始化连接管理器
        
        Args:
            heartbeat_interval: 心跳检测间隔 (秒)
        """
        self.active_connections: Dict[str, Connection] = {}
        self.channel_subscribers: Dict[str, Set[str]] = {}  # channel -> client_ids
        self.heartbeat_interval = heartbeat_interval
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        logger.info(f"ConnectionManager initialized (heartbeat_interval={heartbeat_interval}s)")
    
    async def connect(self, websocket: WebSocket) -> str:
        """
        注册新的 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接对象
        
        Returns:
            client_id: 客户端唯一标识
        """
        await websocket.accept()
        
        client_id = str(uuid.uuid4())
        current_time = time.time()
        
        connection = Connection(
            websocket=websocket,
            client_id=client_id,
            connected_at=current_time,
            last_heartbeat=current_time,
        )
        
        self.active_connections[client_id] = connection
        
        logger.info(f"Client connected: {client_id} (total: {len(self.active_connections)})")
        
        # 发送连接成功消息
        await self.send_personal(client_id, {
            "type": "connected",
            "client_id": client_id,
            "server_time": int(current_time),
        })
        
        return client_id
    
    def disconnect(self, client_id: str):
        """
        断开并清理连接
        
        Args:
            client_id: 客户端ID
        """
        if client_id not in self.active_connections:
            return
        
        connection = self.active_connections[client_id]
        
        # 取消所有订阅
        for channel in connection.subscriptions.copy():
            self.unsubscribe(client_id, channel)
        
        # 移除连接
        del self.active_connections[client_id]
        
        logger.info(f"Client disconnected: {client_id} (total: {len(self.active_connections)})")
    
    def subscribe(self, client_id: str, channel: str, filters: Optional[Dict[str, Any]] = None):
        """
        订阅频道
        
        Args:
            client_id: 客户端ID
            channel: 频道名称 (如 "market", "indices", "stock:SH600000")
            filters: 可选的过滤条件
        """
        if client_id not in self.active_connections:
            logger.warning(f"Cannot subscribe: client {client_id} not found")
            return
        
        connection = self.active_connections[client_id]
        connection.subscriptions.add(channel)
        
        if filters:
            connection.filters[channel] = filters
        
        # 更新频道订阅者列表
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        
        self.channel_subscribers[channel].add(client_id)
        
        logger.debug(f"Client {client_id} subscribed to {channel} (filters: {filters})")
    
    def unsubscribe(self, client_id: str, channel: str):
        """
        取消订阅频道
        
        Args:
            client_id: 客户端ID
            channel: 频道名称
        """
        if client_id not in self.active_connections:
            return
        
        connection = self.active_connections[client_id]
        connection.subscriptions.discard(channel)
        
        if channel in connection.filters:
            del connection.filters[channel]
        
        # 更新频道订阅者列表
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(client_id)
            
            # 如果频道没有订阅者，移除频道
            if not self.channel_subscribers[channel]:
                del self.channel_subscribers[channel]
        
        logger.debug(f"Client {client_id} unsubscribed from {channel}")
    
    def update_heartbeat(self, client_id: str):
        """
        更新心跳时间
        
        Args:
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].last_heartbeat = time.time()
    
    async def send_personal(self, client_id: str, message: dict):
        """
        发送消息给特定客户端
        
        Args:
            client_id: 客户端ID
            message: 消息内容 (字典)
        """
        if client_id not in self.active_connections:
            return
        
        connection = self.active_connections[client_id]
        
        try:
            await connection.websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to {client_id}: {e}")
            self.disconnect(client_id)
    
    async def broadcast(self, channel: str, message: dict, exclude: Optional[Set[str]] = None):
        """
        广播消息到频道的所有订阅者
        
        Args:
            channel: 频道名称
            message: 消息内容 (字典)
            exclude: 排除的客户端ID集合
        """
        if channel not in self.channel_subscribers:
            return
        
        exclude = exclude or set()
        subscribers = self.channel_subscribers[channel] - exclude
        
        if not subscribers:
            return
        
        dead_connections = []
        
        for client_id in subscribers:
            if client_id not in self.active_connections:
                dead_connections.append(client_id)
                continue
            
            connection = self.active_connections[client_id]
            
            # 应用过滤器
            if channel in connection.filters:
                if not self._apply_filters(message, connection.filters[channel]):
                    continue
            
            try:
                await connection.websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                dead_connections.append(client_id)
        
        # 清理断开的连接
        for client_id in dead_connections:
            self.disconnect(client_id)
        
        if subscribers:
            logger.debug(f"Broadcasted to {len(subscribers)} subscribers on channel '{channel}'")
    
    def _apply_filters(self, message: dict, filters: Dict[str, Any]) -> bool:
        """
        应用过滤器判断消息是否应该发送
        
        Args:
            message: 消息内容
            filters: 过滤条件
        
        Returns:
            是否通过过滤
        """
        # 简单实现: 检查 symbols 过滤器
        if "symbols" in filters:
            allowed_symbols = set(filters["symbols"])
            
            # 检查消息中的 symbol 字段
            if "data" in message:
                data = message["data"]
                
                # 单个股票数据
                if "symbol" in data:
                    if data["symbol"] not in allowed_symbols:
                        return False
                
                # 股票列表数据
                if "stocks" in data:
                    # 过滤股票列表
                    message["data"]["stocks"] = [
                        stock for stock in data["stocks"]
                        if stock.get("symbol") in allowed_symbols
                    ]
        
        return True
    
    async def start_heartbeat_checker(self):
        """启动心跳检测任务"""
        if self._heartbeat_task is not None:
            logger.warning("Heartbeat checker already running")
            return
        
        self._heartbeat_task = asyncio.create_task(self._heartbeat_checker())
        logger.info("Heartbeat checker started")
    
    async def stop_heartbeat_checker(self):
        """停止心跳检测任务"""
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            
            self._heartbeat_task = None
            logger.info("Heartbeat checker stopped")
    
    async def _heartbeat_checker(self):
        """心跳检测循环"""
        timeout = self.heartbeat_interval * 2  # 2倍心跳间隔作为超时
        
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = time.time()
                dead_connections = []
                
                for client_id, connection in self.active_connections.items():
                    time_since_heartbeat = current_time - connection.last_heartbeat
                    
                    if time_since_heartbeat > timeout:
                        logger.warning(
                            f"Client {client_id} heartbeat timeout "
                            f"({time_since_heartbeat:.1f}s > {timeout}s)"
                        )
                        dead_connections.append(client_id)
                
                # 清理超时连接
                for client_id in dead_connections:
                    self.disconnect(client_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat checker: {e}", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_connections": len(self.active_connections),
            "total_channels": len(self.channel_subscribers),
            "channels": {
                channel: len(subscribers)
                for channel, subscribers in self.channel_subscribers.items()
            },
        }


# 全局单例
_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """获取全局连接管理器实例"""
    global _manager
    
    if _manager is None:
        _manager = ConnectionManager()
    
    return _manager
