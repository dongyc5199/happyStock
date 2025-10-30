"""
配置指数成分股
T036-T039: 配置 HAPPY300, HAPPY50, GROW100 的成分股及权重
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.db_manager_sqlite import get_db_manager

def configure_index_constituents():
    """配置指数成分股"""
    print("=" * 80)
    print("📊 配置指数成分股")
    print("=" * 80)
    print()
    
    db = get_db_manager()
    
    # 1. 获取所有股票及其市值，按市值排序
    print("📈 1. 获取股票市值数据...")
    query = """
        SELECT s.symbol, s.name, s.sector_code, s.current_price,
               sm.market_cap, sm.beta, sm.volatility
        FROM stocks s
        JOIN stock_metadata sm ON s.symbol = sm.symbol
        WHERE s.is_active = 1
        ORDER BY sm.market_cap DESC
    """
    all_stocks = db.execute_query(query)
    print(f"  ✅ 共 {len(all_stocks)} 只活跃股票")
    print()
    
    if len(all_stocks) < 100:
        print(f"  ⚠️  股票数量不足100只，无法配置 HAPPY300")
        return False
    
    # 2. T036: 配置 HAPPY300 (按市值前100只)
    print("📊 2. 配置 HAPPY300 成分股...")
    happy300_stocks = all_stocks[:min(100, len(all_stocks))]
    
    # 计算自由流通市值加权（这里简化为使用 market_cap）
    total_market_cap = sum([s['market_cap'] for s in happy300_stocks])
    
    constituents_h300 = []
    for rank, stock in enumerate(happy300_stocks, 1):
        # 计算原始权重（小数形式，0-1）
        raw_weight = stock['market_cap'] / total_market_cap
        # 应用10%上限（0.1）
        weight = min(raw_weight, 0.10)
        
        constituents_h300.append({
            'index_code': 'H300',
            'stock_symbol': stock['symbol'],
            'weight': weight,
            'rank': rank
        })
    
    # 权重归一化（确保总和为1.0）
    total_weight = sum([c['weight'] for c in constituents_h300])
    for c in constituents_h300:
        c['weight'] = c['weight'] / total_weight
    
    print(f"  ✅ HAPPY300: {len(constituents_h300)} 只成分股")
    print(f"     前5大权重股:")
    for c in constituents_h300[:5]:
        stock = next(s for s in happy300_stocks if s['symbol'] == c['stock_symbol'])
        print(f"       • {c['rank']:3d}. {stock['symbol']} - {stock['name']:12s}: {c['weight']*100:5.2f}% (市值: {stock['market_cap']:.0f}亿)")
    print()
    
    # 3. T037: 配置 HAPPY50 (HAPPY300 中前50只)
    print("📊 3. 配置 HAPPY50 成分股...")
    happy50_stocks = all_stocks[:min(50, len(all_stocks))]
    
    total_market_cap_50 = sum([s['market_cap'] for s in happy50_stocks])
    
    constituents_h50 = []
    for rank, stock in enumerate(happy50_stocks, 1):
        raw_weight = stock['market_cap'] / total_market_cap_50
        weight = min(raw_weight, 0.10)
        
        constituents_h50.append({
            'index_code': 'H50',
            'stock_symbol': stock['symbol'],
            'weight': weight,
            'rank': rank
        })
    
    # 权重归一化
    total_weight = sum([c['weight'] for c in constituents_h50])
    for c in constituents_h50:
        c['weight'] = c['weight'] / total_weight
    
    print(f"  ✅ HAPPY50: {len(constituents_h50)} 只成分股")
    print(f"     前5大权重股:")
    for c in constituents_h50[:5]:
        stock = next(s for s in happy50_stocks if s['symbol'] == c['stock_symbol'])
        print(f"       • {c['rank']:3d}. {stock['symbol']} - {stock['name']:12s}: {c['weight']*100:5.2f}% (市值: {stock['market_cap']:.0f}亿)")
    print()
    
    # 4. T038: 配置 GROW100 (高成长股票 - 高Beta、科技/新能源为主)
    print("📊 4. 配置 GROW100 成分股...")
    
    # 筛选高成长股票：Beta > 1.0, 主要来自科技/新能源板块
    growth_sectors = ['TECH', 'NEV', 'HEALTH', 'CONS']
    
    growth_stocks = [
        s for s in all_stocks 
        if s['beta'] >= 1.0 and s['sector_code'] in growth_sectors
    ]
    
    # 按 Beta * 波动率 排序，选择前50只
    growth_stocks.sort(key=lambda x: x['beta'] * x['volatility'], reverse=True)
    grow100_stocks = growth_stocks[:min(50, len(growth_stocks))]
    
    # 如果不足50只，从其他板块补充高Beta股票
    if len(grow100_stocks) < 50:
        remaining_stocks = [
            s for s in all_stocks 
            if s['beta'] >= 1.0 and s['symbol'] not in [gs['symbol'] for gs in grow100_stocks]
        ]
        remaining_stocks.sort(key=lambda x: x['beta'], reverse=True)
        grow100_stocks.extend(remaining_stocks[:50 - len(grow100_stocks)])
    
    # 等权重配置（简化处理）
    constituents_g100 = []
    for rank, stock in enumerate(grow100_stocks, 1):
        constituents_g100.append({
            'index_code': 'G100',
            'stock_symbol': stock['symbol'],
            'weight': 1.0 / len(grow100_stocks),  # 等权重（小数形式）
            'rank': rank
        })
    
    print(f"  ✅ GROW100: {len(constituents_g100)} 只成分股")
    print(f"     前5大权重股:")
    for c in constituents_g100[:5]:
        stock = next(s for s in grow100_stocks if s['symbol'] == c['stock_symbol'])
        print(f"       • {c['rank']:3d}. {stock['symbol']} - {stock['name']:12s}: {c['weight']*100:5.2f}% (Beta: {stock['beta']:.2f}, 板块: {stock['sector_code']})")
    print()
    
    # 5. 清空现有成分股配置
    print("🗑️  5. 清空现有成分股配置...")
    for index_code in ['H300', 'H50', 'G100']:
        query = "DELETE FROM index_constituents WHERE index_code = ?"
        db.execute_update(query, (index_code,))
    print("  ✅ 已清空")
    print()
    
    # 6. 插入新的成分股配置
    print("💾 6. 插入成分股配置...")
    
    all_constituents = constituents_h300 + constituents_h50 + constituents_g100
    
    insert_query = """
        INSERT INTO index_constituents 
        (index_code, stock_symbol, weight, rank, join_date, is_active)
        VALUES (?, ?, ?, ?, date('now'), 1)
    """
    
    for c in all_constituents:
        db.execute_update(
            insert_query,
            (c['index_code'], c['stock_symbol'], c['weight'], c['rank'])
        )
    
    print(f"  ✅ 共插入 {len(all_constituents)} 条成分股记录")
    print()
    
    # 7. 验证结果
    print("✅ 7. 验证配置结果...")
    for index_code, count in [('H300', 100), ('H50', 50), ('G100', 50)]:
        query = """
            SELECT COUNT(*) as count, SUM(weight) as total_weight
            FROM index_constituents
            WHERE index_code = ? AND is_active = 1
        """
        result = db.execute_query(query, (index_code,), fetch_one=True)
        
        total_weight_pct = result['total_weight'] * 100 if result['total_weight'] else 0
        status = "✅" if result['count'] >= count - 5 and 99 <= total_weight_pct <= 101 else "⚠️"
        print(f"  {status} {index_code}: {result['count']} 只成分股, 总权重: {total_weight_pct:.2f}%")
    
    print()
    print("=" * 80)
    print("🎉 成分股配置完成！")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    success = configure_index_constituents()
    sys.exit(0 if success else 1)
