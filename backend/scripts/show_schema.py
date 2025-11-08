"""
查看数据库表结构
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.db_manager_sqlite import get_db_manager

def show_table_structure(table_name):
    """显示表结构"""
    db = get_db_manager()
    
    print(f"\n{'='*60}")
    print(f"表: {table_name}")
    print('='*60)
    
    result = db.execute_query(f'PRAGMA table_info({table_name})')
    
    print(f"{'列名':<20} {'类型':<15} {'非空':<8} {'默认值'}")
    print('-'*60)
    
    for col in result:
        null_str = "NOT NULL" if col['notnull'] else ""
        default_str = col['dflt_value'] if col['dflt_value'] else ""
        print(f"{col['name']:<20} {col['type']:<15} {null_str:<8} {default_str}")
    
    print('='*60)

if __name__ == '__main__':
    tables = ['indices', 'index_constituents', 'stocks', 'price_data']
    for table in tables:
        try:
            show_table_structure(table)
        except Exception as e:
            print(f"Error with table {table}: {e}")
