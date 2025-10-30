"""监控价格变化情况"""
import time
from lib.db_manager_sqlite import DatabaseManager

def get_snapshot():
    """获取当前价格快照"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT symbol, name, current_price, change_pct, updated_at
        FROM stocks 
        WHERE is_active = 1
        ORDER BY symbol
        LIMIT 5
    """)
    
    snapshot = {}
    for row in cursor.fetchall():
        symbol, name, price, change_pct, updated_at = row
        snapshot[symbol] = {
            'name': name,
            'price': price,
            'change_pct': change_pct,
            'updated_at': updated_at
        }
    
    conn.close()
    return snapshot

print("开始监控价格变化...")
print("每10秒检查一次前5只股票的价格变化")
print("=" * 100)

prev_snapshot = None
count = 0

while count < 5:  # 监控5次,共50秒
    count += 1
    current_snapshot = get_snapshot()
    
    print(f"\n[检查 #{count}] {time.strftime('%H:%M:%S')}")
    print("-" * 100)
    
    for symbol, data in current_snapshot.items():
        if prev_snapshot and symbol in prev_snapshot:
            prev_data = prev_snapshot[symbol]
            price_diff = data['price'] - prev_data['price']
            change_diff = data['change_pct'] - prev_data['change_pct']
            
            # 判断是否有变化
            if abs(price_diff) > 0.001 or abs(change_diff) > 0.001:
                status = "✅ 有变化"
            else:
                status = "❌ 无变化"
            
            print(f"{status} | {symbol} {data['name']:10} | "
                  f"价格: {prev_data['price']:.2f} → {data['price']:.2f} (差:{price_diff:+.4f}) | "
                  f"涨跌: {prev_data['change_pct']:.2f}% → {data['change_pct']:.2f}% (差:{change_diff:+.4f}%) | "
                  f"时间: {data['updated_at']}")
        else:
            print(f"初始 | {symbol} {data['name']:10} | "
                  f"价格: {data['price']:.2f} | "
                  f"涨跌: {data['change_pct']:.2f}% | "
                  f"时间: {data['updated_at']}")
    
    prev_snapshot = current_snapshot
    
    if count < 5:
        time.sleep(10)  # 等待10秒

print("\n" + "=" * 100)
print("监控结束")
