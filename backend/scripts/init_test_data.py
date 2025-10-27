"""
初始化测试数据脚本
"""
import asyncio
from tortoise import Tortoise
from decimal import Decimal
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TORTOISE_ORM
from models.user import User
from models.asset import Asset


async def init_test_data():
    """初始化测试数据"""

    # 初始化 Tortoise-ORM
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("开始初始化测试数据...")

    # 1. 创建测试用户
    print("\n1. 创建测试用户...")
    try:
        user1 = await User.create(
            username="testuser1",
            email="test1@example.com",
            password_hash="hashed_password_123"
        )
        print(f"   [OK] 创建用户: {user1.username} (ID: {user1.id})")

        user2 = await User.create(
            username="testuser2",
            email="test2@example.com",
            password_hash="hashed_password_456"
        )
        print(f"   [OK] 创建用户: {user2.username} (ID: {user2.id})")
    except Exception as e:
        print(f"   ! 用户可能已存在: {e}")

    # 2. 创建测试资产
    print("\n2. 创建测试资产...")
    assets_data = [
        {
            "symbol": "600000.SH",
            "name": "浦发银行",
            "exchange": "上海证券交易所",
            "asset_type": "股票",
            "current_price": Decimal("12.50"),
        },
        {
            "symbol": "000001.SZ",
            "name": "平安银行",
            "exchange": "深圳证券交易所",
            "asset_type": "股票",
            "current_price": Decimal("15.30"),
        },
        {
            "symbol": "600036.SH",
            "name": "招商银行",
            "exchange": "上海证券交易所",
            "asset_type": "股票",
            "current_price": Decimal("42.80"),
        },
        {
            "symbol": "601318.SH",
            "name": "中国平安",
            "exchange": "上海证券交易所",
            "asset_type": "股票",
            "current_price": Decimal("58.90"),
        },
        {
            "symbol": "600519.SH",
            "name": "贵州茅台",
            "exchange": "上海证券交易所",
            "asset_type": "股票",
            "current_price": Decimal("1680.00"),
        },
    ]

    for asset_data in assets_data:
        try:
            asset = await Asset.create(**asset_data)
            print(f"   [OK] 创建资产: {asset.symbol} - {asset.name} ({asset.current_price})")
        except Exception as e:
            print(f"   ! 资产 {asset_data['symbol']} 可能已存在: {e}")

    print("\n[SUCCESS] 测试数据初始化完成！")
    print("\n可用的测试用户:")
    users = await User.all()
    for user in users:
        print(f"   - User ID: {user.id}, Username: {user.username}")

    print("\n可用的测试资产:")
    assets = await Asset.all()
    for asset in assets:
        print(f"   - {asset.symbol}: {asset.name} ({asset.current_price})")

    # 关闭连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_test_data())
