"""Lucky Spin service - wheel of fortune mechanics."""
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.spin import SpinReward, UserSpin
from app.models.transaction import Transaction
from app.models.enums import SpinRewardType, TxType
from app.i18n import get_text as t

# Spin costs
FREE_SPIN_COOLDOWN_HOURS = 24
PAID_SPIN_COST = Decimal("1")  # $1 per paid spin


async def get_spin_rewards(db: AsyncSession) -> list[SpinReward]:
    """Get all active spin rewards ordered for wheel display."""
    result = await db.execute(
        select(SpinReward)
        .where(SpinReward.is_active == True)
        .order_by(SpinReward.order)
    )
    return list(result.scalars().all())


async def get_last_free_spin(db: AsyncSession, user_id: int) -> Optional[UserSpin]:
    """Get user's last free spin."""
    result = await db.execute(
        select(UserSpin)
        .where(
            and_(
                UserSpin.user_id == user_id,
                UserSpin.is_free_spin == True,
            )
        )
        .order_by(UserSpin.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def can_free_spin(db: AsyncSession, user_id: int) -> tuple[bool, Optional[datetime]]:
    """
    Check if user can do a free spin.
    Returns (can_spin, next_free_spin_time).
    """
    last_spin = await get_last_free_spin(db, user_id)

    if not last_spin:
        return True, None

    next_spin_time = last_spin.created_at + timedelta(hours=FREE_SPIN_COOLDOWN_HOURS)
    now = datetime.utcnow()

    if now >= next_spin_time:
        return True, None

    return False, next_spin_time


async def get_spin_status(db: AsyncSession, user_id: int) -> dict:
    """Get user's spin status including free spin availability."""
    can_spin, next_free_time = await can_free_spin(db, user_id)

    # Count total spins today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(UserSpin.id)).where(
            and_(
                UserSpin.user_id == user_id,
                UserSpin.created_at >= today_start,
            )
        )
    )
    spins_today = result.scalar() or 0

    # Total winnings today
    winnings_result = await db.execute(
        select(func.sum(UserSpin.reward_value)).where(
            and_(
                UserSpin.user_id == user_id,
                UserSpin.created_at >= today_start,
                UserSpin.reward_type == SpinRewardType.XPET,
            )
        )
    )
    winnings_today = winnings_result.scalar() or Decimal("0")

    return {
        "can_free_spin": can_spin,
        "next_free_spin_at": next_free_time.isoformat() if next_free_time else None,
        "paid_spin_cost": PAID_SPIN_COST,
        "spins_today": spins_today,
        "winnings_today": winnings_today,
    }


def select_random_reward(rewards: list[SpinReward]) -> SpinReward:
    """Select a random reward based on probability weights."""
    if not rewards:
        raise ValueError(t("error.spin_no_rewards"))

    weights = [float(r.probability) for r in rewards]
    return random.choices(rewards, weights=weights, k=1)[0]


async def perform_spin(
    db: AsyncSession,
    user: User,
    is_free: bool = False,
) -> tuple[UserSpin, SpinReward, Decimal]:
    """
    Perform a spin and return results.
    Returns (user_spin, reward, amount_won).
    Raises ValueError if spin not allowed.
    """
    # Check if free spin is available
    if is_free:
        can_spin, next_time = await can_free_spin(db, user.id)
        if not can_spin:
            raise ValueError(t("error.spin_cooldown", time=next_time.isoformat()))
    else:
        # Paid spin - check balance
        if user.balance_xpet < PAID_SPIN_COST:
            raise ValueError(t("error.insufficient_balance"))

        # Deduct cost
        user.balance_xpet -= PAID_SPIN_COST

        # Record spin cost transaction
        tx = Transaction(
            user_id=user.id,
            type=TxType.SPIN_COST,
            amount_xpet=-PAID_SPIN_COST,
            meta={"type": "paid_spin"},
        )
        db.add(tx)

    # Get rewards and select random one
    rewards = await get_spin_rewards(db)
    if not rewards:
        raise ValueError(t("error.spin_no_config"))

    reward = select_random_reward(rewards)

    # Calculate actual reward value
    amount_won = Decimal("0")
    if reward.reward_type == SpinRewardType.XPET:
        amount_won = reward.value
        user.balance_xpet += amount_won

        # Record win transaction
        tx = Transaction(
            user_id=user.id,
            type=TxType.SPIN_WIN,
            amount_xpet=amount_won,
            meta={
                "reward_id": reward.id,
                "reward_label": reward.label,
                "is_free_spin": is_free,
            },
        )
        db.add(tx)

    # Record the spin
    user_spin = UserSpin(
        user_id=user.id,
        reward_id=reward.id,
        reward_type=reward.reward_type,
        reward_value=amount_won,
        cost_xpet=Decimal("0") if is_free else PAID_SPIN_COST,
        is_free_spin=is_free,
    )
    db.add(user_spin)

    await db.commit()
    await db.refresh(user_spin)

    return user_spin, reward, amount_won


async def get_spin_history(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
) -> list[UserSpin]:
    """Get user's recent spin history."""
    result = await db.execute(
        select(UserSpin)
        .where(UserSpin.user_id == user_id)
        .order_by(UserSpin.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_spin_stats(db: AsyncSession) -> dict:
    """Get global spin statistics (for admin)."""
    # Total spins
    total_result = await db.execute(select(func.count(UserSpin.id)))
    total_spins = total_result.scalar() or 0

    # Total paid out
    payout_result = await db.execute(
        select(func.sum(UserSpin.reward_value)).where(
            UserSpin.reward_type == SpinRewardType.XPET
        )
    )
    total_paid = payout_result.scalar() or Decimal("0")

    # Total collected from paid spins
    collected_result = await db.execute(
        select(func.sum(UserSpin.cost_xpet)).where(
            UserSpin.is_free_spin == False
        )
    )
    total_collected = collected_result.scalar() or Decimal("0")

    # Spins today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(UserSpin.id)).where(
            UserSpin.created_at >= today_start
        )
    )
    spins_today = today_result.scalar() or 0

    return {
        "total_spins": total_spins,
        "total_paid_out": total_paid,
        "total_collected": total_collected,
        "profit": total_collected - total_paid,
        "spins_today": spins_today,
    }
