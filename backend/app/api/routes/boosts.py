"""
API routes for boost system: Snacks, ROI Boosts, Auto-Claim.
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.pet import UserPet
from app.schemas.boost import (
    SnackPricesResponse,
    SnackPriceInfo,
    BuySnackRequest,
    BuySnackResponse,
    RoiBoostPricesResponse,
    RoiBoostPriceInfo,
    BuyRoiBoostRequest,
    BuyRoiBoostResponse,
    AutoClaimStatusResponse,
    BuyAutoClaimRequest,
    BuyAutoClaimResponse,
    BoostStatsResponse,
)
from app.services.boosts import (
    get_snack_prices,
    buy_snack,
    get_active_snack,
    get_roi_boost_prices,
    buy_roi_boost,
    get_pet_total_roi_boost,
    get_auto_claim_status,
    buy_auto_claim,
    get_user_boost_stats,
    AUTO_CLAIM_MONTHLY_COST,
    AUTO_CLAIM_COMMISSION_PERCENT,
)

router = APIRouter(prefix="/boosts", tags=["boosts"])


# ============== SNACK ROUTES ==============

@router.get("/snacks/prices/{pet_id}", response_model=SnackPricesResponse)
async def get_snack_prices_endpoint(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get snack prices for a pet."""
    # Verify pet belongs to user
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type))
        .where(UserPet.id == pet_id, UserPet.user_id == current_user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

    prices = await get_snack_prices(db, pet_id)
    active_snack = await get_active_snack(db, pet_id)

    daily_profit = pet.invested_total * pet.pet_type.daily_rate

    return SnackPricesResponse(
        pet_id=pet_id,
        daily_profit=daily_profit,
        active_snack=active_snack.snack_type.value if active_snack else None,
        prices={
            k: SnackPriceInfo(**v) for k, v in prices.items()
        },
    )


@router.post("/snacks/buy", response_model=BuySnackResponse)
async def buy_snack_endpoint(
    request: BuySnackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Buy a snack for a pet."""
    try:
        snack, new_balance = await buy_snack(
            db, current_user, request.pet_id, request.snack_type
        )
        return BuySnackResponse(
            snack_id=snack.id,
            snack_type=snack.snack_type,
            bonus_percent=snack.bonus_percent * 100,
            cost=snack.cost_xpet,
            new_balance=new_balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== ROI BOOST ROUTES ==============

@router.get("/roi/prices/{pet_id}", response_model=RoiBoostPricesResponse)
async def get_roi_boost_prices_endpoint(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ROI boost prices for a pet."""
    # Verify pet belongs to user
    result = await db.execute(
        select(UserPet).where(UserPet.id == pet_id, UserPet.user_id == current_user.id)
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

    prices_data = await get_roi_boost_prices(db, pet_id)

    return RoiBoostPricesResponse(
        pet_id=pet_id,
        current_boost=prices_data["current_boost"],
        max_boost=prices_data["max_boost"],
        options={
            k: RoiBoostPriceInfo(**v) for k, v in prices_data["options"].items()
        },
    )


@router.post("/roi/buy", response_model=BuyRoiBoostResponse)
async def buy_roi_boost_endpoint(
    request: BuyRoiBoostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Buy a permanent ROI boost for a pet."""
    try:
        boost, new_balance = await buy_roi_boost(
            db, current_user, request.pet_id, request.boost_percent
        )

        # Get total boost on pet
        total_boost = await get_pet_total_roi_boost(db, request.pet_id)

        return BuyRoiBoostResponse(
            boost_id=boost.id,
            boost_percent=boost.boost_percent * 100,
            extra_profit=boost.extra_profit,
            cost=boost.cost_xpet,
            new_balance=new_balance,
            total_boost=total_boost * 100,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== AUTO-CLAIM ROUTES ==============

@router.get("/auto-claim/status", response_model=AutoClaimStatusResponse)
async def get_auto_claim_status_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get auto-claim subscription status."""
    status_data = await get_auto_claim_status(db, current_user.id)
    return AutoClaimStatusResponse(**status_data)


@router.post("/auto-claim/buy", response_model=BuyAutoClaimResponse)
async def buy_auto_claim_endpoint(
    request: BuyAutoClaimRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Buy auto-claim subscription."""
    try:
        subscription, new_balance = await buy_auto_claim(
            db, current_user, request.months
        )
        return BuyAutoClaimResponse(
            subscription_id=subscription.id,
            expires_at=subscription.expires_at,
            cost=subscription.cost_xpet,
            new_balance=new_balance,
            commission_percent=subscription.commission_percent * 100,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== STATS ROUTE ==============

@router.get("/stats", response_model=BoostStatsResponse)
async def get_boost_stats_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's boost statistics."""
    stats = await get_user_boost_stats(db, current_user.id)
    return BoostStatsResponse(**stats)
