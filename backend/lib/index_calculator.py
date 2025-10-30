"""
指数计算引擎
实现市值加权指数计算逻辑

T040-T043: 指数计算和历史数据生成
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from .db_manager_sqlite import get_db_manager

logger = logging.getLogger(__name__)


class IndexCalculator:
    """指数计算器基类"""
    
    def __init__(self, index_code: str):
        self.index_code = index_code
        self.db = get_db_manager()
        self._load_index_info()
    
    def _load_index_info(self):
        """加载指数基本信息"""
        query = """
            SELECT code, name, base_point, index_type, calculation_method
            FROM indices
            WHERE code = ?
        """
        result = self.db.execute_query(query, (self.index_code,), fetch_one=True)
        
        if not result:
            raise ValueError(f"Index {self.index_code} not found")
        
        self.name = result['name']
        self.base_point = result['base_point']
        self.index_type = result['index_type']
        self.calculation_method = result['calculation_method']
    
    def get_constituents(self) -> List[Dict]:
        """获取指数成分股及权重"""
        query = """
            SELECT 
                ic.stock_symbol,
                ic.weight,
                ic.rank,
                s.name as stock_name,
                s.current_price
            FROM index_constituents ic
            JOIN stocks s ON ic.stock_symbol = s.symbol
            WHERE ic.index_code = ? AND ic.is_active = 1
            ORDER BY ic.rank
        """
        return self.db.execute_query(query, (self.index_code,))
    
    def calculate_index_value(self, price_data: Dict[str, float] = None) -> float:
        """
        计算指数点位
        
        Args:
            price_data: 股票代码到价格的映射，如果为None则使用当前价格
        
        Returns:
            指数点位
        """
        constituents = self.get_constituents()
        
        if not constituents:
            logger.warning(f"No constituents found for index {self.index_code}")
            return self.base_point
        
        # 计算加权价格总和
        weighted_sum = 0.0
        total_weight = 0.0
        
        for constituent in constituents:
            symbol = constituent['stock_symbol']
            weight = constituent['weight']
            
            # 获取价格
            if price_data and symbol in price_data:
                price = price_data[symbol]
            else:
                price = constituent['current_price']
            
            weighted_sum += price * weight
            total_weight += weight
        
        # 归一化权重
        if total_weight > 0:
            normalized_value = weighted_sum / total_weight
        else:
            normalized_value = 0
        
        # 指数点位 = 加权价格 / 除数 × 基点
        # 简化计算：假设除数已经包含在基点中
        # 这里我们使用基点作为参考，实际值按比例调整
        index_value = normalized_value * 10  # 简化的比例因子
        
        return round(index_value, 2)
    
    def calculate_index_from_historical_prices(
        self, 
        timestamp: int,
        datetime_str: str
    ) -> Optional[Dict]:
        """
        根据历史价格计算指数值
        
        Args:
            timestamp: Unix时间戳
            datetime_str: 日期时间字符串
        
        Returns:
            包含OHLC的字典，如果数据不足则返回None
        """
        constituents = self.get_constituents()
        
        if not constituents:
            return None
        
        # 获取所有成分股在该时间点的价格数据
        symbols = [c['stock_symbol'] for c in constituents]
        placeholders = ','.join(['?' for _ in symbols])
        
        query = f"""
            SELECT target_code, open, high, low, close
            FROM price_data
            WHERE target_type = 'STOCK'
                AND target_code IN ({placeholders})
                AND timestamp = ?
        """
        
        stock_prices = self.db.execute_query(
            query, 
            tuple(symbols) + (timestamp,)
        )
        
        # 检查是否所有成分股都有数据
        if len(stock_prices) < len(symbols) * 0.8:  # 至少80%的成分股有数据
            logger.warning(
                f"Insufficient data for index {self.index_code} at {datetime_str}: "
                f"got {len(stock_prices)}/{len(symbols)} stocks"
            )
            return None
        
        # 创建价格映射
        price_map = {
            row['target_code']: {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            }
            for row in stock_prices
        }
        
        # 计算OHLC
        ohlc = {
            'open': 0.0,
            'high': 0.0,
            'low': 0.0,
            'close': 0.0
        }
        
        for price_type in ['open', 'high', 'low', 'close']:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for constituent in constituents:
                symbol = constituent['stock_symbol']
                weight = constituent['weight']
                
                if symbol in price_map:
                    price = price_map[symbol][price_type]
                    weighted_sum += price * weight
                    total_weight += weight
            
            if total_weight > 0:
                ohlc[price_type] = round((weighted_sum / total_weight) * 10, 2)
        
        return {
            'target_type': 'INDEX',
            'target_code': self.index_code,
            'timestamp': timestamp,
            'datetime': datetime_str,
            'open': ohlc['open'],
            'high': ohlc['high'],
            'low': ohlc['low'],
            'close': ohlc['close'],
            'volume': 0,  # 指数没有成交量
            'turnover': 0.0,
            'change_pct': 0.0  # 稍后计算
        }
    
    def generate_historical_klines(self, days: int = 90) -> int:
        """
        生成指数的历史K线数据
        
        Args:
            days: 生成天数
        
        Returns:
            生成的K线数量
        """
        logger.info(f"Generating {days} days of historical K-lines for {self.index_code}")
        
        # 获取股票K线的时间范围
        query = """
            SELECT DISTINCT timestamp, datetime
            FROM price_data
            WHERE target_type = 'STOCK'
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        timestamps = self.db.execute_query(query, (days,))
        
        if not timestamps:
            logger.warning("No stock price data found")
            return 0
        
        # 反转顺序，从旧到新
        timestamps.reverse()
        
        # 计算每个时间点的指数值
        klines = []
        previous_close = None
        
        for ts_row in timestamps:
            timestamp = ts_row['timestamp']
            datetime_str = ts_row['datetime']
            
            kline = self.calculate_index_from_historical_prices(
                timestamp, 
                datetime_str
            )
            
            if kline:
                # 计算涨跌幅
                if previous_close:
                    change_pct = ((kline['close'] - previous_close) / previous_close) * 100
                    kline['change_pct'] = round(change_pct, 2)
                
                klines.append(kline)
                previous_close = kline['close']
        
        # 批量插入数据库
        if klines:
            # 先删除已有数据
            delete_query = """
                DELETE FROM price_data 
                WHERE target_type = 'INDEX' AND target_code = ?
            """
            self.db.execute_update(delete_query, (self.index_code,))
            
            # 插入新数据
            insert_query = """
                INSERT INTO price_data 
                (target_type, target_code, timestamp, datetime, 
                 open, high, low, close, volume, turnover, change_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for kline in klines:
                self.db.execute_update(
                    insert_query,
                    (
                        kline['target_type'],
                        kline['target_code'],
                        kline['timestamp'],
                        kline['datetime'],
                        kline['open'],
                        kline['high'],
                        kline['low'],
                        kline['close'],
                        kline['volume'],
                        kline['turnover'],
                        kline['change_pct']
                    )
                )
            
            # 更新指数表的当前值
            latest_kline = klines[-1]
            update_index_query = """
                UPDATE indices
                SET current_value = ?,
                    previous_close = ?,
                    change_value = ?,
                    change_pct = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            """
            
            previous = klines[-2]['close'] if len(klines) > 1 else latest_kline['close']
            change_value = latest_kline['close'] - previous
            change_pct = ((latest_kline['close'] - previous) / previous * 100) if previous > 0 else 0
            
            self.db.execute_update(
                update_index_query,
                (
                    latest_kline['close'],
                    previous,
                    round(change_value, 2),
                    round(change_pct, 2),
                    self.index_code
                )
            )
            
            logger.info(
                f"Generated {len(klines)} K-lines for {self.index_code}, "
                f"current value: {latest_kline['close']:.2f}"
            )
        
        return len(klines)
    
    def update_current_value(self):
        """更新指数当前值"""
        current_value = self.calculate_index_value()
        
        # 获取昨日收盘价
        query = """
            SELECT close as previous_close
            FROM price_data
            WHERE target_type = 'INDEX' AND target_code = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        result = self.db.execute_query(query, (self.index_code,), fetch_one=True)
        previous_close = result['previous_close'] if result else current_value
        
        # 计算涨跌
        change_value = current_value - previous_close
        change_pct = (change_value / previous_close * 100) if previous_close > 0 else 0
        
        # 更新数据库
        update_query = """
            UPDATE indices
            SET current_value = ?,
                previous_close = ?,
                change_value = ?,
                change_pct = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE code = ?
        """
        
        self.db.execute_update(
            update_query,
            (
                current_value,
                previous_close,
                round(change_value, 2),
                round(change_pct, 2),
                self.index_code
            )
        )
        
        return current_value


def generate_all_indices_historical_data(days: int = 90):
    """
    为所有核心指数生成历史数据
    
    Args:
        days: 生成天数
    """
    core_indices = ['HAPPY300', 'HAPPY50', 'GROW100']
    
    total_klines = 0
    for index_code in core_indices:
        try:
            calculator = IndexCalculator(index_code)
            count = calculator.generate_historical_klines(days)
            total_klines += count
            print(f"✅ {index_code}: 生成 {count} 条K线")
        except Exception as e:
            print(f"❌ {index_code}: 生成失败 - {e}")
            logger.error(f"Failed to generate data for {index_code}", exc_info=True)
    
    print(f"\n📊 总计生成 {total_klines} 条指数K线数据")
    return total_klines


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 生成历史数据
    generate_all_indices_historical_data(90)
