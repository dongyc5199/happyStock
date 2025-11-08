"""查看指数代码"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.db_manager_sqlite import get_db_manager

db = get_db_manager()
indices = db.execute_query('SELECT code, name, index_type FROM indices WHERE index_type="CORE"')

print("核心指数:")
for idx in indices:
    print(f"  {idx['code']:10s} - {idx['name']}")
