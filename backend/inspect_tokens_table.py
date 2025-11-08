#!/usr/bin/env python3
"""查看password_reset_tokens表详细信息"""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n📋 password_reset_tokens 表结构:")
cursor.execute("PRAGMA table_info(password_reset_tokens)")
columns = cursor.fetchall()
col_names = []
for col in columns:
    col_names.append(col[1])
    print(f"  {col[1]} ({col[2]})")

print(f"\n列名列表: {col_names}")

# 查看所有数据
print("\n📋 所有令牌记录:")
cursor.execute("SELECT * FROM password_reset_tokens ORDER BY created_at DESC")
rows = cursor.fetchall()
print(f"总共 {len(rows)} 条记录\n")

for i, row in enumerate(rows[:5], 1):
    print(f"{i}. 记录:")
    for j, col_name in enumerate(col_names):
        print(f"   {col_name}: {row[j]}")
    print()

conn.close()
