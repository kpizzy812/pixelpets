"""
Pydantic schemas for boost system.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums import SnackType, BoostType


# ============== SNACK SCHEMAS ==============

class SnackPriceInfo(BaseModel):
    cost: Decimal
    bonus_percent: Decimal  # As percentage (e.g., 10 for 10%)
    bonus_amount: Decimal
    net_benefit: Decimal


class SnackPricesResponse(BaseModel):
    pet_id: int
    daily_profit: Decimal
    active_snack: Optional[str] = None
    prices: dict[str, SnackPriceInfo]


class BuySnackRequest(BaseModel):
    pet_id: int
    snack_type: SnackType


class BuySnackResponse(BaseModel):
    snack_id: int
    snack_type: SnackType
    bonus_percent: Decimal
    cost: Decimal
    new_balance: Decimal


# ============== ROI BOOST SCHEMAS ==============

class RoiBoostPriceInfo(BaseModel):
    cost: Decimal
    boost_percent: Decimal  # As percentage (e.g., 5 for 5%)
    extra_profit: Decimal
    net_benefit: Decimal
    can_buy: bool


class RoiBoostPricesResponse(BaseModel):
    pet_id: int
    current_boost: Decimal  # As percentage
    max_boost: Decimal  # 50%
    options: dict[str, RoiBoostPriceInfo]


class BuyRoiBoostRequest(BaseModel):
    pet_id: int
    boost_percent: Decimal  # As decimal (e.g., 0.05 for 5%)


class BuyRoiBoostResponse(BaseModel):
    boost_id: int
    boost_percent: Decimal
    extra_profit: Decimal
    cost: Decimal
    new_balance: Decimal
    total_boost: Decimal  # Total boost on pet now


# ============== AUTO-CLAIM SCHEMAS ==============

class AutoClaimStatusResponse(BaseModel):
    is_active: bool
    expires_at: Optional[str] = None
    days_remaining: Optional[int] = None
    total_claims: Optional[int] = None
    total_commission: Optional[Decimal] = None
    commission_percent: Decimal
    monthly_cost: Optional[Decimal] = None


class BuyAutoClaimRequest(BaseModel):
    months: int = 1  # 1, 3, or 6 months


class BuyAutoClaimResponse(BaseModel):
    subscription_id: int
    expires_at: datetime
    cost: Decimal
    new_balance: Decimal
    commission_percent: Decimal


# ============== BOOST STATS ==============

class BoostStatsResponse(BaseModel):
    total_spent: Decimal
    snacks_purchased: int
    roi_boosts_purchased: int
    auto_claim_subscriptions: int


# ============== PET BOOST INFO (for pet response) ==============

class PetBoostInfo(BaseModel):
    """Boost info to include in pet response."""
    active_snack: Optional[SnackType] = None
    snack_bonus_percent: Optional[Decimal] = None
    total_roi_boost: Decimal = Decimal("0")
    boosted_roi_cap: Decimal
