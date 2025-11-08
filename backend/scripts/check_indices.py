"""
检查指数数据和成分股配置
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.db_manager_sqlite import get_db_manager

def check_indices():
    """检查指数数据"""
    print("=" * 80)
    print("🔍 检查指数数据")
    print("=" * 80)
    print()
    
    db = get_db_manager()
    
    # 1. 检查指数表
    print("📊 1. 指数基础数据")
    query = "SELECT code, name, index_type, base_point, current_value FROM indices ORDER BY index_type, code"
    indices = db.execute_query(query)
    
    if not indices:
        print("  ❌ 没有找到指数数据")
        return False
    
    for idx in indices:
        current_val = f"{idx['current_value']:.2f}" if idx['current_value'] else 'N/A'
        print(f"  📈 [{idx['index_type']:8s}] {idx['code']:8s} - {idx['name']:20s} | 基点: {idx['base_point']:6.1f} | 当前: {current_val}")
    print()
    
    # 2. 检查成分股配置
    print("📋 2. 指数成分股配置")
    core_indices = ['HAPPY300', 'HAPPY50', 'GROW100']
    
    for index_code in core_indices:
        query = """
            SELECT COUNT(*) as count, SUM(weight) as total_weight
            FROM index_constituents
            WHERE index_code = ?
        """
        result = db.execute_query(query, (index_code,), fetch_one=True)
        
        if result and result['count'] > 0:
            count = result['count']
            total_weight = (result['total_weight'] or 0) * 100  # 转换为百分比
            status = "✅" if 99 <= total_weight <= 101 else "⚠️"
            print(f"  {status} {index_code}: {count} 只成分股, 总权重: {total_weight:.2f}%")
            
            # 显示前5大权重股
            query2 = """
                SELECT ic.stock_symbol, s.name, ic.weight
                FROM index_constituents ic
                JOIN stocks s ON ic.stock_symbol = s.symbol
                WHERE ic.index_code = ?
                ORDER BY ic.weight DESC
                LIMIT 5
            """
            top_stocks = db.execute_query(query2, (index_code,))
            for stock in top_stocks:
                print(f"      • {stock['stock_symbol']} - {stock['name']:12s}: {stock['weight']*100:.2f}%")
        else:
            print(f"  ❌ {index_code}: 没有成分股配置")
    print()
    
    # 3. 检查指数K线数据
    print("📉 3. 指数历史K线数据")
    for index_code in core_indices:
        query = """
            SELECT COUNT(*) as count
            FROM price_data
            WHERE target_type = 'INDEX' AND target_code = ?
        """
        result = db.execute_query(query, (index_code,), fetch_one=True)
        count = result['count'] if result else 0
        status = "✅" if count >= 60 else "❌"
        print(f"  {status} {index_code}: {count} 条K线记录")
    print()
    
    # 4. 检查数据完整性
    print("🔧 4. 数据完整性检查")
    
    # 检查是否有成分股不存在
    query = """
        SELECT ic.index_code, ic.stock_symbol
        FROM index_constituents ic
        LEFT JOIN stocks s ON ic.stock_symbol = s.symbol
        WHERE s.symbol IS NULL
    """
    invalid_constituents = db.execute_query(query)
    if invalid_constituents:
        print("  ⚠️  发现无效成分股:")
        for item in invalid_constituents:
            print(f"      • {item['index_code']}: {item['stock_symbol']} (股票不存在)")
    else:
        print("  ✅ 所有成分股都有效")
    print()
    
    # 总结
    print("=" * 80)
    print("📊 总结")
    print("=" * 80)
    
    # 检查三大核心指数
    all_ok = True
    for index_code in core_indices:
        query = """
            SELECT 
                (SELECT COUNT(*) FROM index_constituents WHERE index_code = ?) as constituent_count,
                (SELECT COUNT(*) FROM price_data WHERE target_type = 'INDEX' AND target_code = ?) as kline_count,
                (SELECT SUM(weight) FROM index_constituents WHERE index_code = ?) as total_weight
        """
        result = db.execute_query(query, (index_code, index_code, index_code), fetch_one=True)
        
        has_constituents = result['constituent_count'] > 0
        has_klines = result['kline_count'] >= 60
        total_weight_pct = (result['total_weight'] or 0) * 100  # 转换为百分比
        weight_valid = 99 <= total_weight_pct <= 101
        
        status = "✅" if (has_constituents and has_klines and weight_valid) else "❌"
        print(f"  {status} {index_code}: ", end="")
        
        parts = []
        if has_constituents:
            parts.append(f"{result['constituent_count']}只成分股")
        else:
            parts.append("缺少成分股")
            all_ok = False
        
        if has_klines:
            parts.append(f"{result['kline_count']}条K线")
        else:
            parts.append("缺少K线数据")
            all_ok = False
        
        if weight_valid:
            parts.append(f"权重{total_weight_pct:.1f}%")
        else:
            parts.append(f"权重异常({total_weight_pct:.1f}%)")
            all_ok = False
        
        print(", ".join(parts))
    
    print()
    if all_ok:
        print("🎉 指数数据完整，可以开始 Phase 4 开发！")
    else:
        print("⚠️  需要先配置指数成分股和历史数据")
    print("=" * 80)
    
    return all_ok

if __name__ == '__main__':
    success = check_indices()
    sys.exit(0 if success else 1)
