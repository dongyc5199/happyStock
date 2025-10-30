"""
价格生成器 V2 - 按照《模拟市场价格生成规范（修订版）》实现

核心改进:
1. 统一时间尺度为"日" - 所有参数以日为基准
2. 使用对数收益 - P = P × exp(r) 
3. 相关性用共享随机冲击 - Corr(Z_m, Z_s) = ρ
4. 板块噪声为标准差×√dt
5. 布朗桥近似生成OHLC
"""

from typing import Dict, Optional, Tuple, List
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.db_manager_sqlite import DatabaseManager
from lib.market_state_manager import MarketStateManager


class PriceGeneratorV2:
    """
    价格生成器 V2 - 符合统计规范的实现
    
    公式:
        r_m = μ_m·dt + σ_m_day·√dt·Z_m         (市场层)
        r_s = σ_s_day·√dt·Z_s                   (板块层)  
        r_i = σ_i_day·√dt·Z_i                   (个股层)
        
        最终: r = w_m·β_m·r_m + w_s·β_s·r_s + w_i·r_i
        
        价格: P_new = P_old × exp(r)
    """
    
    # === 常量配置 ===
    TRADING_MINUTES_PER_DAY = 240  # 每个交易日240分钟
    TRADING_DAYS_PER_YEAR = 250    # 每年250个交易日
    
    # 涨跌停限制
    PRICE_LIMIT_PCT = 0.10  # ±10%
    
    # 三层权重
    MARKET_WEIGHT = 0.50   # 市场影响权重 (w_m)
    SECTOR_WEIGHT = 0.30   # 板块影响权重 (w_s)
    INDIVIDUAL_WEIGHT = 0.20  # 个股波动权重 (w_i)
    
    # 市场-板块相关系数
    RHO_MS = 0.75  # 相关系数 ρ_ms
    
    # 年化波动率 (调大以增强视觉效果)
    SIGMA_MARKET_ANNUAL = 0.30   # 30% 市场年化波动 (原18%)
    SIGMA_SECTOR_ANNUAL = 0.40   # 40% 板块年化波动 (原25%)
    SIGMA_INDIVIDUAL_ANNUAL = 0.80  # 80% 个股年化波动 (原50%)
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        market_state_manager: Optional[MarketStateManager] = None,
        steps_per_day: int = 4800,  # 3秒/步: 240分×60秒÷3秒 = 4800步
    ):
        """
        初始化价格生成器
        
        Args:
            db_manager: 数据库管理器
            market_state_manager: 市场状态管理器
            steps_per_day: 每日步数 (决定dt)
        """
        self.db_manager = db_manager or DatabaseManager()
        self.market_state_manager = market_state_manager or MarketStateManager(
            self.db_manager
        )
        
        # 时间步长 (以日为单位)
        self.steps_per_day = steps_per_day
        self.dt = 1.0 / steps_per_day  # dt = 1/4800 ≈ 0.000208 (日)
        
        # 年化 -> 日化转换
        self.sigma_m_day = self.SIGMA_MARKET_ANNUAL / np.sqrt(self.TRADING_DAYS_PER_YEAR)
        self.sigma_s_day = self.SIGMA_SECTOR_ANNUAL / np.sqrt(self.TRADING_DAYS_PER_YEAR)
        self.sigma_i_day = self.SIGMA_INDIVIDUAL_ANNUAL / np.sqrt(self.TRADING_DAYS_PER_YEAR)
        
        # 缓存板块数据
        self._sector_cache: Dict[str, Dict] = {}
        self._load_sectors()
        
        print(f"[PriceGeneratorV2] 初始化完成:")
        print(f"  - 每日步数: {steps_per_day}")
        print(f"  - 时间步长 dt: {self.dt:.6f} 日")
        print(f"  - 市场日化波动: {self.sigma_m_day:.4f}")
        print(f"  - 板块日化波动: {self.sigma_s_day:.4f}")
        print(f"  - 个股日化波动: {self.sigma_i_day:.4f}")
    
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
                    "beta": row[2] if row[2] else 1.0,
                }
            
            print(f"[+] 加载 {len(self._sector_cache)} 个板块到缓存")
        finally:
            conn.close()
    
    def get_sector_beta(self, sector_code: str) -> float:
        """获取板块Beta系数"""
        sector = self._sector_cache.get(sector_code)
        if sector:
            return sector["beta"]
        return 1.0
    
    def generate_correlated_shocks(self) -> Tuple[float, float, float]:
        """
        生成相关的随机冲击
        
        Returns:
            (Z_m, Z_s, Z_i) - 三个标准正态分布随机数
            其中 Corr(Z_m, Z_s) = ρ_ms
        """
        # 生成3个独立的标准正态随机数
        z0, z1, z2 = np.random.normal(0, 1, size=3)
        
        # 市场冲击
        z_m = z0
        
        # 板块冲击 (与市场相关)
        z_s = self.RHO_MS * z0 + np.sqrt(1 - self.RHO_MS**2) * z1
        
        # 个股冲击 (独立)
        z_i = z2
        
        return z_m, z_s, z_i
    
    def generate_log_return(
        self,
        stock_beta: float,
        sector_code: str,
        sector_beta: float,
        mu_m_daily: float,
    ) -> Tuple[float, Dict]:
        """
        生成单步对数收益 (按规范实现)
        
        Args:
            stock_beta: 股票的市场Beta (β_m)
            sector_code: 板块代码
            sector_beta: 股票的板块Beta (β_s)
            mu_m_daily: 市场日均漂移
        
        Returns:
            (对数收益, 调试信息)
        """
        # 1. 生成相关随机冲击
        z_m, z_s, z_i = self.generate_correlated_shocks()
        
        # 2. 市场层对数收益
        r_m = mu_m_daily * self.dt + self.sigma_m_day * np.sqrt(self.dt) * z_m
        
        # 3. 板块层对数收益 (无漂移,纯随机)
        r_s = self.sigma_s_day * np.sqrt(self.dt) * z_s
        
        # 4. 个股层对数收益 (纯随机)
        r_i = self.sigma_i_day * np.sqrt(self.dt) * z_i
        
        # 5. 加权合成
        r_total = (
            self.MARKET_WEIGHT * stock_beta * r_m +
            self.SECTOR_WEIGHT * sector_beta * r_s +
            self.INDIVIDUAL_WEIGHT * r_i
        )
        
        # 调试信息
        debug_info = {
            "r_m": r_m,
            "r_s": r_s,
            "r_i": r_i,
            "r_total": r_total,
            "z_m": z_m,
            "z_s": z_s,
            "z_i": z_i,
        }
        
        return r_total, debug_info
    
    def apply_price_limit(
        self, 
        new_price: float, 
        previous_close: float
    ) -> float:
        """
        应用涨跌停限制
        
        Args:
            new_price: 新价格
            previous_close: 昨收价
        
        Returns:
            限制后的价格
        """
        upper_limit = previous_close * (1 + self.PRICE_LIMIT_PCT)
        lower_limit = previous_close * (1 - self.PRICE_LIMIT_PCT)
        
        return min(max(new_price, lower_limit), upper_limit)
    
    def generate_ohlc_brownian_bridge(
        self,
        open_price: float,
        close_price: float,
        log_return: float,
        previous_close: float,
    ) -> Tuple[float, float]:
        """
        使用布朗桥近似生成High和Low
        
        Args:
            open_price: 开盘价
            close_price: 收盘价 (已限制)
            log_return: 总对数收益
            previous_close: 昨收价
        
        Returns:
            (high, low)
        """
        # 路径点采样: x0=0, x1=u, x2=u+v, x3=R
        # 其中 u,v ~ N(0, σ²)
        
        # 使用合成波动的一个比例作为中间波动
        sigma_bridge = abs(log_return) * 0.5  # 简化估计
        
        u = np.random.normal(0, sigma_bridge)
        v = np.random.normal(0, sigma_bridge)
        
        # 构造路径
        path_points = [
            0,           # x0: 开盘
            u,           # x1: 中间点1
            u + v,       # x2: 中间点2
            log_return,  # x3: 收盘
        ]
        
        # 转换为价格路径
        price_path = [open_price * np.exp(x) for x in path_points]
        
        # 应用涨跌停限制到每个点
        price_path_limited = [
            self.apply_price_limit(p, previous_close) 
            for p in price_path
        ]
        
        # 取最高和最低
        high = max(price_path_limited)
        low = min(price_path_limited)
        
        # 确保 high >= max(open, close) 和 low <= min(open, close)
        high = max(high, open_price, close_price)
        low = min(low, open_price, close_price)
        
        return high, low
    
    def generate_next_price(
        self, 
        stock_symbol: str, 
        verbose: bool = False
    ) -> Optional[Dict]:
        """
        为单只股票生成下一个价格 (V2版本)
        
        Args:
            stock_symbol: 股票代码
            verbose: 是否输出详细信息
        
        Returns:
            包含新价格和OHLC的字典,失败返回None
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # 获取股票信息
            # 注意: stocks表只有基本字段,beta和volatility需要从stock_metadata获取
            cursor.execute(
                """
                SELECT symbol, current_price, previous_close, sector_code
                FROM stocks 
                WHERE symbol = ? AND is_active = 1
                """,
                (stock_symbol,)
            )
            row = cursor.fetchone()
            
            if not row:
                if verbose:
                    print(f"[!] 股票 {stock_symbol} 未找到")
                return None
            
            symbol, current_price, previous_close, sector_code = row
            
            # 尝试从stock_metadata获取beta和volatility
            cursor.execute(
                """
                SELECT beta, volatility
                FROM stock_metadata
                WHERE symbol = ?
                """,
                (stock_symbol,)
            )
            meta_row = cursor.fetchone()
            
            # 设置默认值
            beta = 1.0
            volatility = self.SIGMA_INDIVIDUAL_ANNUAL
            
            if meta_row:
                if meta_row[0] is not None:
                    beta = meta_row[0]
                if meta_row[1] is not None:
                    # 如果数据库有自定义波动率,转换为日化
                    volatility = meta_row[1]
                    sigma_i_day = volatility / np.sqrt(self.TRADING_DAYS_PER_YEAR)
                    self.sigma_i_day = sigma_i_day
            
            # 获取板块Beta
            sector_beta = self.get_sector_beta(sector_code)
            
            # 获取市场趋势
            market_state = self.market_state_manager.get_current_state()
            mu_m_daily = market_state["daily_trend"] if market_state else 0.0
            
            # 生成对数收益
            log_return, debug_info = self.generate_log_return(
                stock_beta=beta,
                sector_code=sector_code,
                sector_beta=sector_beta,
                mu_m_daily=mu_m_daily,
            )
            
            # 使用对数收益更新价格
            new_price_raw = current_price * np.exp(log_return)
            
            # 应用涨跌停限制
            new_price = self.apply_price_limit(new_price_raw, previous_close)
            
            # 防止负价格
            new_price = max(new_price, 0.01)
            
            # 生成OHLC
            open_price = current_price
            close_price = new_price
            
            high, low = self.generate_ohlc_brownian_bridge(
                open_price=open_price,
                close_price=close_price,
                log_return=log_return,
                previous_close=previous_close,
            )
            
            # 计算涨跌
            change_value = close_price - previous_close
            change_pct = (change_value / previous_close) * 100 if previous_close > 0 else 0
            
            # 生成成交量和成交额 (简化模型)
            base_volume = 10000 + np.random.poisson(5000)
            volume_mult = 1.0 + abs(log_return) * 50  # 波动大时成交量增加
            volume = int(base_volume * volume_mult)
            turnover = volume * close_price
            
            result = {
                "symbol": symbol,
                "open": open_price,
                "close": close_price,
                "high": high,
                "low": low,
                "volume": volume,
                "turnover": turnover,
                "previous_close": previous_close,
                "change_value": change_value,
                "change_pct": change_pct,
                "log_return": log_return,
                "capped": new_price != new_price_raw,
            }
            
            if verbose:
                print(f"[{symbol}] {previous_close:.2f} → {close_price:.2f} "
                      f"({change_pct:+.2f}%) log_r={log_return:.4f}")
            
            return result
            
        finally:
            conn.close()


def test_generator():
    """测试价格生成器V2"""
    print("=" * 80)
    print("价格生成器 V2 测试")
    print("=" * 80)
    
    generator = PriceGeneratorV2(steps_per_day=4800)  # 3秒/步
    
    # 测试单只股票
    print("\n测试单只股票价格生成:")
    result = generator.generate_next_price("000002", verbose=True)  # 万科A
    
    if result:
        print(f"\n生成结果:")
        print(f"  开盘: {result['open']:.2f}")
        print(f"  最高: {result['high']:.2f}")
        print(f"  最低: {result['low']:.2f}")
        print(f"  收盘: {result['close']:.2f}")
        print(f"  涨跌: {result['change_value']:+.2f} ({result['change_pct']:+.2f}%)")
        print(f"  成交量: {result['volume']:,}")
        print(f"  对数收益: {result['log_return']:.6f}")
        print(f"  触及涨跌停: {'是' if result['capped'] else '否'}")
    
    # 测试多步价格路径
    print("\n\n测试10步价格路径:")
    prices = [180.0]  # 初始价格
    
    for i in range(10):
        result = generator.generate_next_price("000002")  # 万科A
        if result:
            prices.append(result['close'])
            print(f"步骤 {i+1}: {result['close']:.2f} ({result['change_pct']:+.2f}%)")
    
    print(f"\n价格路径: {[f'{p:.2f}' for p in prices]}")
    
    # 统计检验
    if len(prices) > 1:
        log_returns = [np.log(prices[i]/prices[i-1]) for i in range(1, len(prices))]
        print(f"\n统计量:")
        print(f"  对数收益均值: {np.mean(log_returns):.6f}")
        print(f"  对数收益标准差: {np.std(log_returns):.6f}")
        print(f"  价格变化范围: {min(prices):.2f} ~ {max(prices):.2f}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_generator()
