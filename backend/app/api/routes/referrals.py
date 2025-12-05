from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.referral import (
    RefLinkResponse,
    ReferralsResponse,
    RefLevelInfo,
)
from app.services.referrals import (
    get_referral_stats,
    generate_ref_link,
    get_share_text,
)

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/link", response_model=RefLinkResponse)
async def get_referral_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's referral link for sharing."""
    ref_link = await generate_ref_link(db, current_user.ref_code)
    return RefLinkResponse(
        ref_code=current_user.ref_code,
        ref_link=ref_link,
        share_text=get_share_text(),
    )


@router.get("", response_model=ReferralsResponse)
async def get_referrals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get referral statistics and levels info."""
    stats = await get_referral_stats(db, current_user)

    levels = [
        RefLevelInfo(**level_data)
        for level_data in stats["levels"]
    ]

    return ReferralsResponse(
        ref_code=stats["ref_code"],
        total_earned_xpet=stats["total_earned_xpet"],
        levels_unlocked=stats["levels_unlocked"],
        levels=levels,
        active_referrals_count=stats["active_referrals_count"],
    )
