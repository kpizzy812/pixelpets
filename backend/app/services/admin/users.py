from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import select, func, or_, desc, asc, String, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Transaction, UserPet, TxType, PetStatus


async def get_users_list(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    order_by: str = "created_at",
    order_desc: bool = True,
) -> Tuple[List[User], int]:
    """Get paginated list of users with optional search."""
    query = select(User)

    # Search filter (use func.lower for SQLite compatibility)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                cast(User.telegram_id, String).like(f"%{search}%"),
                func.lower(User.username).like(search_term),
                func.lower(User.ref_code).like(search_term),
                func.lower(User.first_name).like(search_term),
                func.lower(User.last_name).like(search_term),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Ordering
    order_column = getattr(User, order_by, User.created_at)
    if order_desc:
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(asc(order_column))

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    users = list(result.scalars().all())

    return users, total


async def get_user_detail(db: AsyncSession, user_id: int) -> Optional[dict]:
    """Get user with aggregated stats."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Get stats
    stats = await _get_user_stats(db, user_id)

    return {
        "user": user,
        **stats,
    }


async def _get_user_stats(db: AsyncSession, user_id: int) -> dict:
    """Get aggregated stats for a user."""
    # Total deposited
    deposit_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TxType.DEPOSIT,
        )
    )
    total_deposited = deposit_result.scalar() or Decimal("0")

    # Total withdrawn
    withdraw_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TxType.WITHDRAW,
        )
    )
    total_withdrawn = withdraw_result.scalar() or Decimal("0")

    # Total claimed
    claim_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TxType.CLAIM,
        )
    )
    total_claimed = claim_result.scalar() or Decimal("0")

    # Total ref earned
    ref_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount_xpet), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TxType.REF_REWARD,
        )
    )
    total_ref_earned = ref_result.scalar() or Decimal("0")

    # Active pets count
    pets_result = await db.execute(
        select(func.count()).where(
            UserPet.user_id == user_id,
            UserPet.status.in_([
                PetStatus.OWNED_IDLE,
                PetStatus.TRAINING,
                PetStatus.READY_TO_CLAIM,
            ]),
        )
    )
    active_pets_count = pets_result.scalar() or 0

    # Referrals count
    refs_result = await db.execute(
        select(func.count()).where(User.referrer_id == user_id)
    )
    referrals_count = refs_result.scalar() or 0

    return {
        "total_deposited": total_deposited,
        "total_withdrawn": total_withdrawn,
        "total_claimed": total_claimed,
        "total_ref_earned": total_ref_earned,
        "active_pets_count": active_pets_count,
        "referrals_count": referrals_count,
    }


async def adjust_user_balance(
    db: AsyncSession,
    user: User,
    amount: Decimal,
    reason: str,
    admin_id: int,
) -> Tuple[Transaction, Decimal, Decimal]:
    """
    Adjust user balance. Returns (transaction, old_balance, new_balance).
    Amount can be positive (add) or negative (subtract).
    """
    old_balance = user.balance_xpet
    new_balance = old_balance + amount

    if new_balance < 0:
        raise ValueError("Resulting balance cannot be negative")

    user.balance_xpet = new_balance

    # Create transaction record
    tx = Transaction(
        user_id=user.id,
        type=TxType.ADMIN_ADJUST,
        amount_xpet=amount,
        meta={
            "reason": reason,
            "admin_id": admin_id,
            "old_balance": str(old_balance),
            "new_balance": str(new_balance),
        },
    )
    db.add(tx)

    await db.commit()
    await db.refresh(tx)

    return tx, old_balance, new_balance
