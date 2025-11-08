"""直接添加users表的新列"""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # 添加 email_verified 列
    print("添加 email_verified 列...")
    cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
    print("✓ email_verified 列添加成功")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("✓ email_verified 列已存在")
    else:
        print(f"✗ 添加 email_verified 列失败: {e}")

try:
    # 添加 email_verified_at 列
    print("添加 email_verified_at 列...")
    cursor.execute("ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP")
    print("✓ email_verified_at 列添加成功")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("✓ email_verified_at 列已存在")
    else:
        print(f"✗ 添加 email_verified_at 列失败: {e}")

conn.commit()
conn.close()

print("\n✅ 列添加完成!")
