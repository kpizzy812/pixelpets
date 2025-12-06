from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: str = "en"


class UserCreate(UserBase):
    ref_code: str
    referrer_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: str
    balance_xpet: Decimal
    ref_code: str
    referrer_id: Optional[int]
    ref_levels_unlocked: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_pets_owned: int
    total_claimed: Decimal
    total_ref_earned: Decimal


class UserWithStats(UserResponse):
    stats: UserStats


class ProfileStats(BaseModel):
    """Extended stats for profile page."""
    # Pets
    total_pets_owned: int
    total_pets_value: Decimal  # Sum of invested_total
    total_pets_evolved: int
    # Earnings
    total_claimed: Decimal
    total_farmed_all_time: Decimal  # From Hall of Fame
    # Spin
    total_spin_wins: Decimal
    total_spins: int
    # Referrals
    total_ref_earned: Decimal
    total_referrals: int
    active_referrals: int


class ProfileResponse(UserResponse):
    """Full profile with extended stats."""
    stats: ProfileStats


class TelegramAuthRequest(BaseModel):
    init_data: str
    ref_code: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse


class SyntraVerifyResponse(BaseModel):
    """Ответ для проверки пользователя Syntra"""
    is_registered: bool
    has_pet: bool
    pets_count: int
    total_invested: Decimal
    registered_at: Optional[datetime]
