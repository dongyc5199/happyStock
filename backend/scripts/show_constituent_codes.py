"""查看成分股表中的指数代码"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.db_manager_sqlite import get_db_manager

db = get_db_manager()
result = db.execute_query('SELECT DISTINCT index_code FROM index_constituents')

print("成分股表中的指数代码:")
for row in result:
    print(f"  {row['index_code']}")
