"""
添加邮件相关表的数据库迁移脚本
执行: python add_email_tables_migration.py
"""
import asyncio
from tortoise import Tortoise
from config import settings

async def migrate():
    """执行数据库迁移"""
    # 初始化 Tortoise-ORM
    await Tortoise.init(
        db_url=settings.resolved_database_url,
        modules={
            'models': [
                'models.user',
                'models.account',
                'models.asset',
                'models.trade',
                'models.holding',
                'models.password_reset_token',
                'models.email_verification_token',
                'models.email_log',
            ]
        }
    )
    
    conn = Tortoise.get_connection("default")
    
    # 1. 生成新表（如果不存在）
    await Tortoise.generate_schemas()
    
    # 2. 手动添加 users 表的新列（如果不存在）
    try:
        # 检查列是否已存在
        result = await conn.execute_query_dict("PRAGMA table_info(users)")
        existing_columns = [col['name'] for col in result]
        
        if 'email_verified' not in existing_columns:
            print("添加 email_verified 列...")
            await conn.execute_query("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
            print("✓ email_verified 列添加成功")
        else:
            print("✓ email_verified 列已存在")
            
        if 'email_verified_at' not in existing_columns:
            print("添加 email_verified_at 列...")
            await conn.execute_query("ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP")
            print("✓ email_verified_at 列添加成功")
        else:
            print("✓ email_verified_at 列已存在")
            
    except Exception as e:
        print(f"⚠️ 添加列时出错: {e}")
    
    print("\n✅ 数据库迁移完成！")
    print("新增表:")
    print("  - password_reset_tokens (密码重置令牌)")
    print("  - email_verification_tokens (邮箱验证令牌)")
    print("  - email_logs (邮件发送日志)")
    print("扩展表:")
    print("  - users (添加 email_verified, email_verified_at 字段)")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(migrate())
