"""
数据库初始化脚本
执行 init_virtual_market.sql 创建所有表
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def init_database():
    """执行 SQL 脚本初始化数据库"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ 错误：未找到 DATABASE_URL 环境变量")
        return False
    
    # 读取 SQL 文件
    sql_file = project_root.parent / 'sql_scripts' / 'init_virtual_market.sql'
    
    if not sql_file.exists():
        print(f"❌ 错误：SQL 文件不存在: {sql_file}")
        return False
    
    print(f"📂 读取 SQL 文件: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库并执行
    try:
        print(f"🔌 连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🚀 开始执行 SQL 脚本...")
        cursor.execute(sql_content)
        
        print("✅ SQL 脚本执行成功！")
        
        # 验证表是否创建成功
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 已创建 {len(tables)} 个表:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("🎯 A股虚拟市场 - 数据库初始化")
    print("=" * 80)
    print()
    
    success = init_database()
    
    print()
    print("=" * 80)
    
    if success:
        print("✅ 数据库初始化完成！")
        print("📌 下一步: 运行 data_initializer.py 插入股票数据和历史K线")
    else:
        print("❌ 数据库初始化失败，请检查错误信息")
        sys.exit(1)
    
    print("=" * 80)
