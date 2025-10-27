"""
自定义异常类
用于交易系统的业务异常处理
"""


class TradingException(Exception):
    """交易异常基类"""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InsufficientBalanceError(TradingException):
    """余额不足异常"""

    def __init__(self, message: str = "账户余额不足"):
        super().__init__(message, "INSUFFICIENT_BALANCE")


class InsufficientHoldingsError(TradingException):
    """持仓不足异常"""

    def __init__(self, message: str = "持仓数量不足"):
        super().__init__(message, "INSUFFICIENT_HOLDINGS")


class AccountNotFoundError(TradingException):
    """账户不存在异常"""

    def __init__(self, message: str = "账户不存在"):
        super().__init__(message, "ACCOUNT_NOT_FOUND")


class AssetNotFoundError(TradingException):
    """资产不存在异常"""

    def __init__(self, message: str = "资产不存在"):
        super().__init__(message, "ASSET_NOT_FOUND")


class HoldingNotFoundError(TradingException):
    """持仓不存在异常"""

    def __init__(self, message: str = "持仓不存在"):
        super().__init__(message, "HOLDING_NOT_FOUND")


class InvalidQuantityError(TradingException):
    """无效交易数量异常"""

    def __init__(self, message: str = "交易数量无效"):
        super().__init__(message, "INVALID_QUANTITY")


class InvalidPriceError(TradingException):
    """无效价格异常"""

    def __init__(self, message: str = "价格无效"):
        super().__init__(message, "INVALID_PRICE")


class AccountLimitReachedError(TradingException):
    """账户数量达到上限异常"""

    def __init__(self, message: str = "账户数量已达上限"):
        super().__init__(message, "ACCOUNT_LIMIT_REACHED")


class TradeFailedError(TradingException):
    """交易执行失败异常"""

    def __init__(self, message: str = "交易执行失败"):
        super().__init__(message, "TRADE_FAILED")


class DatabaseError(TradingException):
    """数据库错误异常"""

    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, "DATABASE_ERROR")
