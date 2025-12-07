"""
Pydantic schemas for broadcast API.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any

from pydantic import BaseModel, Field, field_validator

from app.models.enums import BroadcastStatus, BroadcastTargetType


class BroadcastButton(BaseModel):
    """Single inline button."""
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None


class BroadcastCreate(BaseModel):
    """Create a new broadcast."""
    text: str = Field(..., min_length=1, max_length=4096)
    target_type: BroadcastTargetType = BroadcastTargetType.ALL

    # Media
    photo_file_id: Optional[str] = None
    video_file_id: Optional[str] = None

    # Buttons: [[{text, url}], [{text, url}]] - rows of buttons
    buttons: Optional[List[List[BroadcastButton]]] = None

    # Targeting filters
    min_balance: Optional[Decimal] = None
    max_balance: Optional[Decimal] = None
    has_pets: Optional[bool] = None
    min_pets_count: Optional[int] = Field(None, ge=1, le=3)
    has_deposits: Optional[bool] = None
    min_deposit_total: Optional[Decimal] = None
    registered_after: Optional[datetime] = None
    registered_before: Optional[datetime] = None
    language_codes: Optional[List[str]] = None
    custom_user_ids: Optional[List[int]] = None

    # Scheduling
    scheduled_at: Optional[datetime] = None

    @field_validator("buttons", mode="before")
    @classmethod
    def convert_buttons(cls, v):
        """Convert button dicts to proper format for Telegram."""
        if not v:
            return None
        # Already in correct format
        return v


class BroadcastResponse(BaseModel):
    """Broadcast response."""
    id: int
    text: str
    target_type: BroadcastTargetType
    photo_file_id: Optional[str]
    video_file_id: Optional[str]
    buttons: Optional[Any]

    # Targeting
    min_balance: Optional[Decimal]
    max_balance: Optional[Decimal]
    has_pets: Optional[bool]
    min_pets_count: Optional[int]
    has_deposits: Optional[bool]
    min_deposit_total: Optional[Decimal]
    registered_after: Optional[datetime]
    registered_before: Optional[datetime]
    language_codes: Optional[List[str]]
    custom_user_ids: Optional[List[int]]

    # Scheduling
    scheduled_at: Optional[datetime]

    # Status
    status: BroadcastStatus
    total_recipients: int
    sent_count: int
    delivered_count: int
    failed_count: int
    blocked_count: int

    # Metadata
    created_by_admin_id: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BroadcastListResponse(BaseModel):
    """List of broadcasts."""
    items: List[BroadcastResponse]
    total: int


class BroadcastPreviewResponse(BaseModel):
    """Preview response with recipient count."""
    broadcast_id: int
    target_type: BroadcastTargetType
    recipient_count: int
    text_preview: str


class BroadcastSendResponse(BaseModel):
    """Response after sending a broadcast."""
    broadcast_id: int
    status: BroadcastStatus
    total: int
    sent: int
    delivered: int
    blocked: int
    failed: int
    success_rate: float


class BroadcastStatsResponse(BaseModel):
    """Overall broadcast statistics."""
    total_broadcasts: int
    total_messages_sent: int
    total_delivered: int
    total_blocked: int
    total_failed: int
    overall_delivery_rate: float
