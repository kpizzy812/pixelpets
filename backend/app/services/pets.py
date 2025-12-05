from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.pet import PetType, UserPet
from app.models.transaction import Transaction
from app.models.enums import PetStatus, PetLevel, TxType
from app.i18n import get_text as t

MAX_SLOTS = 3
SELL_REFUND_PERCENT = Decimal("0.85")
TRAINING_DURATION_HOURS = 24

LEVEL_ORDER = [PetLevel.BABY, PetLevel.ADULT, PetLevel.MYTHIC]


def get_next_level(current_level: PetLevel) -> Optional[PetLevel]:
    """Get next level or None if already max."""
    try:
        current_idx = LEVEL_ORDER.index(current_level)
        if current_idx < len(LEVEL_ORDER) - 1:
            return LEVEL_ORDER[current_idx + 1]
        return None
    except ValueError:
        return None


def calculate_max_profit(invested_total: Decimal, roi_cap_multiplier: Decimal) -> Decimal:
    """Calculate maximum profit for a pet."""
    return invested_total * roi_cap_multiplier


def calculate_daily_profit(invested_total: Decimal, daily_rate: Decimal) -> Decimal:
    """Calculate daily profit for a pet."""
    return invested_total * daily_rate


def calculate_upgrade_cost(level_prices: dict, next_level: PetLevel, invested_total: Decimal) -> Decimal:
    """Calculate cost to upgrade to next level."""
    next_level_price = Decimal(str(level_prices.get(next_level.value, 0)))
    return max(Decimal("0"), next_level_price - invested_total)


async def get_pet_catalog(db: AsyncSession) -> list[PetType]:
    """Get all active pet types."""
    result = await db.execute(
        select(PetType).where(PetType.is_active == True).order_by(PetType.base_price)
    )
    return list(result.scalars().all())


async def get_user_pets(db: AsyncSession, user_id: int) -> list[UserPet]:
    """Get all pets for a user (excluding sold)."""
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.user_id == user_id, UserPet.status != PetStatus.SOLD)
        .order_by(UserPet.slot_index)
    )
    return list(result.scalars().all())


async def get_free_slot(db: AsyncSession, user_id: int) -> Optional[int]:
    """Get first free slot index or None if all occupied."""
    result = await db.execute(
        select(UserPet.slot_index).where(
            UserPet.user_id == user_id,
            UserPet.status != PetStatus.SOLD,
        )
    )
    occupied_slots = set(result.scalars().all())

    for slot in range(MAX_SLOTS):
        if slot not in occupied_slots:
            return slot
    return None


async def buy_pet(
    db: AsyncSession,
    user: User,
    pet_type_id: int,
) -> tuple[UserPet, Decimal]:
    """
    Buy a pet for the user.
    Returns (new_pet, new_balance) or raises ValueError.
    """
    # Get pet type
    result = await db.execute(select(PetType).where(PetType.id == pet_type_id))
    pet_type = result.scalar_one_or_none()

    if not pet_type:
        raise ValueError(t("error.pet_type_not_found"))

    if not pet_type.is_active:
        raise ValueError(t("error.pet_type_not_available"))

    # Check balance
    if user.balance_xpet < pet_type.base_price:
        raise ValueError(t("error.insufficient_balance"))

    # Check free slots
    free_slot = await get_free_slot(db, user.id)
    if free_slot is None:
        raise ValueError(t("error.no_free_slots"))

    # Deduct balance
    user.balance_xpet -= pet_type.base_price

    # Create pet
    new_pet = UserPet(
        user_id=user.id,
        pet_type_id=pet_type_id,
        invested_total=pet_type.base_price,
        level=PetLevel.BABY,
        status=PetStatus.OWNED_IDLE,
        slot_index=free_slot,
    )
    db.add(new_pet)

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.PET_BUY,
        amount_xpet=-pet_type.base_price,
        meta={"pet_type_id": pet_type_id, "pet_name": pet_type.name},
    )
    db.add(tx)

    await db.commit()
    await db.refresh(new_pet)

    # Load pet_type relation
    result = await db.execute(
        select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == new_pet.id)
    )
    new_pet = result.scalar_one()

    return new_pet, user.balance_xpet


async def upgrade_pet(
    db: AsyncSession,
    user: User,
    pet_id: int,
) -> tuple[UserPet, Decimal]:
    """
    Upgrade a pet to the next level.
    Returns (upgraded_pet, new_balance) or raises ValueError.
    """
    # Get pet
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id, UserPet.user_id == user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise ValueError(t("error.pet_not_found"))

    if pet.status == PetStatus.SOLD:
        raise ValueError(t("error.pet_cannot_sell"))

    if pet.status == PetStatus.EVOLVED:
        raise ValueError(t("error.pet_cannot_sell"))

    # Check next level
    next_level = get_next_level(pet.level)
    if not next_level:
        raise ValueError(t("error.pet_already_max_level"))

    # Calculate upgrade cost
    upgrade_cost = calculate_upgrade_cost(pet.pet_type.level_prices, next_level, pet.invested_total)

    if user.balance_xpet < upgrade_cost:
        raise ValueError(t("error.insufficient_balance"))

    # Deduct balance and upgrade
    user.balance_xpet -= upgrade_cost
    pet.invested_total += upgrade_cost
    pet.level = next_level
    pet.updated_at = datetime.utcnow()

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.PET_UPGRADE,
        amount_xpet=-upgrade_cost,
        meta={"pet_id": pet_id, "new_level": next_level.value},
    )
    db.add(tx)

    await db.commit()
    await db.refresh(pet)

    return pet, user.balance_xpet


