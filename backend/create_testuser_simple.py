#!/usr/bin/env python3
"""创建testuser@example.com用户"""
import sqlite3
from datetime import datetime
import bcrypt

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 检查是否已存在
cursor.execute("SELECT id, username FROM users WHERE email=?", ('testuser@example.com',))
existing = cursor.fetchone()

if existing:
    print(f"✅ 用户已存在: ID={existing[0]}, 用户名={existing[1]}")
else:
    # 生成密码哈希 (密码: TestPass123!)
    password = 'TestPass123!'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 插入新用户
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, created_at, updated_at, email_verified)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('testuser_new', 'testuser@example.com', password_hash, 
          datetime.now().isoformat(), datetime.now().isoformat(), 0))
    
    conn.commit()
    user_id = cursor.lastrowid
    
    print(f"✅ 用户创建成功!")
    print(f"  ID: {user_id}")
    print(f"  用户名: testuser_new")
    print(f"  邮箱: testuser@example.com")
    print(f"  初始密码: {password}")

conn.close()
