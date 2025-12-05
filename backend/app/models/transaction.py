from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import TxType, TxStatus, NetworkType, RequestStatus

if TYPE_CHECKING:
    from app.models.user import User


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[TxType] = mapped_column(nullable=False)
    amount_xpet: Mapped[Decimal] = mapped_column(nullable=False)
    fee: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    meta: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[TxStatus] = mapped_column(default=TxStatus.COMPLETED)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="transactions")

    __table_args__ = (
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_type", "type"),
    )


class DepositRequest(Base):
    __tablename__ = "deposit_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    network: Mapped[NetworkType] = mapped_column(nullable=False)
    deposit_address: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[RequestStatus] = mapped_column(default=RequestStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column()
    confirmed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="deposit_requests")

    __table_args__ = (Index("idx_deposit_requests_status", "status"),)


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    fee: Mapped[Decimal] = mapped_column(nullable=False)
    network: Mapped[NetworkType] = mapped_column(nullable=False)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(default=RequestStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column()
    processed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="withdraw_requests")

    __table_args__ = (Index("idx_withdraw_requests_status", "status"),)
