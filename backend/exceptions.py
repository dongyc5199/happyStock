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


# ==================== 邮箱和认证相关异常 ====================

class EmailException(Exception):
    """邮箱异常基类"""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InvalidEmailError(EmailException):
    """无效邮箱异常"""

    def __init__(self, message: str = "请输入有效的邮箱地址"):
        super().__init__(message, "INVALID_EMAIL")


class InvalidTokenError(EmailException):
    """无效令牌异常"""

    def __init__(self, message: str = "无效的验证链接"):
        super().__init__(message, "INVALID_TOKEN")


class TokenExpiredError(EmailException):
    """令牌过期异常"""

    def __init__(self, message: str = "验证链接已过期"):
        super().__init__(message, "TOKEN_EXPIRED")


class TokenUsedError(EmailException):
    """令牌已使用异常"""

    def __init__(self, message: str = "验证链接已被使用"):
        super().__init__(message, "TOKEN_USED")


class TokenNotFoundError(EmailException):
    """令牌不存在异常"""

    def __init__(self, message: str = "验证链接不存在或已失效"):
        super().__init__(message, "TOKEN_NOT_FOUND")


class WeakPasswordError(EmailException):
    """密码强度不足异常"""

    def __init__(self, message: str = "密码必须至少8个字符，包含字母和数字"):
        super().__init__(message, "WEAK_PASSWORD")


class PasswordMismatchError(EmailException):
    """密码不匹配异常"""

    def __init__(self, message: str = "两次输入的密码不一致"):
        super().__init__(message, "PASSWORD_MISMATCH")


class EmailAlreadyVerifiedError(EmailException):
    """邮箱已验证异常"""

    def __init__(self, message: str = "您的邮箱已经验证过了"):
        super().__init__(message, "EMAIL_ALREADY_VERIFIED")


class EmailUnchangedError(EmailException):
    """邮箱未变更异常"""

    def __init__(self, message: str = "新邮箱与当前邮箱相同"):
        super().__init__(message, "EMAIL_UNCHANGED")


class EmailInUseError(EmailException):
    """邮箱已被使用异常"""

    def __init__(self, message: str = "该邮箱已被其他账户使用"):
        super().__init__(message, "EMAIL_IN_USE")


class InvalidPasswordError(EmailException):
    """密码错误异常"""

    def __init__(self, message: str = "当前密码错误"):
        super().__init__(message, "INVALID_PASSWORD")


class RateLimitExceededError(EmailException):
    """频率限制超限异常"""

    def __init__(self, message: str = "请求过于频繁", retry_after: int = 0):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
