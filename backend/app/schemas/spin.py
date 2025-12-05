from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums import SpinRewardType


class SpinRewardResponse(BaseModel):
    """Single reward on the wheel."""
    id: int
    reward_type: SpinRewardType
    value: Decimal
    label: str
    emoji: str
    color: str
    order: int

    class Config:
        from_attributes = True


class SpinWheelResponse(BaseModel):
    """Wheel configuration with all rewards."""
    rewards: list[SpinRewardResponse]
    can_free_spin: bool
    next_free_spin_at: Optional[str]
    paid_spin_cost: Decimal
    spins_today: int
    winnings_today: Decimal


class SpinRequest(BaseModel):
    """Request to perform a spin."""
    is_free: bool = False


class SpinResultResponse(BaseModel):
    """Result of a spin."""
    reward: SpinRewardResponse
    amount_won: Decimal
    new_balance: Decimal
    was_free_spin: bool
    # For wheel animation - index of winning segment
    winning_index: int


class SpinHistoryEntry(BaseModel):
    """Single spin history entry."""
    id: int
    reward_type: SpinRewardType
    reward_label: str
    reward_emoji: str
    amount_won: Decimal
    cost: Decimal
    was_free: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SpinHistoryResponse(BaseModel):
    """User's spin history."""
    spins: list[SpinHistoryEntry]
    total_spent: Decimal
    total_won: Decimal
