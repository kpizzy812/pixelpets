from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.pet import UserPet
from app.models.transaction import Transaction
from app.models.referral import ReferralStats, ReferralReward
from app.models.enums import TxType, PetStatus
from app.services.admin.config import get_config_value


async def get_referral_percentages(db: AsyncSession) -> dict[int, Decimal]:
    """
    Get referral percentages from SystemConfig.
    Returns dict: {level: Decimal percent} e.g. {1: Decimal("0.20"), ...}
    """
    percentages = await get_config_value(db, "referral_percentages")
    return {
        int(level): Decimal(str(percent)) / 100
        for level, percent in percentages.items()
    }


async def get_referral_thresholds(db: AsyncSession) -> dict[int, int]:
    """
    Get referral unlock thresholds from SystemConfig.
    Returns dict: {level: min_active_refs} e.g. {1: 0, 2: 3, ...}
    """
    thresholds = await get_config_value(db, "referral_unlock_thresholds")
    return {int(level): int(threshold) for level, threshold in thresholds.items()}


async def get_bot_username(db: AsyncSession) -> str:
    """Get bot username from SystemConfig."""
    return await get_config_value(db, "bot_username", "pixelpets_bot")


async def get_active_referrals_count(db: AsyncSession, user_id: int) -> int:
    """
    Count active referrals (users who bought at least 1 pet).
    Only counts direct referrals (level 1).
    """
    # Find direct referrals who have pets
    result = await db.execute(
        select(func.count(User.id.distinct()))
        .select_from(User)
        .join(UserPet, User.id == UserPet.user_id)
        .where(
            User.referrer_id == user_id,
            UserPet.status != PetStatus.SOLD,
        )
    )
    return result.scalar() or 0


async def update_user_ref_levels(db: AsyncSession, user: User) -> int:
    """
    Update user's unlocked referral levels based on active referrals count.
    Returns new ref_levels_unlocked value.
    """
    active_count = await get_active_referrals_count(db, user.id)
    thresholds = await get_referral_thresholds(db)

    new_levels = 1  # Level 1 always unlocked
    for level in range(2, 6):
        min_refs = thresholds.get(level, 0)
        if active_count >= min_refs:
            new_levels = level
        else:
            break

    if user.ref_levels_unlocked != new_levels:
        user.ref_levels_unlocked = new_levels
        await db.commit()

    return new_levels


async def get_referrer_chain(db: AsyncSession, user_id: int, max_levels: int = 5) -> list[User]:
    """
    Get chain of referrers up to max_levels.
    Returns list of users from level 1 (direct referrer) to level 5.
    """
    chain = []
    current_id = user_id

    for _ in range(max_levels):
        result = await db.execute(
            select(User).where(User.id == current_id)
        )
        current_user = result.scalar_one_or_none()

        if not current_user or not current_user.referrer_id:
            break

        # Get referrer
        result = await db.execute(
            select(User).where(User.id == current_user.referrer_id)
        )
        referrer = result.scalar_one_or_none()

        if not referrer:
            break

        chain.append(referrer)
        current_id = referrer.id

    return chain


async def process_referral_rewards(
    db: AsyncSession,
    claiming_user: User,
    claim_amount: Decimal,
) -> list[dict]:
    """
    Process referral rewards when a user claims profit.
    Distributes rewards to referrers up to 5 levels.
    Returns list of rewards distributed.
    """
    rewards_distributed = []

    # Get referrer chain
    referrer_chain = await get_referrer_chain(db, claiming_user.id)

    # Get percentages from config
    percentages = await get_referral_percentages(db)

    for level, referrer in enumerate(referrer_chain, start=1):
        # Check if this level is unlocked for the referrer
        if referrer.ref_levels_unlocked < level:
            continue

        # Calculate reward
        percent = percentages.get(level, Decimal("0"))
        reward_amount = claim_amount * percent

        if reward_amount <= 0:
            continue

        # Credit referrer balance
        referrer.balance_xpet += reward_amount

        # Record referral reward
        ref_reward = ReferralReward(
            from_user_id=claiming_user.id,
            to_user_id=referrer.id,
            level=level,
            claim_amount=claim_amount,
            reward_amount=reward_amount,
        )
        db.add(ref_reward)

        # Record transaction
        tx = Transaction(
            user_id=referrer.id,
            type=TxType.REF_REWARD,
            amount_xpet=reward_amount,
            meta={
                "from_user_id": claiming_user.id,
                "level": level,
                "claim_amount": str(claim_amount),
            },
        )
        db.add(tx)

        # Update referral stats
        await update_referral_stats(db, referrer.id, level, reward_amount)

        rewards_distributed.append({
            "referrer_id": referrer.id,
            "level": level,
            "reward_amount": reward_amount,
        })

    await db.commit()
    return rewards_distributed


