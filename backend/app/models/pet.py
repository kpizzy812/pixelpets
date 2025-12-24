from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import PetStatus, PetLevel

if TYPE_CHECKING:
    from app.models.user import User


class PetType(Base):
    __tablename__ = "pet_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[Optional[str]] = mapped_column(String(10))
    image_key: Mapped[str] = mapped_column(String(50), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(nullable=False)  # e.g., 0.01 = 1%
    roi_cap_multiplier: Mapped[Decimal] = mapped_column(nullable=False)  # e.g., 1.5 = 150%
    level_prices: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_available: Mapped[bool] = mapped_column(default=True)  # Available for purchase in shop
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class UserPet(Base):
    __tablename__ = "user_pets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pet_type_id: Mapped[int] = mapped_column(ForeignKey("pet_types.id"), nullable=False)
    invested_total: Mapped[Decimal] = mapped_column(nullable=False)
    level: Mapped[PetLevel] = mapped_column(default=PetLevel.BABY)
    status: Mapped[PetStatus] = mapped_column(default=PetStatus.OWNED_IDLE)
    slot_index: Mapped[int] = mapped_column(nullable=False)  # 0, 1, or 2
    profit_claimed: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    training_started_at: Mapped[Optional[datetime]] = mapped_column()
    training_ends_at: Mapped[Optional[datetime]] = mapped_column()
    evolved_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="pets")
    pet_type: Mapped["PetType"] = relationship("PetType")

    __table_args__ = (
        Index("idx_user_pets_user_id", "user_id"),
        Index("idx_user_pets_status", "status"),
    )
