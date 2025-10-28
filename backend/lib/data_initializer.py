"""
Data Initializer for Virtual A-Share Market
虚拟A股市场数据初始化脚本

功能：
1. 插入106只股票的基本信息和元数据
2. 建立指数成分股关系
3. 生成90天的历史K线数据（分钟级）
"""
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple
import numpy as np

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db_manager import get_db_manager
from models.stock import Stock, StockMetadata, get_market_cap_tier
from models.market import SECTOR_BETA_MAP


# ============================================================================
# 配置常量
# ============================================================================

HISTORY_DAYS = 90  # 历史数据天数
TRADING_HOURS_PER_DAY = 4  # 每天交易4小时 (9:30-11:30, 13:00-15:00)
MINUTES_PER_DAY = TRADING_HOURS_PER_DAY * 60  # 每天240分钟
BASE_DATE = datetime(2024, 1, 1, 9, 30, 0)  # 基准日期


# ============================================================================
# 106只股票定义
# ============================================================================

STOCK_DEFINITIONS = {
    'TECH': [  # 科技板块 (11只)
        ('600001', '科技龙头', 500_0000_0000, 1.30, 0.035),
        ('600002', '云计算王', 300_0000_0000, 1.40, 0.040),
        ('600003', '芯片制造', 250_0000_0000, 1.50, 0.045),
        ('600004', '人工智能', 200_0000_0000, 1.35, 0.038),
        ('600005', '软件服务', 150_0000_0000, 1.25, 0.032),
        ('600006', '互联网+', 180_0000_0000, 1.28, 0.036),
        ('600007', '大数据', 120_0000_0000, 1.32, 0.037),
        ('600008', '网络安全', 100_0000_0000, 1.22, 0.033),
        ('600009', '5G通信', 90_0000_0000, 1.27, 0.035),
        ('600010', '物联网', 80_0000_0000, 1.24, 0.034),
        ('600011', '区块链', 70_0000_0000, 1.45, 0.042),
    ],
    'FIN': [  # 金融板块 (11只)
        ('601318', '平安保险', 2000_0000_0000, 0.72, 0.022),
        ('601398', '工商银行', 1800_0000_0000, 0.68, 0.020),
        ('601939', '建设银行', 1600_0000_0000, 0.70, 0.021),
        ('601288', '农业银行', 1400_0000_0000, 0.69, 0.020),
        ('601988', '中国银行', 1200_0000_0000, 0.71, 0.021),
        ('600036', '招商银行', 1000_0000_0000, 0.75, 0.023),
        ('600016', '民生银行', 500_0000_0000, 0.78, 0.025),
        ('600030', '中信证券', 400_0000_0000, 0.80, 0.026),
        ('601688', '华泰证券', 350_0000_0000, 0.82, 0.027),
        ('600999', '招商证券', 300_0000_0000, 0.79, 0.026),
        ('601601', '太平洋保险', 250_0000_0000, 0.76, 0.024),
    ],
    'CONS': [  # 消费板块 (11只)
        ('600519', '贵州茅台', 2500_0000_0000, 0.82, 0.025),
        ('000858', '五粮液', 800_0000_0000, 0.88, 0.027),
        ('000568', '泸州老窖', 400_0000_0000, 0.90, 0.028),
        ('600887', '伊利股份', 350_0000_0000, 0.85, 0.026),
        ('000333', '美的集团', 600_0000_0000, 0.87, 0.027),
        ('000651', '格力电器', 500_0000_0000, 0.84, 0.026),
        ('002304', '洋河股份', 300_0000_0000, 0.89, 0.028),
        ('600809', '山西汾酒', 350_0000_0000, 0.91, 0.029),
        ('603288', '海天味业', 280_0000_0000, 0.83, 0.025),
        ('600276', '恒瑞医药', 400_0000_0000, 0.86, 0.026),
        ('000596', '古井贡酒', 200_0000_0000, 0.92, 0.030),
    ],
    'NEV': [  # 新能源板块 (10只)
        ('002594', '比亚迪', 800_0000_0000, 1.55, 0.050),
        ('300750', '宁德时代', 1200_0000_0000, 1.60, 0.052),
        ('601012', '隆基绿能', 400_0000_0000, 1.45, 0.047),
        ('688599', '天合光能', 300_0000_0000, 1.50, 0.048),
        ('002129', '中环股份', 250_0000_0000, 1.42, 0.046),
        ('600438', '通威股份', 350_0000_0000, 1.48, 0.047),
        ('300274', '阳光电源', 280_0000_0000, 1.52, 0.049),
        ('002459', '晶澳科技', 220_0000_0000, 1.46, 0.046),
        ('688005', '容百科技', 180_0000_0000, 1.58, 0.051),
        ('300014', '亿纬锂能', 300_0000_0000, 1.54, 0.050),
    ],
    'HEALTH': [  # 医药板块 (11只)
        ('600276', '恒瑞医药', 500_0000_0000, 0.88, 0.028),
        ('300015', '爱尔眼科', 400_0000_0000, 0.92, 0.030),
        ('000661', '长春高新', 350_0000_0000, 0.95, 0.031),
        ('300760', '迈瑞医疗', 600_0000_0000, 0.90, 0.029),
        ('002821', '凯莱英', 200_0000_0000, 0.93, 0.030),
        ('603259', '药明康德', 450_0000_0000, 0.91, 0.029),
        ('300142', '沃森生物', 180_0000_0000, 0.96, 0.032),
        ('300347', '泰格医药', 250_0000_0000, 0.94, 0.031),
        ('688301', '奕瑞科技', 150_0000_0000, 0.97, 0.032),
        ('688513', '苑东生物', 120_0000_0000, 0.98, 0.033),
        ('603882', '金域医学', 160_0000_0000, 0.89, 0.028),
    ],
    'IND': [  # 工业板块 (10只)
        ('601766', '中国中车', 600_0000_0000, 1.08, 0.032),
        ('600031', '三一重工', 500_0000_0000, 1.10, 0.033),
        ('000333', '美的集团', 700_0000_0000, 1.05, 0.031),
        ('002415', '海康威视', 550_0000_0000, 1.07, 0.032),
        ('601601', '中国太保', 400_0000_0000, 1.02, 0.030),
        ('600585', '海螺水泥', 450_0000_0000, 1.06, 0.031),
        ('002236', '大华股份', 300_0000_0000, 1.09, 0.033),
        ('600150', '中国船舶', 350_0000_0000, 1.12, 0.034),
        ('601919', '中远海控', 280_0000_0000, 1.11, 0.033),
        ('600406', '国电南瑞', 320_0000_0000, 1.04, 0.031),
    ],
    'REAL': [  # 地产板块 (10只)
        ('000002', '万科A', 800_0000_0000, 1.20, 0.038),
        ('600048', '保利发展', 700_0000_0000, 1.18, 0.037),
        ('001979', '招商蛇口', 500_0000_0000, 1.15, 0.036),
        ('000656', '金科股份', 200_0000_0000, 1.25, 0.040),
        ('600340', '华夏幸福', 150_0000_0000, 1.30, 0.042),
        ('600606', '绿地控股', 300_0000_0000, 1.22, 0.038),
        ('600383', '金地集团', 250_0000_0000, 1.17, 0.037),
        ('001914', '招商积余', 180_0000_0000, 1.12, 0.035),
        ('600895', '张江高科', 160_0000_0000, 1.10, 0.034),
        ('600663', '陆家嘴', 400_0000_0000, 1.14, 0.036),
    ],
    'ENERGY': [  # 能源板块 (11只)
        ('601857', '中国石油', 1500_0000_0000, 0.92, 0.028),
        ('600028', '中国石化', 1300_0000_0000, 0.90, 0.027),
        ('601088', '中国神华', 600_0000_0000, 0.95, 0.029),
        ('600011', '华能国际', 400_0000_0000, 0.93, 0.028),
        ('600019', '宝钢股份', 500_0000_0000, 0.98, 0.030),
        ('601225', '陕西煤业', 350_0000_0000, 0.96, 0.029),
        ('601898', '中煤能源', 300_0000_0000, 0.94, 0.028),
        ('600188', '兖矿能源', 280_0000_0000, 0.97, 0.029),
        ('601666', '平煤股份', 200_0000_0000, 0.99, 0.030),
        ('600123', '兰花科创', 150_0000_0000, 1.00, 0.031),
        ('600395', '盘江股份', 180_0000_0000, 0.95, 0.029),
    ],
    'MATER': [  # 材料板块 (10只)
        ('600019', '宝钢股份', 800_0000_0000, 1.15, 0.035),
        ('000709', '河钢股份', 400_0000_0000, 1.18, 0.036),
        ('600362', '江西铜业', 350_0000_0000, 1.20, 0.037),
        ('600219', '南山铝业', 300_0000_0000, 1.12, 0.034),
        ('002466', '天齐锂业', 500_0000_0000, 1.25, 0.039),
        ('002460', '赣锋锂业', 450_0000_0000, 1.22, 0.038),
        ('600111', '北方稀土', 280_0000_0000, 1.16, 0.036),
        ('600489', '中金黄金', 200_0000_0000, 1.10, 0.033),
        ('002756', '永兴材料', 180_0000_0000, 1.13, 0.034),
        ('600547', '山东黄金', 250_0000_0000, 1.08, 0.032),
    ],
    'UTIL': [  # 公用事业板块 (11只)
        ('600900', '长江电力', 1000_0000_0000, 0.62, 0.018),
        ('600011', '华能国际', 500_0000_0000, 0.68, 0.020),
        ('600795', '国电电力', 400_0000_0000, 0.65, 0.019),
        ('600886', '国投电力', 350_0000_0000, 0.66, 0.019),
        ('600021', '上海电力', 300_0000_0000, 0.64, 0.019),
        ('600027', '华电国际', 280_0000_0000, 0.67, 0.020),
        ('601985', '中国核电', 450_0000_0000, 0.63, 0.018),
        ('600023', '浙能电力', 320_0000_0000, 0.65, 0.019),
        ('600674', '川投能源', 250_0000_0000, 0.66, 0.019),
        ('600726', '华电能源', 180_0000_0000, 0.69, 0.021),
        ('600101', '明星电力', 150_0000_0000, 0.70, 0.021),
    ],
}


