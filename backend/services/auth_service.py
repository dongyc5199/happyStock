"""
认证服务
处理密码加密、JWT 生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from models.user import User
from config import settings

# JWT 配置
SECRET_KEY = getattr(settings, 'SECRET_KEY', "your-secret-key-change-in-production-09a8f7b6c5d4e3f2a1")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 天


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        加密后的密码哈希
    """
    # 将密码编码为字节,生成盐值并哈希
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        密码是否匹配
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, datetime]:
    """
    创建 JWT access token
    
    Args:
        data: 要编码的数据 (通常包含用户 ID)
        expires_delta: 过期时间增量
        
    Returns:
        (token字符串, 过期时间)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 将过期时间转换为时间戳
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt, expire


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码并验证 JWT token
    
    Args:
        token: JWT token 字符串
        
    Returns:
        解码后的数据,如果 token 无效则返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    验证用户凭据
    
    Args:
        username: 用户名或邮箱
        password: 密码
        
    Returns:
        验证成功返回 User 对象,失败返回 None
    """
    # 尝试用用户名查询
    user = await User.filter(username=username).first()
    
    # 如果用户名未找到,尝试用邮箱查询
    if not user:
        user = await User.filter(email=username).first()
    
    # 用户不存在
    if not user:
        return None
    
    # 验证密码
    if not verify_password(password, user.password_hash):
        return None
    
    return user


async def register_user(username: str, email: str, password: str) -> User:
    """
    注册新用户
    
    Args:
        username: 用户名
        email: 邮箱
        password: 密码
        
    Returns:
        创建的 User 对象
        
    Raises:
        ValueError: 用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    existing_user = await User.filter(username=username).first()
    if existing_user:
        raise ValueError("USERNAME_TAKEN")
    
    # 检查邮箱是否已存在
    existing_email = await User.filter(email=email).first()
    if existing_email:
        raise ValueError("EMAIL_TAKEN")
    
    # 创建新用户
    password_hash = hash_password(password)
    user = await User.create(
        username=username,
        email=email,
        password_hash=password_hash
    )
    
    return user


async def get_user_by_id(user_id: int) -> Optional[User]:
    """
    通过 ID 获取用户
    
    Args:
        user_id: 用户 ID
        
    Returns:
        User 对象或 None
    """
    return await User.filter(id=user_id).first()
