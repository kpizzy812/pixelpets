"""
Boost service: Snacks, ROI Boosts, Auto-Claim subscriptions.

Pricing model:
- Snacks: Cost = bonus% × 60% of extra profit (player gets 40% net benefit)
- ROI Boost: Cost = 25% of extra profit (player gets 75% but over time, system gets 25% NOW)
- Auto-Claim: $5/month + 3% commission from each auto-claim
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.pet import UserPet, PetType
from app.models.boost import PetSnack, PetRoiBoost, AutoClaimSubscription, BoostTransaction
from app.models.transaction import Transaction
from app.models.enums import SnackType, BoostType, TxType, PetStatus
from app.i18n import get_text as t


# ============== SNACK CONFIGURATION ==============

SNACK_CONFIG = {
    SnackType.COOKIE: {
        "bonus_percent": Decimal("0.10"),  # +10%
        "cost_coefficient": Decimal("0.60"),  # Pay 60% of bonus
    },
    SnackType.STEAK: {
        "bonus_percent": Decimal("0.25"),  # +25%
        "cost_coefficient": Decimal("0.55"),  # Pay 55% of bonus
    },
    SnackType.CAKE: {
        "bonus_percent": Decimal("0.50"),  # +50%
        "cost_coefficient": Decimal("0.50"),  # Pay 50% of bonus
    },
}

# ROI Boost: Player pays 25% of extra profit upfront
ROI_BOOST_COST_COEFFICIENT = Decimal("0.25")

# Auto-Claim subscription
AUTO_CLAIM_MONTHLY_COST = Decimal("5.00")
AUTO_CLAIM_COMMISSION_PERCENT = Decimal("0.03")  # 3%


# ============== SNACK FUNCTIONS ==============

def calculate_snack_price(
    pet: UserPet,
    snack_type: SnackType,
) -> tuple[Decimal, Decimal]:
    """
    Calculate snack price based on pet's daily profit.

    Formula: cost = invested × daily_rate × bonus% × cost_coefficient

    Returns: (cost, bonus_percent)
    """
    config = SNACK_CONFIG[snack_type]
    bonus_percent = config["bonus_percent"]
    cost_coefficient = config["cost_coefficient"]

    # Daily profit = invested × daily_rate
    daily_profit = pet.invested_total * pet.pet_type.daily_rate

    # Bonus amount = daily_profit × bonus%
    bonus_amount = daily_profit * bonus_percent

    # Cost = bonus_amount × cost_coefficient
    cost = bonus_amount * cost_coefficient

    # Minimum cost of 0.01 XPET
    cost = max(cost, Decimal("0.01"))

    return cost, bonus_percent


async def get_active_snack(db: AsyncSession, pet_id: int) -> Optional[PetSnack]:
    """Get active (unused) snack for a pet."""
    result = await db.execute(
        select(PetSnack).where(
            and_(
                PetSnack.pet_id == pet_id,
                PetSnack.is_used == False,
            )
        )
    )
    return result.scalar_one_or_none()


async def buy_snack(
    db: AsyncSession,
    user: User,
    pet_id: int,
    snack_type: SnackType,
) -> tuple[PetSnack, Decimal]:
    """
    Buy a snack for a pet.

    Returns: (snack, new_balance)
    Raises ValueError if cannot buy.
    """
    # Get pet with type loaded
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id, UserPet.user_id == user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise ValueError(t("error.pet_not_found"))

    if pet.status in [PetStatus.SOLD, PetStatus.EVOLVED]:
        raise ValueError(t("error.pet_cannot_boost"))

    # Check if pet already has active snack
    existing_snack = await get_active_snack(db, pet_id)
    if existing_snack:
        raise ValueError(t("error.snack_already_active"))

    # Calculate price
    cost, bonus_percent = calculate_snack_price(pet, snack_type)

    # Check balance
    if user.balance_xpet < cost:
        raise ValueError(t("error.insufficient_balance"))

    # Deduct balance
    user.balance_xpet -= cost

    # Create snack
    snack = PetSnack(
        pet_id=pet_id,
        user_id=user.id,
        snack_type=snack_type,
        bonus_percent=bonus_percent,
        cost_xpet=cost,
    )
    db.add(snack)

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.BOOST_PURCHASE,
        amount_xpet=-cost,
        meta={
            "boost_type": "snack",
            "snack_type": snack_type.value,
            "pet_id": pet_id,
            "bonus_percent": str(bonus_percent),
        },
    )
    db.add(tx)

    # Record boost transaction
    boost_tx = BoostTransaction(
        user_id=user.id,
        boost_type=BoostType.SNACK,
        pet_id=pet_id,
        amount_xpet=-cost,
        description=f"Bought {snack_type.value} for pet #{pet_id}",
    )
    db.add(boost_tx)

    await db.commit()
    await db.refresh(snack)

    return snack, user.balance_xpet


async def use_snack(db: AsyncSession, snack: PetSnack) -> None:
    """Mark snack as used (called during claim)."""
    snack.is_used = True
    snack.used_at = datetime.now(timezone.utc)
    await db.commit()


async def get_snack_prices(db: AsyncSession, pet_id: int) -> dict:
    """Get all snack prices for a pet."""
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        return {}

    prices = {}
    for snack_type in SnackType:
        cost, bonus_percent = calculate_snack_price(pet, snack_type)
        daily_profit = pet.invested_total * pet.pet_type.daily_rate
        bonus_amount = daily_profit * bonus_percent

        prices[snack_type.value] = {
            "cost": cost,
            "bonus_percent": bonus_percent * 100,  # As percentage
            "bonus_amount": bonus_amount,
            "net_benefit": bonus_amount - cost,
        }

    return prices


# ============== ROI BOOST FUNCTIONS ==============

def calculate_roi_boost_price(
    pet: UserPet,
    boost_percent: Decimal,
) -> tuple[Decimal, Decimal]:
    """
    Calculate ROI boost price.

    Formula:
    - Extra profit = invested × boost%
    - Cost = extra_profit × 25%

    Returns: (cost, extra_profit)
    """
    extra_profit = pet.invested_total * boost_percent
    cost = extra_profit * ROI_BOOST_COST_COEFFICIENT

    # Minimum cost of 0.05 XPET
    cost = max(cost, Decimal("0.05"))

    return cost, extra_profit


async def get_pet_total_roi_boost(db: AsyncSession, pet_id: int) -> Decimal:
    """Get total ROI boost applied to a pet."""
    result = await db.execute(
        select(PetRoiBoost).where(PetRoiBoost.pet_id == pet_id)
    )
    boosts = result.scalars().all()
    return sum(b.boost_percent for b in boosts)


async def buy_roi_boost(
    db: AsyncSession,
    user: User,
    pet_id: int,
    boost_percent: Decimal,
) -> tuple[PetRoiBoost, Decimal]:
    """
    Buy a permanent ROI boost for a pet.

    Returns: (boost, new_balance)
    Raises ValueError if cannot buy.
    """
    # Validate boost percent (5%, 10%, 15%, 20%)
    valid_boosts = [Decimal("0.05"), Decimal("0.10"), Decimal("0.15"), Decimal("0.20")]
    if boost_percent not in valid_boosts:
        raise ValueError(t("error.invalid_boost_percent"))

    # Get pet with type loaded
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id, UserPet.user_id == user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise ValueError(t("error.pet_not_found"))

    if pet.status in [PetStatus.SOLD, PetStatus.EVOLVED]:
        raise ValueError(t("error.pet_cannot_boost"))

    # Check total boost doesn't exceed 50%
    current_boost = await get_pet_total_roi_boost(db, pet_id)
    if current_boost + boost_percent > Decimal("0.50"):
        raise ValueError(t("error.roi_boost_max_exceeded"))

    # Calculate price
    cost, extra_profit = calculate_roi_boost_price(pet, boost_percent)

    # Check balance
    if user.balance_xpet < cost:
        raise ValueError(t("error.insufficient_balance"))

    # Deduct balance
    user.balance_xpet -= cost

    # Create boost
    boost = PetRoiBoost(
        pet_id=pet_id,
        user_id=user.id,
        boost_percent=boost_percent,
        extra_profit=extra_profit,
        cost_xpet=cost,
    )
    db.add(boost)

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.BOOST_PURCHASE,
        amount_xpet=-cost,
        meta={
            "boost_type": "roi_boost",
            "boost_percent": str(boost_percent),
            "pet_id": pet_id,
            "extra_profit": str(extra_profit),
        },
    )
    db.add(tx)

    # Record boost transaction
    boost_tx = BoostTransaction(
        user_id=user.id,
        boost_type=BoostType.ROI_BOOST,
        pet_id=pet_id,
        amount_xpet=-cost,
        description=f"Bought +{int(boost_percent * 100)}% ROI boost for pet #{pet_id}",
    )
    db.add(boost_tx)

    await db.commit()
    await db.refresh(boost)

    return boost, user.balance_xpet


async def get_roi_boost_prices(db: AsyncSession, pet_id: int) -> dict:
    """Get all ROI boost prices for a pet."""
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        return {}

    current_boost = await get_pet_total_roi_boost(db, pet_id)

    prices = {}
    for boost_pct in [Decimal("0.05"), Decimal("0.10"), Decimal("0.15"), Decimal("0.20")]:
        cost, extra_profit = calculate_roi_boost_price(pet, boost_pct)
        can_buy = current_boost + boost_pct <= Decimal("0.50")

        prices[f"+{int(boost_pct * 100)}%"] = {
            "cost": cost,
            "boost_percent": boost_pct * 100,
            "extra_profit": extra_profit,
            "net_benefit": extra_profit - cost,
            "can_buy": can_buy,
        }

    return {
        "current_boost": current_boost * 100,
        "max_boost": Decimal("50"),
        "options": prices,
    }


# ============== AUTO-CLAIM FUNCTIONS ==============

async def get_active_auto_claim(db: AsyncSession, user_id: int) -> Optional[AutoClaimSubscription]:
    """Get active auto-claim subscription for user."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(AutoClaimSubscription).where(
            and_(
                AutoClaimSubscription.user_id == user_id,
                AutoClaimSubscription.is_active == True,
                AutoClaimSubscription.expires_at > now,
            )
        )
    )
    return result.scalar_one_or_none()


