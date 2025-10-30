"""
数据库初始化脚本 (SQLite 版本)
执行 init_virtual_market_sqlite.sql 创建所有表
"""
import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def init_database():
    """执行 SQL 脚本初始化 SQLite 数据库"""
    
    # SQLite 数据库文件路径
    db_file = project_root / 'virtual_market.db'
    
    # 读取 SQL 文件
    sql_file = project_root.parent / 'sql_scripts' / 'init_virtual_market_sqlite.sql'
    
    if not sql_file.exists():
        print(f"❌ 错误：SQL 文件不存在: {sql_file}")
        return False
    
    print(f"📂 读取 SQL 文件: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库并执行
    try:
        print(f"🔌 连接 SQLite 数据库: {db_file}")
        
        # 如果数据库文件已存在，备份
        if db_file.exists():
            backup_file = db_file.with_suffix('.db.backup')
            print(f"📦 备份现有数据库到: {backup_file}")
            import shutil
            shutil.copy2(db_file, backup_file)
        
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        
        print("🚀 开始执行 SQL 脚本...")
        cursor.executescript(sql_content)
        conn.commit()
        
        print("✅ SQL 脚本执行成功！")
        
        # 验证表是否创建成功
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 已创建 {len(tables)} 个表:")
        for table in tables:
            # 查询每个表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table[0]:25s} ({count} 条记录)")
        
        cursor.close()
        conn.close()
        
        print(f"\n💾 数据库文件: {db_file}")
        print(f"📏 文件大小: {db_file.stat().st_size / 1024:.2f} KB")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("🎯 A股虚拟市场 - 数据库初始化 (SQLite)")
    print("=" * 80)
    print()
    
    success = init_database()
    
    print()
    print("=" * 80)
    
    if success:
        print("✅ 数据库初始化完成！")
        print("📌 下一步: 运行 data_initializer.py 插入股票数据和历史K线")
        print()
        print("💡 提示: SQLite 用于开发测试，生产环境建议使用 PostgreSQL")
    else:
        print("❌ 数据库初始化失败，请检查错误信息")
        sys.exit(1)
    
    print("=" * 80)
