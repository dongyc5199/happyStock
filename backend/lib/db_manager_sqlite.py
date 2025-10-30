"""
SQLite Database Connection Manager
SQLite数据库连接管理
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from pathlib import Path


class DatabaseManager:
    """SQLite数据库管理器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库管理器

        Args:
            db_path: SQLite数据库文件路径 (可以是相对路径或绝对路径)
        """
        if db_path is None:
            # 从环境变量读取,支持相对路径
            from config import settings
            db_url = settings.resolved_database_url
            
            # 从 sqlite:///path.db 提取路径
            if db_url.startswith('sqlite:///'):
                self.db_path = db_url[10:]  # 去掉 'sqlite:///'
            else:
                # 默认使用backend目录下的virtual_market.db
                backend_dir = Path(__file__).parent.parent
                self.db_path = str(backend_dir / "virtual_market.db")
        else:
            # 如果传入的是相对路径,转换为绝对路径
            path = Path(db_path)
            if not path.is_absolute():
                backend_dir = Path(__file__).parent.parent
                self.db_path = str(backend_dir / db_path)
            else:
                self.db_path = db_path

    def initialize(self):
        """初始化（SQLite不需要连接池）"""
        print(f"[+] Using SQLite database: {self.db_path}")

    def close(self):
        """关闭（SQLite不需要）"""
        print("[*] SQLite database closed")

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典形式的结果
        return conn

    @contextmanager
    def get_cursor(self) -> Generator:
        """
        获取游标的上下文管理器

        使用示例:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM stocks")
                results = cursor.fetchall()

        Yields:
            cursor: 数据库游标
        """
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            yield cursor
            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[-] Database error: {e}")
            raise

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @contextmanager
    def get_connection_context(self) -> Generator:
        """
        获取连接的上下文管理器

        使用示例:
            with db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM stocks")

        Yields:
            connection: 数据库连接
        """
        conn = None

        try:
            conn = self.get_connection()
            yield conn
            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[-] Database error: {e}")
            raise

        finally:
            if conn:
                conn.close()

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
            cursor.execute(query, params or ())

            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

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
            cursor.execute(query, params or ())
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
