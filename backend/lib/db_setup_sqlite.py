"""
Database Setup Script for SQLite
执行虚拟市场数据库初始化SQL脚本 (SQLite版本)
"""
import os
import sqlite3
from pathlib import Path


def execute_sql_file(db_path: str, sql_file_path: str):
    """执行SQL文件"""
    # 读取SQL文件
    sql_path = Path(sql_file_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 连接SQLite数据库
    print(f"[*] Connecting to SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)

    try:
        print(f"[*] Executing SQL file: {sql_file_path}")
        conn.executescript(sql_content)
        print("[+] SQL file executed successfully!")

    except Exception as e:
        print(f"[-] Error executing SQL: {e}")
        raise
    finally:
        conn.close()
        print("[*] Database connection closed")


def verify_tables(db_path: str):
    """验证表是否创建成功"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 查询所有表
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print("\n[*] Created tables:")
        expected_tables = [
            'sectors', 'stocks', 'stock_metadata',
            'indices', 'index_constituents',
            'price_data', 'market_states'
        ]

        for table_name in expected_tables:
            if table_name in tables:
                print(f"  [+] {table_name}")
            else:
                print(f"  [-] {table_name} (missing)")

        # 检查板块数据
        cursor.execute("SELECT COUNT(*) FROM sectors;")
        sector_count = cursor.fetchone()[0]
        print(f"\n[*] Sectors inserted: {sector_count}/10")

        # 检查指数数据
        cursor.execute("SELECT COUNT(*) FROM indices;")
        index_count = cursor.fetchone()[0]
        print(f"[*] Indices inserted: {index_count}/13")

    finally:
        conn.close()


if __name__ == "__main__":
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    sql_file = project_root / "sql_scripts" / "init_virtual_market_sqlite.sql"
    db_path = project_root / "backend" / "virtual_market.db"

    print("=" * 60)
    print("A-Share Virtual Market Database Initialization (SQLite)")
    print("=" * 60)

    try:
        execute_sql_file(str(db_path), str(sql_file))
        print("\n" + "=" * 60)
        verify_tables(str(db_path))
        print("=" * 60)
        print("\n[+] Database initialization completed!")
        print(f"[*] Database location: {db_path}")
        print("[*] Next step: Run 'python -m backend.lib.data_initializer_sqlite' to insert stock data")

    except Exception as e:
        print(f"\n[-] Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
