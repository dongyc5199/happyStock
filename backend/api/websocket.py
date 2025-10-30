"""
WebSocket API 路由

提供 WebSocket 端点用于实时数据推送。

端点:
- /ws/market: 全市场行情 (所有股票)
- /ws/indices: 指数行情
- /ws/stock/{symbol}: 单个股票行情
"""
import asyncio
import json
import logging
from typing import Optional, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from datetime import datetime

from lib.websocket_manager import get_connection_manager
from lib.redis_pubsub import get_redis_pubsub

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/market")
async def websocket_market_endpoint(
    websocket: WebSocket,
    symbols: Optional[str] = Query(None, description="逗号分隔的股票代码,用于过滤")
):
    """
    全市场行情 WebSocket 端点
    
    订阅频道: market:stocks
    
    消息格式:
    {
        "type": "market_update",
        "data": {
            "timestamp": 1234567890,
            "stocks": [
                {
                    "symbol": "SH600000",
                    "name": "浦发银行",
                    "price": 10.25,
                    "change": 0.05,
                    "change_percent": 0.49,
                    "volume": 1234567,
                    ...
                },
                ...
            ]
        }
    }
    """
    manager = get_connection_manager()
    pubsub = await get_redis_pubsub()
    
    # 连接客户端
    client_id = await manager.connect(websocket)
    
    # 解析过滤器
    filters = None
    if symbols:
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        if symbol_list:
            filters = {"symbols": symbol_list}
            logger.info(f"Client {client_id} filtering symbols: {symbol_list}")
    
    # 订阅市场数据频道
    channel = "market:stocks"
    manager.subscribe(client_id, channel, filters)
    
    # 定义 Redis 消息回调 (转发到 WebSocket)
    async def on_market_message(ch: str, message: dict):
        await manager.broadcast(channel, message)
    
    # 订阅 Redis 频道 (仅第一次订阅时)
    if channel not in pubsub.subscribers:
        await pubsub.subscribe(channel, on_market_message)
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to market data stream",
            "channel": channel,
            "filters": filters,
        })
        
        # 处理客户端消息
        while True:
            data = await websocket.receive_json()
            await handle_client_message(client_id, data, manager, websocket)
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected from market stream")
    
    except Exception as e:
        logger.error(f"Error in market WebSocket: {e}", exc_info=True)
    
    finally:
        manager.disconnect(client_id)


@router.websocket("/ws/indices")
async def websocket_indices_endpoint(websocket: WebSocket):
    """
    指数行情 WebSocket 端点
    
    订阅频道: market:indices
    
    消息格式:
    {
        "type": "indices_update",
        "data": {
            "timestamp": 1234567890,
            "indices": [
                {
                    "symbol": "HAPPY300",
                    "name": "快乐300",
                    "value": 1250.45,
                    "change": 12.30,
                    "change_percent": 0.99,
                    ...
                },
                ...
            ]
        }
    }
    """
    manager = get_connection_manager()
    pubsub = await get_redis_pubsub()
    
    # 连接客户端
    client_id = await manager.connect(websocket)
    
    # 订阅指数数据频道
    channel = "market:indices"
    manager.subscribe(client_id, channel)
    
    # 定义 Redis 消息回调
    async def on_indices_message(ch: str, message: dict):
        await manager.broadcast(channel, message)
    
    # 订阅 Redis 频道
    if channel not in pubsub.subscribers:
        await pubsub.subscribe(channel, on_indices_message)
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to indices data stream",
            "channel": channel,
        })
        
        # 处理客户端消息
        while True:
            data = await websocket.receive_json()
            await handle_client_message(client_id, data, manager, websocket)
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected from indices stream")
    
    except Exception as e:
        logger.error(f"Error in indices WebSocket: {e}", exc_info=True)
    
    finally:
        manager.disconnect(client_id)


@router.websocket("/ws/stock/{symbol}")
async def websocket_stock_endpoint(websocket: WebSocket, symbol: str):
    """
    单个股票行情 WebSocket 端点
    
    订阅频道: market:stock:{symbol}
    
    消息格式:
    {
        "type": "stock_update",
        "data": {
            "timestamp": 1234567890,
            "symbol": "SH600000",
            "name": "浦发银行",
            "price": 10.25,
            "change": 0.05,
            "change_percent": 0.49,
            "volume": 1234567,
            "amount": 12678900.00,
            "high": 10.30,
            "low": 10.20,
            "open": 10.22,
            ...
        }
    }
    """
    manager = get_connection_manager()
    pubsub = await get_redis_pubsub()
    
    # 连接客户端
    client_id = await manager.connect(websocket)
    
    # 订阅股票数据频道
    channel = f"market:stock:{symbol}"
    manager.subscribe(client_id, channel)
    
    # 定义 Redis 消息回调
    async def on_stock_message(ch: str, message: dict):
        await manager.broadcast(channel, message)
    
    # 订阅 Redis 频道
    if channel not in pubsub.subscribers:
        await pubsub.subscribe(channel, on_stock_message)
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "welcome",
            "message": f"Connected to stock {symbol} data stream",
            "channel": channel,
            "symbol": symbol,
        })
        
        # 处理客户端消息
        while True:
            data = await websocket.receive_json()
            await handle_client_message(client_id, data, manager, websocket)
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected from stock {symbol} stream")
    
    except Exception as e:
        logger.error(f"Error in stock {symbol} WebSocket: {e}", exc_info=True)
    
    finally:
        manager.disconnect(client_id)


async def handle_client_message(
    client_id: str,
    message: dict,
    manager,
    websocket: WebSocket
):
    """
    处理客户端发送的消息
    
    支持的消息类型:
    - ping: 心跳检测
    - subscribe: 订阅频道
    - unsubscribe: 取消订阅
    - snapshot: 请求当前快照
    """
    msg_type = message.get("type")
    
    if msg_type == "ping":
        # 心跳响应
        manager.update_heartbeat(client_id)
        await websocket.send_json({
            "type": "pong",
            "timestamp": int(datetime.now().timestamp()),
        })
    
    elif msg_type == "subscribe":
        # 动态订阅新频道
        channel = message.get("channel")
        filters = message.get("filters")
        
        if channel:
            manager.subscribe(client_id, channel, filters)
            await websocket.send_json({
                "type": "subscribed",
                "channel": channel,
                "filters": filters,
            })
    
    elif msg_type == "unsubscribe":
        # 取消订阅频道
        channel = message.get("channel")
        
        if channel:
            manager.unsubscribe(client_id, channel)
            await websocket.send_json({
                "type": "unsubscribed",
                "channel": channel,
            })
    
    elif msg_type == "snapshot":
        # 请求当前快照 (需要实现数据库查询)
        await websocket.send_json({
            "type": "error",
            "message": "Snapshot not implemented yet",
        })
    
    else:
        # 未知消息类型
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {msg_type}",
        })


@router.get("/ws/stats")
async def websocket_stats():
    """
    获取 WebSocket 连接统计信息
    
    返回:
    {
        "total_connections": 10,
        "total_channels": 3,
        "channels": {
            "market:stocks": 5,
            "market:indices": 3,
            "market:stock:SH600000": 2
        }
    }
    """
    manager = get_connection_manager()
    return manager.get_stats()
