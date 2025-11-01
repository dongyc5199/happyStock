"""
认证相关的 API 路由
提供登录、注册、获取当前用户、登出等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from schemas.auth import (
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    MeResponse,
    LogoutResponse,
    ErrorResponse,
    UserResponse,
    AuthSession,
)
from services.auth_service import (
    authenticate_user,
    register_user,
    create_access_token,
    decode_access_token,
    get_user_by_id,
)
from models.user import User

router = APIRouter(prefix="/auth")
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    获取当前认证用户的依赖函数
    从 Authorization header 中提取并验证 JWT token
    
    Raises:
        HTTPException: token 无效或用户不存在
    """
    token = credentials.credentials
    
    # 解码 token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Token 无效或已过期"
                }
            }
        )
    
    # 获取用户 ID (sub 是字符串,需要转换为整数)
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Token 无效"
                }
            }
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Token 无效"
                }
            }
        )
    
    # 查询用户
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "用户不存在"
                }
            }
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    使用用户名/邮箱和密码登录,成功返回 JWT token
    """
    # 验证用户凭据
    user = await authenticate_user(request.username, request.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "用户名或密码错误"
                }
            }
        )
    
    # 生成 JWT token (sub 必须是字符串)
    token, expires_at = create_access_token(data={"sub": str(user.id)})
    
    # 构建响应
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        created_at=user.created_at
    )
    
    session = AuthSession(
        user=user_response,
        token=token,
        expires_at=expires_at
    )
    
    return LoginResponse(success=True, data=session)


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    用户注册
    
    注册新用户账号,成功后自动登录并返回 JWT token
    """
    try:
        # 创建新用户
        user = await register_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
    except ValueError as e:
        error_code = str(e)
        
        if error_code == "USERNAME_TAKEN":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "USERNAME_TAKEN",
                        "message": "该用户名已被占用",
                        "details": {"field": "username"}
                    }
                }
            )
        elif error_code == "EMAIL_TAKEN":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "EMAIL_TAKEN",
                        "message": "该邮箱已被注册",
                        "details": {"field": "email"}
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": {
                        "code": "SERVER_ERROR",
                        "message": "注册失败"
                    }
                }
            )
    
    # 生成 JWT token (自动登录, sub 必须是字符串)
    token, expires_at = create_access_token(data={"sub": str(user.id)})
    
    # 构建响应
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        created_at=user.created_at
    )
    
    session = AuthSession(
        user=user_response,
        token=token,
        expires_at=expires_at
    )
    
    return LoginResponse(success=True, data=session)


@router.get("/me", response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    需要在 Authorization header 中提供有效的 JWT token
    """
    user_response = UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )
    
    return MeResponse(
        success=True,
        data={"user": user_response.model_dump()}
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    注意: 由于使用的是无状态 JWT,实际的 token 失效由客户端处理
    (从 localStorage 中删除 token)
    如需服务端 token 黑名单,需要集成 Redis
    """
    return LogoutResponse(success=True, message="登出成功")