async def buy_auto_claim(
    db: AsyncSession,
    user: User,
    months: int = 1,
) -> tuple[AutoClaimSubscription, Decimal]:
    """
    Buy auto-claim subscription.

    Returns: (subscription, new_balance)
    Raises ValueError if cannot buy.
    """
    if months not in [1, 3, 6]:
        raise ValueError(t("error.invalid_subscription_period"))

    # Check if already has active subscription
    existing = await get_active_auto_claim(db, user.id)
    if existing:
        raise ValueError(t("error.auto_claim_already_active"))

    # Calculate cost (no discount for longer periods for now)
    cost = AUTO_CLAIM_MONTHLY_COST * months

    # Check balance
    if user.balance_xpet < cost:
        raise ValueError(t("error.insufficient_balance"))

    # Deduct balance
    user.balance_xpet -= cost

    # Create subscription
    now = datetime.now(timezone.utc)
    subscription = AutoClaimSubscription(
        user_id=user.id,
        starts_at=now,
        expires_at=now + timedelta(days=30 * months),
        cost_xpet=cost,
        commission_percent=AUTO_CLAIM_COMMISSION_PERCENT,
    )
    db.add(subscription)

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.BOOST_PURCHASE,
        amount_xpet=-cost,
        meta={
            "boost_type": "auto_claim",
            "months": months,
        },
    )
    db.add(tx)

    # Record boost transaction
    boost_tx = BoostTransaction(
        user_id=user.id,
        boost_type=BoostType.AUTO_CLAIM,
        amount_xpet=-cost,
        description=f"Bought {months}-month auto-claim subscription",
    )
    db.add(boost_tx)

    await db.commit()
    await db.refresh(subscription)

    return subscription, user.balance_xpet