def create_stock_data(sector_code: str, symbol: str, name: str, market_cap: int,
                      beta: float, volatility: float, initial_price: float = 100.0) -> Tuple[Stock, StockMetadata]:
    """
    创建股票基本信息和元数据

    Args:
        sector_code: 板块代码
        symbol: 股票代码
        name: 股票名称
        market_cap: 市值(元)
        beta: Beta系数
        volatility: 波动率
        initial_price: 初始价格

    Returns:
        (Stock, StockMetadata) 元组
    """
    # 计算流通股本
    outstanding_shares = int(market_cap / initial_price)

    # 确定市值分档
    market_cap_tier = get_market_cap_tier(market_cap)

    # 创建Stock对象
    stock = Stock(
        symbol=symbol,
        name=name,
        sector_code=sector_code,
        current_price=Decimal(str(initial_price)),
        previous_close=Decimal(str(initial_price)),
        change_value=Decimal('0'),
        change_pct=Decimal('0'),
        volume=0,
        turnover=Decimal('0'),
        is_active=True
    )

    # 创建StockMetadata对象
    metadata = StockMetadata(
        symbol=symbol,
        market_cap=market_cap,
        market_cap_tier=market_cap_tier,
        beta=Decimal(str(beta)),
        volatility=Decimal(str(volatility)),
        outstanding_shares=outstanding_shares,
        listing_date=BASE_DATE.date(),
        is_happy300=False,  # 稍后设置
        weight_in_happy300=None
    )

    return stock, metadata


