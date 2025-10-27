"""
工具函数模块
包含通用的工具函数
"""
from decimal import Decimal
from typing import Optional


def format_currency(amount: Decimal, symbol: str = "¥") -> str:
    """
    格式化货币金额

    Args:
        amount: 金额
        symbol: 货币符号

    Returns:
        格式化后的字符串
    """
    return f"{symbol}{amount:,.2f}"


def calculate_profit_rate(profit: Decimal, cost: Decimal) -> Optional[Decimal]:
    """
    计算收益率

    Args:
        profit: 盈亏金额
        cost: 成本

    Returns:
        收益率百分比，如果成本为0则返回None
    """
    if cost == 0:
        return None
    return (profit / cost) * 100