async def record_auto_claim_commission(
    db: AsyncSession,
    subscription: AutoClaimSubscription,
    claim_amount: Decimal,
) -> Decimal:
    """
    Record commission from auto-claim.
    Returns commission amount.
    """
    commission = claim_amount * subscription.commission_percent
    subscription.total_claims += 1
    subscription.total_commission += commission

    await db.commit()

    return commission


async def get_auto_claim_status(db: AsyncSession, user_id: int) -> dict:
    """Get auto-claim status for user."""
    subscription = await get_active_auto_claim(db, user_id)

    if not subscription:
        return {
            "is_active": False,
            "monthly_cost": AUTO_CLAIM_MONTHLY_COST,
            "commission_percent": AUTO_CLAIM_COMMISSION_PERCENT * 100,
        }

    return {
        "is_active": True,
        "expires_at": subscription.expires_at.isoformat(),
        "days_remaining": (subscription.expires_at.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days,
        "total_claims": subscription.total_claims,
        "total_commission": subscription.total_commission,
        "commission_percent": subscription.commission_percent * 100,
    }


# ============== BOOST STATS ==============

async def get_user_boost_stats(db: AsyncSession, user_id: int) -> dict:
    """Get boost statistics for a user."""
    # Total spent on boosts
    result = await db.execute(
        select(BoostTransaction).where(
            and_(
                BoostTransaction.user_id == user_id,
                BoostTransaction.amount_xpet < 0,
            )
        )
    )
    purchases = result.scalars().all()
    total_spent = sum(abs(tx.amount_xpet) for tx in purchases)

    # Count by type
    snack_count = sum(1 for tx in purchases if tx.boost_type == BoostType.SNACK)
    roi_boost_count = sum(1 for tx in purchases if tx.boost_type == BoostType.ROI_BOOST)
    auto_claim_count = sum(1 for tx in purchases if tx.boost_type == BoostType.AUTO_CLAIM)

    return {
        "total_spent": total_spent,
        "snacks_purchased": snack_count,
        "roi_boosts_purchased": roi_boost_count,
        "auto_claim_subscriptions": auto_claim_count,
    }
