from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class RefLevelInfo(BaseModel):
    level: int
    percent: int  # 20, 15, 10, 5, 2
    unlocked: bool
    unlock_requirement: Optional[int] = None  # None for level 1
    referrals_count: int
    earned_xpet: Decimal
    progress: Optional[str] = None  # "5/10 active" for locked levels


class RefLinkResponse(BaseModel):
    ref_code: str
    ref_link: str
    share_text: str


class ReferralsResponse(BaseModel):
    ref_code: str
    total_earned_xpet: Decimal
    levels_unlocked: int
    levels: list[RefLevelInfo]
    active_referrals_count: int
