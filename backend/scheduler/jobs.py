"""
定时任务调度模块
Job Scheduler Module

使用APScheduler实现市场数据的定时更新。
每分钟执行一次价格生成和指数计算。
"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.db_manager_sqlite import DatabaseManager
from lib.price_generator_v2 import PriceGeneratorV2  # 使用V2生成器
from lib.index_calculator import IndexCalculator
from lib.market_state_manager import MarketStateManager
from lib.redis_pubsub import get_redis_pubsub

# 全局调度器实例
scheduler: AsyncIOScheduler = None


async def generate_prices_job():
    """
    价格生成任务
    
    每分钟执行一次，更新所有股票价格和指数值
    """
    try:
        start_time = datetime.now()
        print(f"\n[{start_time.strftime('%H:%M:%S')}] ===== Price Generation Job Started =====")

        db_manager = DatabaseManager()
        price_generator = PriceGeneratorV2(db_manager, steps_per_day=4800)  # 使用V2生成器

        # 1. 生成所有股票的新价格
        print("[1/3] Generating prices for all stocks...")
        updated_count = await generate_all_stocks(price_generator)
        print(f"      [+] Updated {updated_count} stocks")

        # 2. 重新计算所有指数
        print("[2/3] Recalculating all indices...")
        indices_updated = await calculate_all_indices(db_manager)
        print(f"      [+] Updated {indices_updated} indices")

        # 3. 计算耗时
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[3/3] Job completed in {duration:.2f}s")
        
        # 4. 发布到 Redis (实时推送)
        try:
            await publish_market_data(db_manager)
        except Exception as e:
            print(f"[!] Error publishing to Redis: {e}")
        
        print(f"[{end_time.strftime('%H:%M:%S')}] ===== Price Generation Job Finished =====\n")

    except Exception as e:
        print(f"[!] Error in generate_prices_job: {e}")
        import traceback
        traceback.print_exc()


async def generate_all_stocks(price_generator: PriceGeneratorV2) -> int:
    """
    批量生成所有股票的新价格,并插入历史K线数据
    
    Args:
        price_generator: 价格生成器V2实例
        
    Returns:
        更新的股票数量
    """
    import time
    
    conn = price_generator.db_manager.get_connection()
    try:
        cursor = conn.cursor()
        
        # 获取当前时间戳（分钟级别，秒数归零）
        now = datetime.now()
        timestamp_minute = int(now.replace(second=0, microsecond=0).timestamp())
        datetime_str = now.strftime('%Y-%m-%d %H:%M:00')
        
        # 获取所有活跃股票
        cursor.execute("""
            SELECT symbol FROM stocks
            WHERE is_active = 1
            ORDER BY symbol
        """)
        stocks = cursor.fetchall()
        
        # 批量准备数据
        stock_updates = []
        price_data_inserts = []
        
        updated_count = 0
        for row in stocks:
            symbol = row[0]
            
            # 生成新价格
            result = price_generator.generate_next_price(symbol, verbose=False)
            if result:
                # 计算change_value (新价 - 旧价)
                change_value = result['close'] - result['previous_close']
                
                # 准备stocks表更新数据
                stock_updates.append((
                    result['close'],
                    result['previous_close'],
                    round(change_value, 2),
                    result['change_pct'],
                    symbol
                ))
                
                # 准备price_data表插入数据（使用result中的OHLC）
                price_data_inserts.append((
                    'STOCK',
                    symbol,
                    timestamp_minute,
                    datetime_str,
                    result['open'],
                    result['close'],
                    result['high'],
                    result['low'],
                    0,  # volume (暂时为0)
                    0,  # turnover (暂时为0)
                    result['change_pct']
                ))
                
                updated_count += 1
        
        # 批量更新stocks表
        if stock_updates:
            cursor.executemany("""
                UPDATE stocks
                SET current_price = ?,
                    previous_close = ?,
                    change_value = ?,
                    change_pct = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE symbol = ?
            """, stock_updates)
        
        # 批量插入price_data表（使用INSERT OR REPLACE避免重复）
        if price_data_inserts:
            cursor.executemany("""
                INSERT OR REPLACE INTO price_data (
                    target_type, target_code, timestamp, datetime,
                    open, close, high, low, volume, turnover, change_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, price_data_inserts)
        
        conn.commit()
        return updated_count
        
    finally:
        conn.close()


async def publish_market_data(db_manager: DatabaseManager):
    """
    将最新的市场数据发布到 Redis
    
    Args:
        db_manager: 数据库管理器实例
    """
    try:
        # 获取 Redis Pub/Sub 实例
        pubsub = await get_redis_pubsub()
        
        conn = db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # 获取所有活跃股票的最新数据
            cursor.execute("""
                SELECT 
                    symbol, name, sector_code,
                    current_price, previous_close, change_value, change_pct,
                    volume, turnover
                FROM stocks
                WHERE is_active = 1
                ORDER BY symbol
            """)
            
            stocks_data = []
            for row in cursor.fetchall():
                stock_data = {
                    "symbol": row[0],
                    "name": row[1],
                    "sector": row[2],
                    "current_price": float(row[3]) if row[3] else 0,
                    "previous_close": float(row[4]) if row[4] else 0,
                    "change_value": float(row[5]) if row[5] else 0,
                    "change_pct": float(row[6]) if row[6] else 0,
                    "volume": int(row[7]) if row[7] else 0,
                    "turnover": float(row[8]) if row[8] else 0,
                    "timestamp": int(datetime.now().timestamp()),
                }
                stocks_data.append(stock_data)
                
                # 发布单只股票数据
                await pubsub.publish(f"market:stock:{row[0]}", stock_data)
            
            # 发布全市场数据
            market_message = {
                "type": "market_update",
                "data": stocks_data,
                "timestamp": int(datetime.now().timestamp()),
            }
            await pubsub.publish("market:stocks", market_message)
            
            print(f"[4/4] Published {len(stocks_data)} stocks to Redis")
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[!] Failed to publish market data: {e}")
        import traceback
        traceback.print_exc()


