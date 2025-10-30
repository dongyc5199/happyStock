"""实时监控价格变化 - 持续观察"""
import time
from lib.db_manager_sqlite import DatabaseManager
from datetime import datetime

def get_prices():
    """获取当前价格"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT symbol, name, current_price, change_pct, updated_at
        FROM stocks 
        WHERE is_active = 1
        ORDER BY ABS(change_pct) DESC
        LIMIT 10
    """)
    
    result = cursor.fetchall()
    conn.close()
    return result

print("=" * 100)
print("实时价格变化监控 - 显示变化最大的10只股票")
print("按 Ctrl+C 停止监控")
print("=" * 100)

prev_data = {}
count = 0

try:
    while True:
        count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        rows = get_prices()
        
        print(f"\n[{current_time}] 第 {count} 次刷新")
        print("-" * 100)
        print(f"{'股票代码':<10} {'名称':<12} {'当前价格':>10} {'涨跌幅':>8} {'价格变化':>10} {'涨跌变化':>10} {'更新时间':<20}")
        print("-" * 100)
        
        for row in rows:
            symbol, name, price, change_pct, updated_at = row
            
            # 计算变化
            if symbol in prev_data:
                prev_price, prev_change = prev_data[symbol]
                price_diff = price - prev_price
                change_diff = change_pct - prev_change
                
                # 用颜色标记变化
                if abs(price_diff) > 0.01 or abs(change_diff) > 0.01:
                    marker = "🔴" if price_diff > 0 else "🟢" if price_diff < 0 else "⚪"
                else:
                    marker = "⚪"
                
                print(f"{symbol:<10} {name:<12} {price:>10.2f} {change_pct:>7.2f}% "
                      f"{price_diff:>+9.2f} {change_diff:>+9.2f}% {updated_at:<20} {marker}")
            else:
                print(f"{symbol:<10} {name:<12} {price:>10.2f} {change_pct:>7.2f}% "
                      f"{'--':>9} {'--':>9} {updated_at:<20} ⚪")
            
            prev_data[symbol] = (price, change_pct)
        
        # 等待3秒
        time.sleep(3)
        
except KeyboardInterrupt:
    print("\n\n" + "=" * 100)
    print("监控已停止")
    print("=" * 100)
