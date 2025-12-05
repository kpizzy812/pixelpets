from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.pet import UserPet
from app.models.enums import PetStatus
from app.models.referral import ReferralStats
from app.schemas.user import (
    TelegramAuthRequest,
    AuthResponse,
    UserResponse,
    UserWithStats,
    UserStats,
)
from app.services.auth import (
    validate_telegram_init_data,
    create_access_token,
    get_or_create_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(
    request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user via Telegram Mini App initData."""
    # Validate initData
    user_data = validate_telegram_init_data(request.init_data)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )

    # Get or create user
    user = await get_or_create_user(
        db=db,
        telegram_id=user_data.get("id"),
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        language_code=user_data.get("language_code", "en"),
        ref_code_from_link=request.ref_code,
    )

    # Create access token
    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserWithStats)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile with stats."""
    # Refresh user to get latest balance
    await db.refresh(current_user)

    # Count pets
    pets_result = await db.execute(
        select(func.count(UserPet.id)).where(
            UserPet.user_id == current_user.id,
            UserPet.status != PetStatus.SOLD,
        )
    )
    total_pets_owned = pets_result.scalar() or 0

    # Sum profit claimed
    claimed_result = await db.execute(
        select(func.coalesce(func.sum(UserPet.profit_claimed), 0)).where(
            UserPet.user_id == current_user.id
        )
    )
    total_claimed = claimed_result.scalar() or Decimal("0")

    # Get referral earnings
    ref_stats_result = await db.execute(
        select(ReferralStats).where(ReferralStats.user_id == current_user.id)
    )
    ref_stats = ref_stats_result.scalar_one_or_none()
    total_ref_earned = ref_stats.total_earned if ref_stats else Decimal("0")

    stats = UserStats(
        total_pets_owned=total_pets_owned,
        total_claimed=total_claimed,
        total_ref_earned=total_ref_earned,
    )

    return UserWithStats(
        **UserResponse.model_validate(current_user).model_dump(),
        stats=stats,
    )
