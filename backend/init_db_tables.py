"""
检查并初始化数据库表
"""
import asyncio
from tortoise import Tortoise
from config import TORTOISE_ORM

async def init_database():
    print("正在连接数据库...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("正在生成数据库表结构...")
    await Tortoise.generate_schemas()
    
    print("✅ 数据库表已创建/更新")
    
    # 检查 users 表
    from models.user import User
    count = await User.all().count()
    print(f"📊 当前用户数量: {count}")
    
    await Tortoise.close_connections()
    print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    asyncio.run(init_database())
