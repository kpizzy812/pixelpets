"""
Boost system models: Snacks, ROI Boosts, Auto-Claim subscriptions.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import SnackType, BoostType, TxType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.pet import UserPet


class PetSnack(Base):
    """
    Snack applied to a pet for next claim bonus.
    One active snack per pet at a time.
    """
    __tablename__ = "pet_snacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("user_pets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    snack_type: Mapped[SnackType] = mapped_column(nullable=False)
    bonus_percent: Mapped[Decimal] = mapped_column(nullable=False)  # e.g., 0.10 for +10%
    cost_xpet: Mapped[Decimal] = mapped_column(nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    used_at: Mapped[Optional[datetime]] = mapped_column()

    # Relationships
    user: Mapped["User"] = relationship("User", backref="snacks_purchased")
    pet: Mapped["UserPet"] = relationship("UserPet", backref="snacks")

    __table_args__ = (
        Index("idx_pet_snacks_pet_id", "pet_id"),
        Index("idx_pet_snacks_user_id", "user_id"),
    )


class PetRoiBoost(Base):
    """
    Permanent ROI cap boost applied to a pet.
    Multiple boosts can stack on same pet.
    """
    __tablename__ = "pet_roi_boosts"

    id: Mapped[int] = mapped_column(primary_key=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("user_pets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    boost_percent: Mapped[Decimal] = mapped_column(nullable=False)  # e.g., 0.05 for +5%
    extra_profit: Mapped[Decimal] = mapped_column(nullable=False)  # Total extra profit this boost gives
    cost_xpet: Mapped[Decimal] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="roi_boosts_purchased")
    pet: Mapped["UserPet"] = relationship("UserPet", backref="roi_boosts")

    __table_args__ = (
        Index("idx_pet_roi_boosts_pet_id", "pet_id"),
        Index("idx_pet_roi_boosts_user_id", "user_id"),
    )


class AutoClaimSubscription(Base):
    """
    Auto-claim subscription for a user.
    Active subscription auto-claims all pets when training completes.
    """
    __tablename__ = "auto_claim_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    cost_xpet: Mapped[Decimal] = mapped_column(nullable=False)  # $5 fixed
    commission_percent: Mapped[Decimal] = mapped_column(default=Decimal("0.03"))  # 3% from claims
    is_active: Mapped[bool] = mapped_column(default=True)
    total_claims: Mapped[int] = mapped_column(default=0)
    total_commission: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="auto_claim_subscriptions")

    __table_args__ = (
        Index("idx_auto_claim_user_id", "user_id"),
        Index("idx_auto_claim_expires_at", "expires_at"),
    )


class BoostTransaction(Base):
    """
    Record of all boost purchases and usage.
    """
    __tablename__ = "boost_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    boost_type: Mapped[BoostType] = mapped_column(nullable=False)
    pet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_pets.id"))
    amount_xpet: Mapped[Decimal] = mapped_column(nullable=False)  # Negative = cost, positive = commission
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="boost_transactions")

    __table_args__ = (
        Index("idx_boost_tx_user_id", "user_id"),
        Index("idx_boost_tx_type", "boost_type"),
    )
