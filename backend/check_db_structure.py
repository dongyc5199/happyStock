"""检查数据库表结构"""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=" * 60)
print("Users 表结构:")
print("=" * 60)
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[1]:20} {col[2]:15} {'NOT NULL' if col[3] else 'NULL':10} Default: {col[4]}")

print("\n" + "=" * 60)
print("检查邮件相关表:")
print("=" * 60)

tables = ['password_reset_tokens', 'email_verification_tokens', 'email_logs']
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
existing_tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    if table in existing_tables:
        print(f"✓ {table} 存在")
    else:
        print(f"✗ {table} 不存在")

conn.close()
