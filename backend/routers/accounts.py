"""
账户管理 API 路由
"""
from fastapi import APIRouter, Path, Query, status
from typing import List

from services.account_service import AccountService
from schemas.requests import CreateAccountRequest, UpdateAccountRequest
from schemas.responses import AccountResponse, SuccessResponse

router = APIRouter()


@router.post(
    "/accounts",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建模拟账户",
    description="为用户创建一个新的模拟交易账户",
)
async def create_account(request: CreateAccountRequest):
    """
    创建模拟账户

    - **user_id**: 用户ID
    - **account_name**: 账户名称
    - **initial_balance**: 初始资金（默认10万）
    """
    # 创建账户
    account = await AccountService.create_account(
        user_id=request.user_id,
        account_name=request.account_name,
        initial_balance=request.initial_balance,
    )

    # 转换为响应模型
    account_data = AccountResponse.model_validate(account)

    return SuccessResponse(
        success=True,
        message="账户创建成功",
        data=account_data.model_dump(),
    )


@router.get(
    "/accounts/{account_id}",
    response_model=SuccessResponse,
    summary="获取账户详情",
    description="获取指定账户的详细信息，包括总资产、盈亏等",
)
async def get_account(
    account_id: int = Path(..., description="账户ID", gt=0)
):
    """
    获取账户详情

    返回账户的完整信息，包括：
    - 基本信息（账户名、余额等）
    - 总资产
    - 总盈亏
    - 收益率
    """
    # 获取账户
    account = await AccountService.get_account(account_id)

    # 计算汇总信息
    summary = await AccountService.calculate_account_summary(account)

    # 构建响应数据
    account_data = AccountResponse.model_validate(account).model_dump()
    account_data.update(summary)

    return SuccessResponse(
        success=True,
        data=account_data,
    )


@router.get(
    "/accounts/user/{user_id}",
    response_model=SuccessResponse,
    summary="获取用户账户列表",
    description="获取指定用户的所有模拟交易账户",
)
async def get_user_accounts(
    user_id: int = Path(..., description="用户ID", gt=0),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
):
    """
    获取用户账户列表

    支持分页查询
    """
    # 获取账户列表
    accounts, total = await AccountService.get_user_accounts(
        user_id=user_id,
        page=page,
        page_size=page_size,
    )

    # 转换为响应模型
    accounts_data = [
        AccountResponse.model_validate(account).model_dump()
        for account in accounts
    ]

    return SuccessResponse(
        success=True,
        data={
            "accounts": accounts_data,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.put(
    "/accounts/{account_id}/reset",
    response_model=SuccessResponse,
    summary="重置账户",
    description="清空账户的持仓和交易记录，恢复初始资金",
)
async def reset_account(
    account_id: int = Path(..., description="账户ID", gt=0)
):
    """
    重置账户

    此操作将：
    1. 删除所有持仓记录
    2. 删除所有交易记录
    3. 恢复余额为初始资金

    ⚠️ 此操作不可撤销
    """
    # 重置账户
    account = await AccountService.reset_account(account_id)

    # 转换为响应模型
    account_data = AccountResponse.model_validate(account).model_dump()

    return SuccessResponse(
        success=True,
        message="账户已成功重置",
        data=account_data,
    )


@router.patch(
    "/accounts/{account_id}",
    response_model=SuccessResponse,
    summary="更新账户信息",
    description="更新账户名称等信息",
)
async def update_account(
    request: UpdateAccountRequest,
    account_id: int = Path(..., description="账户ID", gt=0),
):
    """
    更新账户信息

    目前支持更新：
    - 账户名称
    """
    # 更新账户
    account = await AccountService.update_account_name(
        account_id=account_id,
        new_name=request.account_name,
    )

    # 转换为响应模型
    account_data = AccountResponse.model_validate(account).model_dump()

    return SuccessResponse(
        success=True,
        message="账户信息已更新",
        data=account_data,
    )


@router.delete(
    "/accounts/{account_id}",
    response_model=SuccessResponse,
    summary="删除账户",
    description="删除指定的模拟交易账户",
)
async def delete_account(
    account_id: int = Path(..., description="账户ID", gt=0)
):
    """
    删除账户

    此操作将删除账户及其所有关联数据（持仓、交易记录）

    ⚠️ 此操作不可撤销
    """
    # 删除账户
    await AccountService.delete_account(account_id)

    return SuccessResponse(
        success=True,
        message=f"账户 {account_id} 已成功删除",
    )
