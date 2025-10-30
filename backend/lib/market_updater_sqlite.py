"""
Market Data Updater for SQLite
虚拟市场数据更新器 - SQLite版本

功能：
1. 从 price_data 表计算最新的涨跌幅
2. 更新 stocks 表的实时数据（current_price, change_value, change_pct, volume）
3. 支持手动更新和定时更新
"""

import sqlite3
from datetime import datetime
from typing import Optional
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db_manager_sqlite import get_db_manager


class MarketUpdater:
    """市场数据更新器"""

    def __init__(self, db_path: str = 'virtual_market.db'):
        self.db_path = db_path
        self.db_manager = get_db_manager()

    def update_stock_from_klines(self, symbol: str) -> bool:
        """
        从K线数据更新单只股票的实时信息

        Args:
            symbol: 股票代码

        Returns:
            bool: 是否更新成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 获取最近两条K线数据（用于计算涨跌幅）
            cursor.execute("""
                SELECT close, volume, turnover, timestamp
                FROM price_data
                WHERE target_type = 'STOCK' AND target_code = ?
                ORDER BY timestamp DESC
                LIMIT 2
            """, (symbol,))

            klines = cursor.fetchall()

            if len(klines) < 2:
                print(f"[-] {symbol}: 没有足够的K线数据")
                conn.close()
                return False

            # 最新数据
            latest = klines[0]
            previous = klines[1]

            current_price = latest['close']
            previous_close = previous['close']
            volume = latest['volume']
            turnover = latest['turnover']

            # 计算涨跌
            change_value = current_price - previous_close
            change_pct = (change_value / previous_close) * 100 if previous_close > 0 else 0

            # 限制涨跌幅在 ±10% 范围内（符合A股涨跌停限制）
            if change_pct > 10:
                change_pct = 10
                change_value = previous_close * 0.1
            elif change_pct < -10:
                change_pct = -10
                change_value = previous_close * -0.1

            # 更新 stocks 表
            cursor.execute("""
                UPDATE stocks
                SET current_price = ?,
                    previous_close = ?,
                    change_value = ?,
                    change_pct = ?,
                    volume = ?,
                    turnover = ?
                WHERE symbol = ?
            """, (
                current_price,
                previous_close,
                change_value,
                change_pct,
                volume,
                turnover,
                symbol
            ))

            conn.commit()
            conn.close()

            print(f"[+] {symbol}: {current_price:.2f} ({change_pct:+.2f}%) Vol:{volume:,}")
            return True

        except Exception as e:
            print(f"[-] 更新 {symbol} 失败: {e}")
            if conn:
                conn.close()
            return False

    def update_all_stocks(self) -> dict:
        """
        更新所有股票的实时数据

        Returns:
            dict: 更新结果统计
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 获取所有活跃股票
            cursor.execute("SELECT symbol, name FROM stocks WHERE is_active = 1")
            stocks = cursor.fetchall()
            conn.close()

            total = len(stocks)
            success = 0
            failed = 0

            print(f"\n{'='*60}")
            print(f"开始更新 {total} 只股票的实时数据...")
            print(f"{'='*60}\n")

            for stock in stocks:
                if self.update_stock_from_klines(stock['symbol']):
                    success += 1
                else:
                    failed += 1

            result = {
                'total': total,
                'success': success,
                'failed': failed,
                'timestamp': datetime.now().isoformat()
            }

            print(f"\n{'='*60}")
            print(f"更新完成！")
            print(f"成功: {success}/{total}")
            print(f"失败: {failed}/{total}")
            print(f"时间: {result['timestamp']}")
            print(f"{'='*60}\n")

            return result

        except Exception as e:
            print(f"[-] 批量更新失败: {e}")
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'error': str(e)
            }

    def get_market_summary(self) -> dict:
        """
        获取市场概况

        Returns:
            dict: 市场统计数据
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_stocks,
                    SUM(CASE WHEN change_pct > 0 THEN 1 ELSE 0 END) as rising,
                    SUM(CASE WHEN change_pct < 0 THEN 1 ELSE 0 END) as falling,
                    SUM(CASE WHEN change_pct = 0 THEN 1 ELSE 0 END) as unchanged,
                    AVG(change_pct) as avg_change,
                    SUM(volume) as total_volume,
                    SUM(turnover) as total_turnover
                FROM stocks
                WHERE is_active = 1
            """)

            summary = dict(cursor.fetchone())
            conn.close()

            return summary

        except Exception as e:
            print(f"[-] 获取市场概况失败: {e}")
            return {}


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='虚拟市场数据更新器')
    parser.add_argument('--db', type=str, default='virtual_market.db', help='数据库文件路径')
    parser.add_argument('--symbol', type=str, help='更新指定股票（留空则更新全部）')
    parser.add_argument('--summary', action='store_true', help='显示市场概况')

    args = parser.parse_args()

    updater = MarketUpdater(db_path=args.db)

    if args.summary:
        # 显示市场概况
        summary = updater.get_market_summary()
        print("\n=== 市场概况 ===")
        print(f"总股票数: {summary.get('total_stocks', 0)}")
        print(f"上涨: {summary.get('rising', 0)}")
        print(f"下跌: {summary.get('falling', 0)}")
        print(f"平盘: {summary.get('unchanged', 0)}")
        print(f"平均涨跌幅: {summary.get('avg_change', 0):.2f}%")
        print(f"总成交量: {summary.get('total_volume', 0):,}")
        print(f"总成交额: {summary.get('total_turnover', 0):,.2f}")

    elif args.symbol:
        # 更新指定股票
        updater.update_stock_from_klines(args.symbol)

    else:
        # 更新所有股票
        updater.update_all_stocks()


if __name__ == '__main__':
    main()