async def update_referral_stats(
    db: AsyncSession,
    user_id: int,
    level: int,
    reward_amount: Decimal,
) -> None:
    """Update referral stats for a user."""
    result = await db.execute(
        select(ReferralStats).where(ReferralStats.user_id == user_id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        stats = ReferralStats(user_id=user_id)
        db.add(stats)

    # Update level-specific earned
    level_earned_attr = f"level_{level}_earned"
    current_earned = getattr(stats, level_earned_attr, None) or Decimal("0")
    setattr(stats, level_earned_attr, current_earned + reward_amount)

    # Update total
    stats.total_earned = (stats.total_earned or Decimal("0")) + reward_amount


async def get_referral_stats(db: AsyncSession, user: User) -> dict:
    """Get detailed referral statistics for a user."""
    # Get or create stats
    result = await db.execute(
        select(ReferralStats).where(ReferralStats.user_id == user.id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        stats = ReferralStats(user_id=user.id)
        db.add(stats)
        await db.commit()
        await db.refresh(stats)

    # Count referrals per level
    level_counts = {}
    for level in range(1, 6):
        level_counts[level] = await get_level_referrals_count(db, user.id, level)

    # Get active referrals count
    active_count = await get_active_referrals_count(db, user.id)

    # Update ref levels if needed
    await update_user_ref_levels(db, user)

    # Get config from SystemConfig
    percentages = await get_referral_percentages(db)
    thresholds = await get_referral_thresholds(db)

    # Build levels info
    levels = []
    for level in range(1, 6):
        percent = percentages.get(level, Decimal("0"))
        min_refs = thresholds.get(level, 0)
        unlocked = user.ref_levels_unlocked >= level
        level_earned_attr = f"level_{level}_earned"

        level_info = {
            "level": level,
            "percent": int(percent * 100),
            "unlocked": unlocked,
            "referrals_count": level_counts[level],
            "earned_xpet": getattr(stats, level_earned_attr, Decimal("0")),
        }

        if level > 1:
            level_info["unlock_requirement"] = min_refs
            if not unlocked:
                level_info["progress"] = f"{active_count}/{min_refs} active"

        levels.append(level_info)

    return {
        "ref_code": user.ref_code,
        "total_earned_xpet": stats.total_earned,
        "levels_unlocked": user.ref_levels_unlocked,
        "levels": levels,
        "active_referrals_count": active_count,
    }


async def get_level_referrals_count(db: AsyncSession, user_id: int, level: int) -> int:
    """
    Count referrals at a specific level in the tree.
    Level 1 = direct referrals, Level 2 = referrals of referrals, etc.
    """
    if level == 1:
        result = await db.execute(
            select(func.count(User.id)).where(User.referrer_id == user_id)
        )
        return result.scalar() or 0

    # For deeper levels, we need recursive counting
    # This is a simplified version - for production, consider using recursive CTE
    current_level_ids = [user_id]

    for _ in range(level - 1):
        if not current_level_ids:
            return 0

        result = await db.execute(
            select(User.id).where(User.referrer_id.in_(current_level_ids))
        )
        current_level_ids = list(result.scalars().all())

    if not current_level_ids:
        return 0

    result = await db.execute(
        select(func.count(User.id)).where(User.referrer_id.in_(current_level_ids))
    )
    return result.scalar() or 0


async def generate_ref_link(db: AsyncSession, ref_code: str) -> str:
    """Generate Telegram deep link for referral that opens Mini App directly."""
    bot_username = await get_bot_username(db)
    # Use startapp= to open Mini App directly, with ref_ prefix for referral code
    return f"https://t.me/{bot_username}?startapp=ref_{ref_code}"


def get_share_text() -> str:
    """Get default share text for referral link."""
    return "Join Pixel Pets and earn USDT with your virtual pets! 🐾"
