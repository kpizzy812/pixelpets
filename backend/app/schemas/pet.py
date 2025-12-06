from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums import PetStatus, PetLevel


class PetTypeResponse(BaseModel):
    id: int
    name: str
    emoji: Optional[str]
    image_key: str
    base_price: Decimal
    daily_rate: Decimal
    roi_cap_multiplier: Decimal
    level_prices: dict

    class Config:
        from_attributes = True


class PetCatalogResponse(BaseModel):
    pets: list[PetTypeResponse]


class UserPetResponse(BaseModel):
    id: int
    pet_type: PetTypeResponse
    invested_total: Decimal
    level: PetLevel
    status: PetStatus
    slot_index: int
    profit_claimed: Decimal
    max_profit: Decimal
    training_started_at: Optional[datetime]
    training_ends_at: Optional[datetime]
    upgrade_cost: Optional[Decimal]
    evolution_fee: Optional[Decimal]  # 10% fee on upgrade (not added to invested_total)
    next_level: Optional[PetLevel]
    current_daily_rate: Decimal  # Daily rate as percentage (e.g., 1.5 for 1.5%)
    roi_boost_percent: Optional[Decimal] = None  # ROI boost as percentage (e.g., 10 for +10%)

    class Config:
        from_attributes = True


class MyPetsResponse(BaseModel):
    pets: list[UserPetResponse]
    slots_used: int
    max_slots: int


class BuyPetRequest(BaseModel):
    pet_type_id: int


class BuyPetResponse(BaseModel):
    pet: UserPetResponse
    new_balance: Decimal


class PetIdRequest(BaseModel):
    pet_id: int


class UpgradePetResponse(BaseModel):
    pet: UserPetResponse
    new_balance: Decimal
    upgrade_cost: Decimal  # Amount added to invested_total
    evolution_fee: Decimal  # 10% fee (not added to invested_total)
    total_paid: Decimal  # upgrade_cost + evolution_fee


class SellPetResponse(BaseModel):
    refund_amount: Decimal
    fee_percent: Decimal  # Fee as percentage (e.g., 15.0 for 15%)
    new_balance: Decimal


class StartTrainingResponse(BaseModel):
    pet_id: int
    status: PetStatus
    training_started_at: datetime
    training_ends_at: datetime


class ClaimResponse(BaseModel):
    profit_claimed: Decimal
    base_profit: Optional[Decimal] = None
    snack_bonus: Optional[Decimal] = None
    snack_used: Optional[str] = None
    roi_boost_percent: Optional[Decimal] = None
    auto_claim_commission: Optional[Decimal] = None
    new_balance: Decimal
    pet_status: PetStatus
    total_profit_claimed: Decimal
    max_profit: Decimal
    evolved: bool
    hall_of_fame_entry: Optional[dict] = None


class HallOfFameEntry(BaseModel):
    id: int
    pet_type: PetTypeResponse
    final_level: PetLevel
    invested_total: Decimal
    total_farmed: Decimal
    lifetime_days: int
    evolved_at: datetime

    class Config:
        from_attributes = True


class HallOfFameResponse(BaseModel):
    pets: list[HallOfFameEntry]
    total_pets_evolved: int
    total_farmed_all_time: Decimal
