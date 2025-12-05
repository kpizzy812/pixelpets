from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PetType


async def get_pet_types(
    db: AsyncSession,
    include_inactive: bool = False,
) -> List[PetType]:
    """Get all pet types."""
    query = select(PetType).order_by(PetType.base_price)

    if not include_inactive:
        query = query.where(PetType.is_active == True)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_pet_type_by_id(
    db: AsyncSession,
    pet_type_id: int,
) -> Optional[PetType]:
    """Get pet type by ID."""
    result = await db.execute(
        select(PetType).where(PetType.id == pet_type_id)
    )
    return result.scalar_one_or_none()


async def create_pet_type(
    db: AsyncSession,
    name: str,
    base_price: Decimal,
    daily_rate: Decimal,
    roi_cap_multiplier: Decimal,
    level_prices: dict,
    emoji: Optional[str] = None,
    is_active: bool = True,
) -> PetType:
    """Create new pet type."""
    pet_type = PetType(
        name=name,
        emoji=emoji,
        base_price=base_price,
        daily_rate=daily_rate,
        roi_cap_multiplier=roi_cap_multiplier,
        level_prices=level_prices,
        is_active=is_active,
    )
    db.add(pet_type)
    await db.commit()
    await db.refresh(pet_type)
    return pet_type


async def update_pet_type(
    db: AsyncSession,
    pet_type: PetType,
    name: Optional[str] = None,
    emoji: Optional[str] = None,
    base_price: Optional[Decimal] = None,
    daily_rate: Optional[Decimal] = None,
    roi_cap_multiplier: Optional[Decimal] = None,
    level_prices: Optional[dict] = None,
    is_active: Optional[bool] = None,
) -> PetType:
    """Update pet type."""
    if name is not None:
        pet_type.name = name
    if emoji is not None:
        pet_type.emoji = emoji
    if base_price is not None:
        pet_type.base_price = base_price
    if daily_rate is not None:
        pet_type.daily_rate = daily_rate
    if roi_cap_multiplier is not None:
        pet_type.roi_cap_multiplier = roi_cap_multiplier
    if level_prices is not None:
        pet_type.level_prices = level_prices
    if is_active is not None:
        pet_type.is_active = is_active

    await db.commit()
    await db.refresh(pet_type)
    return pet_type


async def delete_pet_type(
    db: AsyncSession,
    pet_type: PetType,
    soft_delete: bool = True,
) -> bool:
    """
    Delete pet type.
    By default, soft-delete (set is_active=False).
    """
    if soft_delete:
        pet_type.is_active = False
        await db.commit()
    else:
        await db.delete(pet_type)
        await db.commit()

    return True
