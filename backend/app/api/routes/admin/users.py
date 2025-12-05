from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import (
    get_current_admin,
    require_admin_or_above,
    get_client_ip,
)
from app.models import Admin, User
from app.schemas.admin import (
    UserListRequest,
    UserListResponse,
    UserDetailResponse,
    BalanceAdjustRequest,
    BalanceAdjustResponse,
)
from app.services.admin import (
    get_users_list,
    get_user_detail,
    adjust_user_balance,
    log_admin_action,
)

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    per_page: int = 20,
    search: str = None,
    order_by: str = "created_at",
    order_desc: bool = True,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List all users with pagination and search."""
    users, total = await get_users_list(
        db,
        page=page,
        per_page=per_page,
        search=search,
        order_by=order_by,
        order_desc=order_desc,
    )

    total_pages = (total + per_page - 1) // per_page

    # Get stats for each user (simplified - no heavy stats)
    user_responses = [
        UserDetailResponse(
            id=u.id,
            telegram_id=u.telegram_id,
            username=u.username,
            first_name=u.first_name,
            last_name=u.last_name,
            language_code=u.language_code,
            balance_xpet=u.balance_xpet,
            ref_code=u.ref_code,
            referrer_id=u.referrer_id,
            ref_levels_unlocked=u.ref_levels_unlocked,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]

    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Get user details with stats."""
    result = await get_user_detail(db, user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = result["user"]

    return UserDetailResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
        balance_xpet=user.balance_xpet,
        ref_code=user.ref_code,
        referrer_id=user.referrer_id,
        ref_levels_unlocked=user.ref_levels_unlocked,
        created_at=user.created_at,
        updated_at=user.updated_at,
        total_deposited=result["total_deposited"],
        total_withdrawn=result["total_withdrawn"],
        total_claimed=result["total_claimed"],
        total_ref_earned=result["total_ref_earned"],
        active_pets_count=result["active_pets_count"],
        referrals_count=result["referrals_count"],
    )


@router.post("/{user_id}/balance", response_model=BalanceAdjustResponse)
async def adjust_balance(
    user_id: int,
    request: BalanceAdjustRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Adjust user balance (admin or super_admin only)."""
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        tx, old_balance, new_balance = await adjust_user_balance(
            db,
            user=user,
            amount=request.amount,
            reason=request.reason,
            admin_id=admin.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="user.balance_adjust",
        target_type="user",
        target_id=user_id,
        details={
            "old_balance": str(old_balance),
            "new_balance": str(new_balance),
            "amount": str(request.amount),
            "reason": request.reason,
        },
        ip_address=get_client_ip(http_request),
    )

    return BalanceAdjustResponse(
        user_id=user_id,
        old_balance=old_balance,
        new_balance=new_balance,
        amount=request.amount,
        reason=request.reason,
        transaction_id=tx.id,
    )
