from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User,
    Transaction,
    DepositRequest,
    WithdrawRequest,
    UserPet,
    TxType,
    RequestStatus,
    PetStatus,
)


async def get_dashboard_stats(db: AsyncSession) -> dict:
    """Get dashboard statistics."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # === Users ===
    total_users = (await db.execute(
        select(func.count()).select_from(User)
    )).scalar() or 0

    new_users_today = (await db.execute(
        select(func.count()).where(User.created_at >= today_start)
    )).scalar() or 0

    new_users_week = (await db.execute(
        select(func.count()).where(User.created_at >= week_start)
    )).scalar() or 0

    # Active users today (had any transaction)
    active_users_today = (await db.execute(
        select(func.count(func.distinct(Transaction.user_id))).where(
            Transaction.created_at >= today_start
        )
    )).scalar() or 0

    # === Total balance ===
    total_balance = (await db.execute(
        select(func.coalesce(func.sum(User.balance_xpet), 0))
    )).scalar() or Decimal("0")

    # === Pending deposits ===
    pending_deposits = await db.execute(
        select(
            func.count(),
            func.coalesce(func.sum(DepositRequest.amount), 0)
        ).where(DepositRequest.status == RequestStatus.PENDING)
    )
    pending_dep_row = pending_deposits.one()
    pending_deposits_count = pending_dep_row[0] or 0
    pending_deposits_amount = pending_dep_row[1] or Decimal("0")

    # === Pending withdrawals ===
    pending_withdrawals = await db.execute(
        select(
            func.count(),
            func.coalesce(func.sum(WithdrawRequest.amount), 0)
        ).where(WithdrawRequest.status == RequestStatus.PENDING)
    )
    pending_wd_row = pending_withdrawals.one()
    pending_withdrawals_count = pending_wd_row[0] or 0
    pending_withdrawals_amount = pending_wd_row[1] or Decimal("0")

    # === Total deposited/withdrawn ===
    total_deposited = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.type == TxType.DEPOSIT
        )
    )).scalar() or Decimal("0")

    total_withdrawn = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.type == TxType.WITHDRAW
        )
    )).scalar() or Decimal("0")

    # === Pets ===
    total_pets_active = (await db.execute(
        select(func.count()).where(
            UserPet.status.in_([
                PetStatus.OWNED_IDLE,
                PetStatus.TRAINING,
                PetStatus.READY_TO_CLAIM,
            ])
        )
    )).scalar() or 0

    total_pets_evolved = (await db.execute(
        select(func.count()).where(UserPet.status == PetStatus.EVOLVED)
    )).scalar() or 0

    total_claimed = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.type == TxType.CLAIM
        )
    )).scalar() or Decimal("0")

    # === Referrals ===
    total_ref_rewards = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.type == TxType.REF_REWARD
        )
    )).scalar() or Decimal("0")

    # === Tasks ===
    total_task_rewards = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.type == TxType.TASK_REWARD
        )
    )).scalar() or Decimal("0")

    return {
        "total_users": total_users,
        "new_users_today": new_users_today,
        "new_users_week": new_users_week,
        "active_users_today": active_users_today,
        "total_balance_xpet": total_balance,
        "pending_deposits_count": pending_deposits_count,
        "pending_deposits_amount": pending_deposits_amount,
        "pending_withdrawals_count": pending_withdrawals_count,
        "pending_withdrawals_amount": pending_withdrawals_amount,
        "total_deposited": total_deposited,
        "total_withdrawn": total_withdrawn,
        "total_pets_active": total_pets_active,
        "total_pets_evolved": total_pets_evolved,
        "total_claimed_xpet": total_claimed,
        "total_ref_rewards_paid": total_ref_rewards,
        "total_task_rewards_paid": total_task_rewards,
    }
