"""
Database Connection Pool Manager
PostgreSQL数据库连接池管理
"""
import os
from contextlib import contextmanager
from typing import Generator, Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    """
    数据库连接池管理器

    使用psycopg2连接池管理PostgreSQL连接
    支持上下文管理器自动获取和释放连接
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        min_connections: int = 2,
        max_connections: int = 10
    ):
        """
        初始化数据库连接池

        Args:
            database_url: PostgreSQL连接URL
            min_connections: 最小连接数
            max_connections: 最大连接数
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:password@localhost:5432/happystock_dev'
        )
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[pool.SimpleConnectionPool] = None

    def initialize(self):
        """初始化连接池"""
        if self._pool is not None:
            print("[!] Connection pool already initialized")
            return

        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                self.min_connections,
                self.max_connections,
                self.database_url
            )
            print(f"[+] Database connection pool initialized ({self.min_connections}-{self.max_connections} connections)")

        except Exception as e:
            print(f"[-] Failed to initialize connection pool: {e}")
            raise

    def close(self):
        """关闭连接池"""
        if self._pool is not None:
            self._pool.closeall()
            self._pool = None
            print("[*] Database connection pool closed")

    def get_connection(self):
        """
        从连接池获取连接

        Returns:
            psycopg2.connection: 数据库连接

        Raises:
            RuntimeError: 连接池未初始化
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call initialize() first.")

        return self._pool.getconn()

    def put_connection(self, connection):
        """
        将连接归还到连接池

        Args:
            connection: 数据库连接
        """
        if self._pool is not None:
            self._pool.putconn(connection)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator:
        """
        获取游标的上下文管理器

        使用示例:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM stocks")
                results = cursor.fetchall()

        Args:
            cursor_factory: 游标工厂类，默认RealDictCursor返回字典

        Yields:
            cursor: 数据库游标
        """
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            cursor = connection.cursor(cursor_factory=cursor_factory)
            yield cursor
            connection.commit()

        except Exception as e:
            if connection:
                connection.rollback()
            print(f"[-] Database error: {e}")
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                self.put_connection(connection)

    @contextmanager
    def get_connection_context(self) -> Generator:
        """
        获取连接的上下文管理器

        使用示例:
            with db_manager.get_connection_context() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM stocks")

        Yields:
            connection: 数据库连接
        """
        connection = None

        try:
            connection = self.get_connection()
            yield connection
            connection.commit()

        except Exception as e:
            if connection:
                connection.rollback()
            print(f"[-] Database error: {e}")
            raise

        finally:
            if connection:
                self.put_connection(connection)

    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False):
        """
        执行查询并返回结果

        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_one: 是否只获取一条记录

        Returns:
            查询结果 (dict或list of dict)
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

            if fetch_one:
                return cursor.fetchone()
            else:
                return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        执行更新/插入/删除操作

        Args:
            query: SQL语句
            params: 参数

        Returns:
            影响的行数
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    def health_check(self) -> bool:
        """
        健康检查：测试数据库连接是否正常

        Returns:
            bool: 连接是否正常
        """
        try:
            result = self.execute_query("SELECT 1 as health", fetch_one=True)
            return result is not None and result.get('health') == 1

        except Exception as e:
            print(f"[-] Database health check failed: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """
    获取全局数据库管理器实例

    Returns:
        DatabaseManager: 数据库管理器
    """
    return db_manager


# FastAPI依赖注入函数
def get_db_cursor():
    """
    FastAPI依赖注入：获取数据库游标

    使用示例:
        @app.get("/stocks")
        async def get_stocks(cursor = Depends(get_db_cursor)):
            cursor.execute("SELECT * FROM stocks")
            return cursor.fetchall()
    """
    with db_manager.get_cursor() as cursor:
        yield cursor
