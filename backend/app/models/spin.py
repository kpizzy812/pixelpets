from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import SpinRewardType

if TYPE_CHECKING:
    from app.models.user import User


class SpinReward(Base):
    """Available rewards on the spin wheel."""
    __tablename__ = "spin_rewards"

    id: Mapped[int] = mapped_column(primary_key=True)
    reward_type: Mapped[SpinRewardType] = mapped_column(nullable=False)
    value: Mapped[Decimal] = mapped_column(nullable=False)  # XPET amount or multiplier
    label: Mapped[str] = mapped_column(String(50), nullable=False)  # Display label
    emoji: Mapped[str] = mapped_column(String(10), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)  # Hex color for wheel
    probability: Mapped[Decimal] = mapped_column(nullable=False)  # Weight for random selection
    order: Mapped[int] = mapped_column(default=0)  # Order on wheel
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class UserSpin(Base):
    """Record of user spins."""
    __tablename__ = "user_spins"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reward_id: Mapped[int] = mapped_column(ForeignKey("spin_rewards.id"), nullable=False)
    reward_type: Mapped[SpinRewardType] = mapped_column(nullable=False)
    reward_value: Mapped[Decimal] = mapped_column(nullable=False)  # Actual value won
    cost_xpet: Mapped[Decimal] = mapped_column(default=Decimal("0"))  # 0 = free spin
    is_free_spin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="spins")
    reward: Mapped["SpinReward"] = relationship("SpinReward")

    __table_args__ = (
        Index("idx_user_spins_user_id", "user_id"),
        Index("idx_user_spins_created_at", "created_at"),
    )
