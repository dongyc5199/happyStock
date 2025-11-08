"""
添加 avatar_url 列到 users 表
"""
import asyncio
import sqlite3

async def add_avatar_url_column():
    db_path = "db.sqlite3"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'avatar_url' in columns:
            print("✅ avatar_url 列已存在,无需添加")
        else:
            print("正在添加 avatar_url 列到 users 表...")
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)")
            conn.commit()
            print("✅ avatar_url 列添加成功!")
        
        # 显示表结构
        cursor.execute("PRAGMA table_info(users)")
        print("\n📊 users 表结构:")
        for row in cursor.fetchall():
            print(f"  {row[1]} {row[2]} {'NOT NULL' if row[3] else 'NULL'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_avatar_url_column())