async def calculate_all_indices(db_manager: DatabaseManager) -> int:
    """
    批量计算所有指数的新值，并插入历史K线数据
    
    Args:
        db_manager: 数据库管理器实例
        
    Returns:
        更新的指数数量
    """
    conn = db_manager.get_connection()
    try:
        cursor = conn.cursor()
        
        # 获取当前时间戳（分钟级别）
        now = datetime.now()
        timestamp_minute = int(now.replace(second=0, microsecond=0).timestamp())
        datetime_str = now.strftime('%Y-%m-%d %H:%M:00')
        
        # 获取所有指数
        cursor.execute("""
            SELECT code FROM indices
            ORDER BY code
        """)
        indices = cursor.fetchall()
        
        # 批量准备数据
        index_updates = []
        price_data_inserts = []
        
        updated_count = 0
        for row in indices:
            index_code = row[0]
            
            # 计算并更新指数值
            try:
                # 为每个指数创建一个IndexCalculator实例
                calculator = IndexCalculator(index_code)
                
                # calculate_index_value()使用当前股票价格计算指数
                new_value = calculator.calculate_index_value()
                
                if new_value:
                    # 获取前一个值计算涨跌
                    cursor.execute("""
                        SELECT current_value FROM indices
                        WHERE code = ?
                    """, (index_code,))
                    prev_row = cursor.fetchone()
                    prev_value = prev_row[0] if prev_row else new_value
                    
                    change_pct = ((new_value - prev_value) / prev_value * 100) if prev_value > 0 else 0
                    
                    # 准备indices表更新数据
                    index_updates.append((new_value, change_pct, index_code))
                    
                    # 准备price_data表插入数据
                    # 对于指数，open/high/low使用简化计算
                    open_val = prev_value
                    close_val = new_value
                    high_val = max(open_val, close_val)
                    low_val = min(open_val, close_val)
                    
                    price_data_inserts.append((
                        'INDEX',
                        index_code,
                        timestamp_minute,
                        datetime_str,
                        round(open_val, 2),
                        round(close_val, 2),
                        round(high_val, 2),
                        round(low_val, 2),
                        0,  # volume
                        0,  # turnover
                        round(change_pct, 2)
                    ))
                    
                    updated_count += 1
            except Exception as e:
                print(f"      ! Error calculating index {index_code}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 批量更新indices表
        if index_updates:
            cursor.executemany("""
                UPDATE indices
                SET current_value = ?,
                    change_pct = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            """, index_updates)
        
        # 批量插入price_data表
        if price_data_inserts:
            cursor.executemany("""
                INSERT OR REPLACE INTO price_data (
                    target_type, target_code, timestamp, datetime,
                    open, close, high, low, volume, turnover, change_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, price_data_inserts)
        
        conn.commit()
        return updated_count
        
    finally:
        conn.close()


def setup_scheduler() -> AsyncIOScheduler:
    """
    设置调度器
    
    Returns:
        配置好的调度器实例
    """
    global scheduler
    
    if scheduler is not None:
        print("[*] Scheduler already initialized")
        return scheduler
    
    # 创建异步调度器
    scheduler = AsyncIOScheduler()
    
    # 添加价格生成任务（每3秒执行一次，符合A股行情习惯）
    scheduler.add_job(
        generate_prices_job,
        trigger=IntervalTrigger(seconds=3),
        id='generate_prices',
        name='Generate Prices and Calculate Indices',
        replace_existing=True,
        max_instances=1,  # 防止并发执行
    )
    
    print("[+] Scheduler configured successfully")
    print("    - Job: generate_prices (interval: 3 seconds)")
    
    return scheduler


def start_scheduler():
    """启动调度器"""
    global scheduler
    
    if scheduler is None:
        scheduler = setup_scheduler()
    
    if not scheduler.running:
        scheduler.start()
        print("[+] Scheduler started")
    else:
        print("[*] Scheduler already running")


def shutdown_scheduler():
    """关闭调度器"""
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=True)
        print("[+] Scheduler shut down")
    else:
        print("[*] Scheduler not running")


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_job():
        """测试定时任务"""
        print("=== Testing Scheduler ===\n")
        
        # 设置并启动调度器
        setup_scheduler()
        start_scheduler()
        
        print("\nScheduler is running. Will execute job every 60 seconds.")
        print("Press Ctrl+C to stop...\n")
        
        try:
            # 运行3分钟后自动停止
            await asyncio.sleep(180)
        except KeyboardInterrupt:
            print("\n\nStopping scheduler...")
        finally:
            shutdown_scheduler()
            print("\n=== Test Complete ===")
    
    # 运行测试
    asyncio.run(test_job())
