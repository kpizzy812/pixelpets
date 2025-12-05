from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ReferralStats(Base):
    __tablename__ = "referral_stats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    level_1_count: Mapped[int] = mapped_column(default=0)
    level_2_count: Mapped[int] = mapped_column(default=0)
    level_3_count: Mapped[int] = mapped_column(default=0)
    level_4_count: Mapped[int] = mapped_column(default=0)
    level_5_count: Mapped[int] = mapped_column(default=0)
    level_1_earned: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    level_2_earned: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    level_3_earned: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    level_4_earned: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    level_5_earned: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    total_earned: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="referral_stats")


class ReferralReward(Base):
    __tablename__ = "referral_rewards"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    level: Mapped[int] = mapped_column(nullable=False)
    claim_amount: Mapped[Decimal] = mapped_column(nullable=False)
    reward_amount: Mapped[Decimal] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id])
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id])

    __table_args__ = (
        CheckConstraint("level >= 1 AND level <= 5", name="check_level_range"),
        Index("idx_referral_rewards_to_user", "to_user_id"),
        Index("idx_referral_rewards_from_user", "from_user_id"),
    )
