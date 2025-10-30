"""
三层价格生成引擎 - Phase 5
Three-Layer Price Generation Engine

实现市场联动机制：
1. 市场层面影响 (30%): 大盘趋势 × 股票Beta
2. 板块层面影响 (30%): 板块趋势 × 板块Beta  
3. 个股层面波动 (40%): GBM随机游走

同时实现涨跌停限制（±10%）
"""

from typing import Dict, Optional, Tuple
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.db_manager_sqlite import DatabaseManager
from lib.market_state_manager import MarketStateManager


class ThreeLayerPriceGenerator:
    """三层价格生成引擎"""

    # 涨跌停限制
    PRICE_LIMIT_PCT = 0.10  # ±10%

    # 权重分配
    MARKET_WEIGHT = 0.30  # 市场影响权重
    SECTOR_WEIGHT = 0.30  # 板块影响权重
    INDIVIDUAL_WEIGHT = 0.40  # 个股波动权重

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        market_state_manager: Optional[MarketStateManager] = None,
    ):
        """
        初始化三层价格生成器

        Args:
            db_manager: 数据库管理器
            market_state_manager: 市场状态管理器
        """
        self.db_manager = db_manager or DatabaseManager()
        self.market_state_manager = market_state_manager or MarketStateManager(
            self.db_manager
        )

        # 缓存板块数据
        self._sector_cache: Dict[str, Dict] = {}
        self._load_sectors()

    def _load_sectors(self):
        """加载板块数据到缓存"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, beta FROM sectors")
            rows = cursor.fetchall()

            for row in rows:
                self._sector_cache[row[0]] = {
                    "code": row[0],
                    "name": row[1],
                    "beta": row[2],
                }

            print(f"[+] Loaded {len(self._sector_cache)} sectors into cache")
        finally:
            conn.close()

    def get_sector_beta(self, sector_code: str) -> float:
        """获取板块Beta系数"""
        sector = self._sector_cache.get(sector_code)
        if sector:
            return sector["beta"]
        return 1.0  # 默认Beta=1.0

    def calculate_sector_trend(self, sector_code: str, market_trend: float) -> float:
        """
        计算板块趋势

        板块趋势 = 市场趋势 × 板块Beta + 噪声

        Args:
            sector_code: 板块代码
            market_trend: 市场趋势值 (daily_trend)

        Returns:
            板块趋势值
        """
        sector_beta = self.get_sector_beta(sector_code)

        # 板块跟随市场，但受Beta影响
        sector_base_trend = market_trend * sector_beta

        # 添加板块特有噪声（小幅）
        sector_noise = np.random.normal(0, 0.0005)  # 0.05%标准差

        return sector_base_trend + sector_noise

    def generate_price_change(
        self,
        stock_symbol: str,
        stock_beta: float,
        sector_code: str,
        base_volatility: float,
        previous_price: float,
    ) -> Tuple[float, Dict]:
        """
        生成股票价格变化（三层模型）

        Args:
            stock_symbol: 股票代码
            stock_beta: 股票Beta系数
            sector_code: 所属板块代码
            base_volatility: 基础波动率
            previous_price: 上一周期价格

        Returns:
            (新价格, 调试信息字典)
        """
        # 1. 获取市场趋势
        market_state = self.market_state_manager.get_current_state()
        market_trend = market_state["daily_trend"] if market_state else 0.0

        # 2. 计算板块趋势
        sector_trend = self.calculate_sector_trend(sector_code, market_trend)

        # 3. 计算个股GBM波动
        dt = 1 / (240 * 250)  # 1分钟 / (每天240分钟 × 每年250交易日)
        individual_shock = base_volatility * np.sqrt(dt) * np.random.normal(0, 1)

        # 4. 三层合成
        # 市场影响 = 市场趋势 × 股票Beta × 时间步长 × 市场权重
        market_component = market_trend * stock_beta * dt * self.MARKET_WEIGHT

        # 板块影响 = 板块趋势 × 时间步长 × 板块权重
        sector_component = sector_trend * dt * self.SECTOR_WEIGHT

        # 个股影响 = GBM随机波动 × 个股权重
        individual_component = individual_shock * self.INDIVIDUAL_WEIGHT

        # 总变化率
        total_change_pct = (
            market_component + sector_component + individual_component
        )

        # 5. 应用涨跌停限制
        if total_change_pct > self.PRICE_LIMIT_PCT:
            total_change_pct = self.PRICE_LIMIT_PCT
        elif total_change_pct < -self.PRICE_LIMIT_PCT:
            total_change_pct = -self.PRICE_LIMIT_PCT

        # 6. 计算新价格
        new_price = previous_price * (1 + total_change_pct)
        new_price = max(new_price, 0.01)  # 防止负价格

        # 调试信息
        debug_info = {
            "market_trend": market_trend,
            "sector_trend": sector_trend,
            "market_component": market_component,
            "sector_component": sector_component,
            "individual_component": individual_component,
            "total_change_pct": total_change_pct,
            "capped": abs(total_change_pct) == self.PRICE_LIMIT_PCT,
        }

        return new_price, debug_info

    def generate_next_price(
        self, stock_symbol: str, verbose: bool = False
    ) -> Optional[Dict]:
        """
        为单只股票生成下一个价格

        Args:
            stock_symbol: 股票代码
            verbose: 是否打印详细信息

        Returns:
            包含新价格和OHLC信息的字典，如果股票不存在则返回None
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()

            # 获取股票信息
            cursor.execute(
                """
                SELECT s.symbol, s.current_price, s.sector_code,
                       sm.beta, sm.volatility
                FROM stocks s
                LEFT JOIN stock_metadata sm ON s.symbol = sm.symbol
                WHERE s.symbol = ?
                """,
                (stock_symbol,),
            )
            row = cursor.fetchone()

            if not row:
                print(f"[!] Stock {stock_symbol} not found")
                return None

            symbol, current_price, sector_code, beta, base_volatility = row

            # 使用默认值
            if beta is None:
                beta = 1.0
            if base_volatility is None:
                # 增大默认波动率到50%,让价格变化更明显(原2% → 20% → 50%)
                # 这样在3秒更新频率下,价格变化会非常容易观察到
                # 50%年化波动率 ≈ 每天±3%,每3秒约±0.01~0.05%
                base_volatility = 0.50  # 50% 年化波动率

            # 生成新价格
            new_price, debug_info = self.generate_price_change(
                stock_symbol=symbol,
                stock_beta=beta,
                sector_code=sector_code,
                base_volatility=base_volatility,
                previous_price=current_price,
            )

            # 生成OHLC（简化版，假设1分钟K线）
            # Open = 上一周期Close
            open_price = current_price

            # Close = 新价格
            close_price = new_price

            # High/Low根据波动生成
            volatility_range = abs(new_price - current_price) * 0.5
            high_price = max(open_price, close_price) + abs(
                np.random.normal(0, volatility_range)
            )
            low_price = min(open_price, close_price) - abs(
                np.random.normal(0, volatility_range)
            )

            # 确保OHLC约束
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            low_price = max(low_price, 0.01)

            if verbose:
                print(f"\n[{symbol}] Price Generation:")
                print(f"  Market trend: {debug_info['market_trend']:.4f}")
                print(f"  Sector trend: {debug_info['sector_trend']:.4f}")
                print(f"  Market component: {debug_info['market_component']:.4f}")
                print(f"  Sector component: {debug_info['sector_component']:.4f}")
                print(
                    f"  Individual component: {debug_info['individual_component']:.4f}"
                )
                print(
                    f"  Total change: {debug_info['total_change_pct']*100:.2f}% {'(CAPPED)' if debug_info['capped'] else ''}"
                )
                print(f"  Price: {current_price:.2f} -> {new_price:.2f}")

            return {
                "symbol": symbol,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "previous_close": round(current_price, 2),
                "change_pct": round(debug_info["total_change_pct"] * 100, 2),
                "debug": debug_info if verbose else None,
            }

        finally:
            conn.close()

    def update_stock_price(self, stock_symbol: str) -> bool:
        """
        更新数据库中的股票价格

        Args:
            stock_symbol: 股票代码

        Returns:
            是否成功更新
        """
        result = self.generate_next_price(stock_symbol)
        if not result:
            return False

        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE stocks
                SET current_price = ?,
                    previous_close = ?,
                    change_pct = ?
                WHERE symbol = ?
                """,
                (
                    result["close"],
                    result["previous_close"],
                    result["change_pct"],
                    stock_symbol,
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"[!] Error updating price for {stock_symbol}: {e}")
            return False
        finally:
            conn.close()


def test_three_layer_generator():
    """测试三层价格生成器"""
    print("=== Testing Three-Layer Price Generator ===\n")

    generator = ThreeLayerPriceGenerator()

    # 1. 设置牛市状态
    print("1. Setting BULL market state...")
    generator.market_state_manager.force_bull_market(trend=0.008)

    # 2. 生成几只不同板块的股票价格
    print("\n2. Generating prices for stocks in different sectors:")

    test_stocks = [
        "600000",  # 浦发银行 (金融, beta=0.75)
        "600519",  # 茅台 (消费, beta=0.85)
        "300750",  # 宁德时代 (新能源, beta=1.4)
    ]

    for symbol in test_stocks:
        print(f"\n{'=' * 60}")
        result = generator.generate_next_price(symbol, verbose=True)

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_three_layer_generator()
