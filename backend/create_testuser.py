#!/usr/bin/env python3
"""创建testuser@example.com用户"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.user import User
from lib.db_setup import init_db, close_db

async def create_user():
    await init_db()
    
    # 检查是否已存在
    existing = await User.filter(email='testuser@example.com').first()
    if existing:
        print(f"✅ 用户已存在: {existing.username}")
        return
    
    # 创建新用户
    user = await User.create(
        username='testuser_new',
        email='testuser@example.com',
        password_hash='$2b$12$dummy_hash_for_testing',  # 临时密码哈希
    )
    print(f"✅ 创建成功!")
    print(f"  ID: {user.id}")
    print(f"  用户名: {user.username}")
    print(f"  邮箱: {user.email}")
    
    await close_db()

if __name__ == '__main__':
    asyncio.run(create_user())