async def sell_pet(
    db: AsyncSession,
    user: User,
    pet_id: int,
) -> tuple[Decimal, Decimal]:
    """
    Sell a pet and get 85% refund.
    Returns (refund_amount, new_balance) or raises ValueError.
    """
    # Get pet
    result = await db.execute(
        select(UserPet).where(UserPet.id == pet_id, UserPet.user_id == user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise ValueError(t("error.pet_not_found"))

    if pet.status == PetStatus.SOLD:
        raise ValueError(t("error.pet_cannot_sell"))

    if pet.status == PetStatus.EVOLVED:
        raise ValueError(t("error.pet_cannot_sell"))

    # Calculate refund
    refund_amount = pet.invested_total * SELL_REFUND_PERCENT

    # Update pet status
    pet.status = PetStatus.SOLD
    pet.updated_at = datetime.utcnow()

    # Credit balance
    user.balance_xpet += refund_amount

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.SELL_REFUND,
        amount_xpet=refund_amount,
        meta={"pet_id": pet_id, "invested_total": str(pet.invested_total)},
    )
    db.add(tx)

    await db.commit()

    return refund_amount, user.balance_xpet


async def start_training(
    db: AsyncSession,
    user: User,
    pet_id: int,
) -> UserPet:
    """
    Start 24h training for a pet.
    Returns updated pet or raises ValueError.
    """
    result = await db.execute(
        select(UserPet).where(UserPet.id == pet_id, UserPet.user_id == user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise ValueError(t("error.pet_not_found"))

    if pet.status != PetStatus.OWNED_IDLE:
        raise ValueError(t("error.pet_not_idle"))

    now = datetime.utcnow()
    pet.status = PetStatus.TRAINING
    pet.training_started_at = now
    pet.training_ends_at = now + timedelta(hours=TRAINING_DURATION_HOURS)
    pet.updated_at = now

    await db.commit()
    await db.refresh(pet)

    return pet


def check_training_status(pet: UserPet) -> UserPet:
    """Check if training is complete and update status if needed."""
    if pet.status == PetStatus.TRAINING:
        if pet.training_ends_at and datetime.utcnow() >= pet.training_ends_at:
            pet.status = PetStatus.READY_TO_CLAIM
    return pet


async def claim_profit(
    db: AsyncSession,
    user: User,
    pet_id: int,
) -> dict:
    """
    Claim daily profit from a pet.
    Returns claim details or raises ValueError.
    """
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id, UserPet.user_id == user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise ValueError(t("error.pet_not_found"))

    # Check and update training status
    pet = check_training_status(pet)

    if pet.status != PetStatus.READY_TO_CLAIM:
        raise ValueError(t("error.training_not_complete"))

    # Calculate profit
    daily_profit_raw = calculate_daily_profit(pet.invested_total, pet.pet_type.daily_rate)
    max_profit = calculate_max_profit(pet.invested_total, pet.pet_type.roi_cap_multiplier)
    remaining_profit = max_profit - pet.profit_claimed
    profit_for_claim = min(daily_profit_raw, remaining_profit)

    # Update pet
    pet.profit_claimed += profit_for_claim
    pet.training_started_at = None
    pet.training_ends_at = None
    pet.updated_at = datetime.utcnow()

    # Check if evolved (reached cap)
    evolved = pet.profit_claimed >= max_profit
    if evolved:
        pet.status = PetStatus.EVOLVED
        pet.evolved_at = datetime.utcnow()
    else:
        pet.status = PetStatus.OWNED_IDLE

    # Credit user balance
    user.balance_xpet += profit_for_claim

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.CLAIM,
        amount_xpet=profit_for_claim,
        meta={"pet_id": pet_id, "pet_name": pet.pet_type.name},
    )
    db.add(tx)

    await db.commit()

    # Process referral rewards (after main commit)
    from app.services.referrals import process_referral_rewards
    await process_referral_rewards(db, user, profit_for_claim)

    result_data = {
        "profit_claimed": profit_for_claim,
        "new_balance": user.balance_xpet,
        "pet_status": pet.status,
        "total_profit_claimed": pet.profit_claimed,
        "max_profit": max_profit,
        "evolved": evolved,
    }

    if evolved:
        lifetime_days = (pet.evolved_at - pet.created_at).days if pet.evolved_at else 0
        result_data["hall_of_fame_entry"] = {
            "pet_name": pet.pet_type.name,
            "final_level": pet.level.value,
            "total_farmed": str(pet.profit_claimed),
            "lifetime_days": lifetime_days,
        }

    return result_data


async def get_hall_of_fame(db: AsyncSession, user_id: int) -> dict:
    """Get user's evolved pets (Hall of Fame)."""
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.user_id == user_id, UserPet.status == PetStatus.EVOLVED)
        .order_by(UserPet.evolved_at.desc())
    )
    pets = list(result.scalars().all())

    total_farmed = sum(pet.profit_claimed for pet in pets)

    return {
        "pets": pets,
        "total_pets_evolved": len(pets),
        "total_farmed_all_time": total_farmed,
    }
