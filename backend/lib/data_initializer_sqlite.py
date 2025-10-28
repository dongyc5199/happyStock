"""
Data Initializer for Virtual A-Share Market (SQLite Version)
虚拟A股市场数据初始化脚本 - SQLite版本
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Tuple
from pathlib import Path
import numpy as np

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 板块Beta映射
SECTOR_BETA_MAP = {
    'TECH': Decimal('1.25'),
    'FIN': Decimal('0.75'),
    'CONS': Decimal('0.85'),
    'NEV': Decimal('1.40'),
    'HEALTH': Decimal('0.90'),
    'IND': Decimal('1.05'),
    'REAL': Decimal('1.15'),
    'ENERGY': Decimal('0.95'),
    'MATER': Decimal('1.10'),
    'UTIL': Decimal('0.65'),
}


def get_market_cap_tier(market_cap: int) -> str:
    """根据市值确定市值分档"""
    market_cap_billion = market_cap / 100000000  # 转换为亿元
    if market_cap_billion >= 1000:
        return '超大盘'
    elif market_cap_billion >= 300:
        return '大盘'
    elif market_cap_billion >= 100:
        return '中盘'
    elif market_cap_billion >= 50:
        return '小盘'
    else:
        return '微盘'


# 配置常量（从data_initializer.py复制）
HISTORY_DAYS = 90
BASE_DATE = datetime(2024, 1, 1, 9, 30, 0)


# 股票定义（从data_initializer.py复制）
STOCK_DEFINITIONS = {
    'TECH': [
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
    'FIN': [
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
    'CONS': [
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
    'NEV': [
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
    'HEALTH': [
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
    'IND': [
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
    'REAL': [
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
    'ENERGY': [
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
    'MATER': [
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
    'UTIL': [
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


def create_stock_data(sector_code, symbol, name, market_cap, beta, volatility, initial_price=100.0):
    """创建股票数据（简化版本，不使用dataclass）"""
    outstanding_shares = int(market_cap / initial_price)
    market_cap_tier = get_market_cap_tier(market_cap)

    stock = {
        'symbol': symbol,
        'name': name,
        'sector_code': sector_code,
        'current_price': Decimal(str(initial_price)),
        'previous_close': Decimal(str(initial_price)),
        'change_value': Decimal('0'),
        'change_pct': Decimal('0'),
        'volume': 0,
        'turnover': Decimal('0'),
        'is_active': True
    }

    metadata = {
        'symbol': symbol,
        'market_cap': market_cap,
        'market_cap_tier': market_cap_tier,
        'beta': Decimal(str(beta)),
        'volatility': Decimal(str(volatility)),
        'outstanding_shares': outstanding_shares,
        'listing_date': BASE_DATE.date(),
        'is_happy300': False,
        'weight_in_happy300': None
    }

    return stock, metadata


def generate_price_with_gbm(initial_price, beta, sector_beta, market_return, volatility, dt=1.0):
    """GBM价格生成算法"""
    market_drift = 0.30 * market_return * beta * sector_beta
    sector_return = np.random.normal(0, 0.01)
    sector_drift = 0.30 * sector_return * sector_beta
    individual_drift = 0.40 * np.random.normal(0, volatility)
    total_drift = market_drift + sector_drift + individual_drift
    shock = volatility * np.sqrt(dt) * np.random.normal(0, 1)
    new_price = initial_price * np.exp(total_drift + shock)
    return new_price


def generate_ohlc_from_close(open_price, close_price, volatility):
    """生成OHLC"""
    base_high = max(open_price, close_price)
    high = base_high * (1 + abs(np.random.normal(0, volatility * 0.5)))
    base_low = min(open_price, close_price)
    low = base_low * (1 - abs(np.random.normal(0, volatility * 0.5)))
    low = min(low, base_low)
    high = max(high, base_high)
    return high, low


# SQLite数据库路径
DB_PATH = Path(__file__).parent.parent / "virtual_market.db"


def get_sqlite_connection():
    """获取SQLite连接"""
    return sqlite3.connect(str(DB_PATH))


def insert_stocks_to_db():
    """插入所有106只股票到SQLite数据库"""
    print("\n[*] Inserting 106 stocks into SQLite database...")

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    total_inserted = 0

    try:
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
                cursor.execute("""
                    INSERT OR IGNORE INTO stocks (symbol, name, sector_code, current_price, previous_close,
                                                  change_value, change_pct, volume, turnover, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock['symbol'], stock['name'], stock['sector_code'],
                    float(stock['current_price']), float(stock['previous_close']),
                    float(stock['change_value']), float(stock['change_pct']),
                    stock['volume'], float(stock['turnover']), 1 if stock['is_active'] else 0
                ))

                # 插入stock_metadata表
                cursor.execute("""
                    INSERT OR IGNORE INTO stock_metadata (symbol, market_cap, market_cap_tier, beta, volatility,
                                                         outstanding_shares, listing_date, is_happy300, weight_in_happy300)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata['symbol'], metadata['market_cap'], metadata['market_cap_tier'],
                    float(metadata['beta']), float(metadata['volatility']),
                    metadata['outstanding_shares'], metadata['listing_date'].isoformat() if metadata['listing_date'] else None,
                    1 if metadata['is_happy300'] else 0, float(metadata['weight_in_happy300']) if metadata['weight_in_happy300'] else None
                ))

                total_inserted += 1

                if total_inserted % 10 == 0:
                    print(f"  [+] Inserted {total_inserted} stocks...")

        conn.commit()
        print(f"\n[+] Successfully inserted {total_inserted} stocks!")

    except Exception as e:
        conn.rollback()
        print(f"[-] Error inserting stocks: {e}")
        raise
    finally:
        conn.close()

    return total_inserted


def generate_historical_klines(days: int = HISTORY_DAYS):
    """生成历史K线数据 (SQLite版本)"""
    print(f"\n[*] Generating {days} days of historical K-line data...")

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    try:
        # 获取所有股票
        cursor.execute("""
            SELECT s.symbol, s.name, s.sector_code, s.current_price,
                   sm.beta, sm.volatility, sm.market_cap
            FROM stocks s
            JOIN stock_metadata sm ON s.symbol = sm.symbol
            WHERE s.is_active = 1
            ORDER BY s.symbol
        """)
        stocks = cursor.fetchall()

        print(f"[*] Found {len(stocks)} active stocks")

        # 模拟市场状态（横盘市场）
        daily_market_return = 0.0

        total_klines = 0
        batch_size = 1000
        kline_batch = []

        # 遍历每一天
        for day_offset in range(days):
            current_date = BASE_DATE + timedelta(days=day_offset)

            # 跳过周末
            if current_date.weekday() >= 5:
                continue

            # 生成当天的市场整体收益率
            day_market_return = np.random.normal(daily_market_return, 0.005)

            # 为每只股票生成当天的K线
            for stock in stocks:
                symbol, name, sector_code, current_price, beta, volatility, market_cap = stock

                # 获取板块Beta
                sector_beta = float(SECTOR_BETA_MAP.get(sector_code, Decimal('1.0')))

                # 生成开盘价
                if day_offset == 0:
                    open_price = float(current_price)
                else:
                    gap = np.random.normal(0, 0.002)
                    open_price = float(current_price) * (1 + gap)

                # 使用GBM生成收盘价
                close_price = generate_price_with_gbm(
                    open_price, beta, sector_beta, day_market_return, volatility, dt=1.0
                )

                # 生成最高价和最低价
                high, low = generate_ohlc_from_close(open_price, close_price, volatility)

                # 生成成交量
                market_cap_billion = market_cap / 100_0000_0000
                amplitude = abs((high - low) / open_price)
                base_volume = int(market_cap_billion * 1000000 * (1 + amplitude * 10))
                volume = int(np.random.uniform(base_volume * 0.5, base_volume * 1.5))

                # 成交额
                avg_price = (open_price + close_price + high + low) / 4
                turnover = volume * avg_price

                # 涨跌幅
                change_pct = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0

                # 时间戳
                kline_datetime = current_date.replace(hour=15, minute=0, second=0)
                timestamp = int(kline_datetime.timestamp() * 1000)

                # 添加到批量插入列表
                kline_batch.append((
                    'STOCK', symbol, timestamp, kline_datetime.isoformat(),
                    open_price, close_price, high, low,
                    volume, turnover, change_pct
                ))

                # 更新当前价格
                current_price = close_price

                # 批量插入
                if len(kline_batch) >= batch_size:
                    cursor.executemany("""
                        INSERT OR IGNORE INTO price_data (target_type, target_code, timestamp, datetime,
                                                         open, close, high, low, volume, turnover, change_pct)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, kline_batch)
                    conn.commit()
                    total_klines += len(kline_batch)
                    kline_batch = []
                    print(f"  [+] Generated {total_klines} K-lines...")

        # 插入剩余数据
        if kline_batch:
            cursor.executemany("""
                INSERT OR IGNORE INTO price_data (target_type, target_code, timestamp, datetime,
                                                 open, close, high, low, volume, turnover, change_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, kline_batch)
            conn.commit()
            total_klines += len(kline_batch)

        print(f"\n[+] Successfully generated {total_klines} K-line records!")

    except Exception as e:
        conn.rollback()
        print(f"[-] Error generating K-lines: {e}")
        raise
    finally:
        conn.close()

    return total_klines


if __name__ == "__main__":
    print("=" * 70)
    print("A-Share Virtual Market Data Initialization (SQLite)")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"[-] Database not found: {DB_PATH}")
        print("[!] Please run 'python -m lib.db_setup_sqlite' first")
        sys.exit(1)

    try:
        # Step 1: 插入106只股票
        insert_stocks_to_db()

        # Step 2: 生成历史K线数据
        print("\n" + "=" * 70)
        generate_historical_klines(days=HISTORY_DAYS)

        print("\n" + "=" * 70)
        print("[+] Data initialization completed!")
        print(f"[*] Generated data: 106 stocks × {HISTORY_DAYS} days")
        print(f"[*] Database: {DB_PATH}")
        print("[*] Next step: Start backend server and test APIs")
        print("=" * 70)

    except Exception as e:
        print(f"\n[-] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