def insert_stocks_to_db(db_manager):
    """插入所有106只股票到数据库"""
    print("\n[*] Inserting 106 stocks into database...")

    total_inserted = 0

    for sector_code, stocks in STOCK_DEFINITIONS.items():
        print(f"\n[*] Processing sector: {sector_code} ({len(stocks)} stocks)")

        for symbol, name, market_cap, beta, volatility in stocks:
            # 根据市值确定初始价格
            if market_cap >= 100_0000_0000:  # >= 100亿
                initial_price = np.random.uniform(50, 200)
            elif market_cap >= 30_0000_0000:  # 30-100亿
                initial_price = np.random.uniform(20, 80)
            else:  # < 30亿
                initial_price = np.random.uniform(10, 40)

            stock, metadata = create_stock_data(
                sector_code, symbol, name, market_cap, beta, volatility, initial_price
            )

            # 插入stocks表
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO stocks (symbol, name, sector_code, current_price, previous_close,
                                      change_value, change_pct, volume, turnover, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO NOTHING
                """, (
                    stock.symbol, stock.name, stock.sector_code,
                    float(stock.current_price), float(stock.previous_close),
                    float(stock.change_value), float(stock.change_pct),
                    stock.volume, float(stock.turnover), stock.is_active
                ))

                # 插入stock_metadata表
                cursor.execute("""
                    INSERT INTO stock_metadata (symbol, market_cap, market_cap_tier, beta, volatility,
                                               outstanding_shares, listing_date, is_happy300, weight_in_happy300)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO NOTHING
                """, (
                    metadata.symbol, metadata.market_cap, metadata.market_cap_tier,
                    float(metadata.beta), float(metadata.volatility),
                    metadata.outstanding_shares, metadata.listing_date,
                    metadata.is_happy300, metadata.weight_in_happy300
                ))

            total_inserted += 1

            if total_inserted % 10 == 0:
                print(f"  [+] Inserted {total_inserted} stocks...")

    print(f"\n[+] Successfully inserted {total_inserted} stocks!")
    return total_inserted


def generate_price_with_gbm(initial_price: float, beta: float, sector_beta: float,
                            market_return: float, volatility: float, dt: float = 1.0) -> float:
    """
    使用Geometric Brownian Motion生成股票价格

    价格影响因子权重：
    - 市场影响: 30% (market_return × beta × sector_beta)
    - 板块影响: 30% (sector_return × sector_beta)
    - 个股影响: 40% (individual random movement)

    Args:
        initial_price: 当前价格
        beta: 个股Beta系数
        sector_beta: 板块Beta系数
        market_return: 市场整体收益率
        volatility: 个股波动率
        dt: 时间步长（天数）

    Returns:
        新价格
    """
    # 市场影响 (30%)
    market_drift = 0.30 * market_return * beta * sector_beta

    # 板块影响 (30%) - 板块自身波动
    sector_return = np.random.normal(0, 0.01)  # 板块日均波动±1%
    sector_drift = 0.30 * sector_return * sector_beta

    # 个股影响 (40%) - 个股特有波动
    individual_drift = 0.40 * np.random.normal(0, volatility)

    # 总漂移
    total_drift = market_drift + sector_drift + individual_drift

    # GBM公式: S(t+dt) = S(t) * exp((μ - 0.5σ²)dt + σ√dt * Z)
    # 简化版本（已包含漂移）
    shock = volatility * np.sqrt(dt) * np.random.normal(0, 1)
    new_price = initial_price * np.exp(total_drift + shock)

    return new_price


def generate_ohlc_from_close(open_price: float, close_price: float, volatility: float) -> Tuple[float, float]:
    """
    根据开盘价和收盘价生成最高价和最低价

    Args:
        open_price: 开盘价
        close_price: 收盘价
        volatility: 波动率

    Returns:
        (high, low) 元组
    """
    # 最高价：在开盘和收盘之间的较大值基础上，加上一个正向波动
    base_high = max(open_price, close_price)
    high = base_high * (1 + abs(np.random.normal(0, volatility * 0.5)))

    # 最低价：在开盘和收盘之间的较小值基础上，减去一个负向波动
    base_low = min(open_price, close_price)
    low = base_low * (1 - abs(np.random.normal(0, volatility * 0.5)))

    # 确保 low <= min(open, close) <= max(open, close) <= high
    low = min(low, base_low)
    high = max(high, base_high)

    return high, low


def generate_historical_klines(db_manager, days: int = HISTORY_DAYS):
    """
    生成历史K线数据

    Args:
        db_manager: 数据库管理器
        days: 生成天数

    生成策略：
    - 为了减少数据量，只生成日级K线，而非分钟级
    - 每天生成1条K线数据
    """
    print(f"\n[*] Generating {days} days of historical K-line data...")

    # 获取所有股票
    with db_manager.get_cursor() as cursor:
        cursor.execute("""
            SELECT s.symbol, s.name, s.sector_code, s.current_price,
                   sm.beta, sm.volatility
            FROM stocks s
            JOIN stock_metadata sm ON s.symbol = sm.symbol
            WHERE s.is_active = TRUE
            ORDER BY s.symbol
        """)
        stocks = cursor.fetchall()

    print(f"[*] Found {len(stocks)} active stocks")

    # 模拟市场状态（简化版：横盘市场，日均趋势0%）
    market_state = 'SIDEWAYS'
    daily_market_return = 0.0  # 横盘市场无明显趋势

    total_klines = 0
    batch_size = 1000
    kline_batch = []

    # 遍历每一天
    for day_offset in range(days):
        current_date = BASE_DATE + timedelta(days=day_offset)

        # 跳过周末
        if current_date.weekday() >= 5:  # 5=周六, 6=周日
            continue

        # 生成当天的市场整体收益率（小幅波动）
        day_market_return = np.random.normal(daily_market_return, 0.005)  # ±0.5%

        # 为每只股票生成当天的K线
        for stock in stocks:
            symbol = stock['symbol']
            sector_code = stock['sector_code']
            current_price = float(stock['current_price'])
            beta = float(stock['beta'])
            volatility = float(stock['volatility'])

            # 获取板块Beta
            sector_beta = float(SECTOR_BETA_MAP.get(sector_code, Decimal('1.0')))

            # 生成开盘价（基于前一天收盘价）
            if day_offset == 0:
                open_price = current_price
            else:
                # 开盘价 = 收盘价 * (1 + 小幅跳空)
                gap = np.random.normal(0, 0.002)  # ±0.2% 跳空
                open_price = current_price * (1 + gap)

            # 使用GBM生成收盘价
            close_price = generate_price_with_gbm(
                open_price, beta, sector_beta, day_market_return, volatility, dt=1.0
            )

            # 生成最高价和最低价
            high, low = generate_ohlc_from_close(open_price, close_price, volatility)

            # 生成成交量（根据市值和振幅）
            market_cap_billion = stock.get('market_cap', 100_0000_0000) / 100_0000_0000
            amplitude = abs((high - low) / open_price)
            base_volume = int(market_cap_billion * 1000000 * (1 + amplitude * 10))
            volume = int(np.random.uniform(base_volume * 0.5, base_volume * 1.5))

            # 成交额 = 成交量 × 平均价格
            avg_price = (open_price + close_price + high + low) / 4
            turnover = volume * avg_price

            # 涨跌幅
            change_pct = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0

            # 时间戳（当天收盘时间 15:00）
            kline_datetime = current_date.replace(hour=15, minute=0, second=0)
            timestamp = int(kline_datetime.timestamp() * 1000)

            # 添加到批量插入列表
            kline_batch.append((
                'STOCK', symbol, timestamp, kline_datetime,
                open_price, close_price, high, low,
                volume, turnover, change_pct
            ))

            # 更新当前价格为收盘价（用于下一天）
            current_price = close_price

            # 批量插入
            if len(kline_batch) >= batch_size:
                insert_kline_batch(db_manager, kline_batch)
                total_klines += len(kline_batch)
                kline_batch = []
                print(f"  [+] Generated {total_klines} K-lines...")

    # 插入剩余数据
    if kline_batch:
        insert_kline_batch(db_manager, kline_batch)
        total_klines += len(kline_batch)

    print(f"\n[+] Successfully generated {total_klines} K-line records!")
    return total_klines


def insert_kline_batch(db_manager, kline_batch: List[Tuple]):
    """批量插入K线数据"""
    with db_manager.get_cursor() as cursor:
        cursor.executemany("""
            INSERT INTO price_data (target_type, target_code, timestamp, datetime,
                                   open, close, high, low, volume, turnover, change_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (target_type, target_code, timestamp) DO NOTHING
        """, kline_batch)


if __name__ == "__main__":
    print("=" * 70)
    print("A-Share Virtual Market Data Initialization")
    print("=" * 70)

    # 初始化数据库连接
    db_manager = get_db_manager()
    db_manager.initialize()

    if not db_manager.health_check():
        print("[-] Database connection failed. Please start PostgreSQL and create database.")
        sys.exit(1)

    try:
        # Step 1: 插入106只股票
        insert_stocks_to_db(db_manager)

        # Step 2: 生成历史K线数据
        print("\n" + "=" * 70)
        generate_historical_klines(db_manager, days=HISTORY_DAYS)

        print("\n" + "=" * 70)
        print("[+] Data initialization completed!")
        print(f"[*] Generated data: 106 stocks × {HISTORY_DAYS} days")
        print("[*] Next step: Start backend server and test APIs")
        print("=" * 70)

    except Exception as e:
        print(f"\n[-] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db_manager.close()
