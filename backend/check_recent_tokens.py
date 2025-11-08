#!/usr/bin/env python3
"""检查最近的令牌请求"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n" + "="*80)
print("📋 最近10个密码重置令牌请求")
print("="*80)

cursor.execute('''
    SELECT email, token, created_at, expires_at, used_at
    FROM password_reset_tokens
    ORDER BY created_at DESC
    LIMIT 10
''')

rows = cursor.fetchall()
if not rows:
    print("❌ 没有找到任何令牌")
else:
    for i, (email, token, created_at, expires_at, used_at) in enumerate(rows, 1):
        status = "✅ 有效" if not used_at else "❌ 已使用"
        print(f"\n{i}. {status}")
        print(f"   邮箱: {email}")
        print(f"   令牌: {token[:50]}...")
        print(f"   创建: {created_at}")
        if used_at:
            print(f"   使用: {used_at}")

print("\n" + "="*80)

# 检查用户表
print("\n📋 检查用户表中的邮箱:")
cursor.execute("SELECT email, username FROM users")
users = cursor.fetchall()
for email, username in users:
    print(f"  - {email} (用户名: {username})")

conn.close()
