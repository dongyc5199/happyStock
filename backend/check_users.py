#!/usr/bin/env python3
"""查看用户表"""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n📋 所有用户:")
cursor.execute("SELECT id, username, email, created_at FROM users")
users = cursor.fetchall()

if not users:
    print("❌ 没有用户")
else:
    for user_id, username, email, created_at in users:
        print(f"\nID: {user_id}")
        print(f"  用户名: {username}")
        print(f"  邮箱: {email}")
        print(f"  创建时间: {created_at}")

# 特别检查testuser@example.com
print("\n" + "="*80)
cursor.execute("SELECT id, username FROM users WHERE email=?", ('testuser@example.com',))
user = cursor.fetchone()
if user:
    print(f"✅ 找到 testuser@example.com: ID={user[0]}, 用户名={user[1]}")
else:
    print("❌ 未找到 testuser@example.com")

conn.close()
