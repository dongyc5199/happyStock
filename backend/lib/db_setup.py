"""
Database Setup Script
执行虚拟市场数据库初始化SQL脚本
"""
import os
import psycopg2
from pathlib import Path


def get_db_url():
    """从环境变量获取数据库URL"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/happystock_dev')
    return db_url


def execute_sql_file(sql_file_path: str):
    """执行SQL文件"""
    # 读取SQL文件
    sql_path = Path(sql_file_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 连接数据库
    db_url = get_db_url()
    print(f"[*] Connecting to database...")

    conn = psycopg2.connect(db_url)
    conn.autocommit = True

    try:
        with conn.cursor() as cursor:
            print(f"[*] Executing SQL file: {sql_file_path}")
            cursor.execute(sql_content)
            print("[+] SQL file executed successfully!")

            # 打印通知消息（如果有）
            for notice in conn.notices:
                print(notice.strip())

    except Exception as e:
        print(f"[-] Error executing SQL: {e}")
        raise
    finally:
        conn.close()
        print("[*] Database connection closed")


def verify_tables():
    """验证表是否创建成功"""
    db_url = get_db_url()
    conn = psycopg2.connect(db_url)

    try:
        with conn.cursor() as cursor:
            # 查询所有表
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()

            print("\n[*] Created tables:")
            expected_tables = [
                'sectors', 'stocks', 'stock_metadata',
                'indices', 'index_constituents',
                'price_data', 'market_states'
            ]

            found_tables = [t[0] for t in tables]

            for table_name in expected_tables:
                if table_name in found_tables:
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
    sql_file = project_root / "sql_scripts" / "init_virtual_market.sql"

    print("=" * 60)
    print("A-Share Virtual Market Database Initialization")
    print("=" * 60)

    try:
        execute_sql_file(str(sql_file))
        print("\n" + "=" * 60)
        verify_tables()
        print("=" * 60)
        print("\n[+] Database initialization completed!")
        print("[*] Next step: Run 'python -m backend.lib.data_initializer' to insert stock data")

    except Exception as e:
        print(f"\n[-] Failed to initialize database: {e}")
        print("\n[!] Troubleshooting:")
        print("  1. Check if PostgreSQL is running")
        print("  2. Verify DATABASE_URL in backend/.env")
        print("  3. Ensure database 'happystock_dev' exists")
        print("  4. Check database credentials")
