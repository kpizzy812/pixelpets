"""
Broadcast system models for Telegram mass messaging.
Supports targeting, scheduling, and delivery tracking.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey, Index, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import BroadcastStatus, BroadcastTargetType


class Broadcast(Base):
    """
    Broadcast message template with targeting configuration.
    """
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(255))  # Telegram file_id
    video_file_id: Mapped[Optional[str]] = mapped_column(String(255))  # Telegram file_id
    buttons: Mapped[Optional[dict]] = mapped_column(JSON)  # Inline keyboard config
    entities: Mapped[Optional[List[dict]]] = mapped_column(JSON)  # Telegram message entities for formatting

    # Targeting
    target_type: Mapped[BroadcastTargetType] = mapped_column(
        default=BroadcastTargetType.ALL
    )
    # Filters (applied based on target_type)
    min_balance: Mapped[Optional[Decimal]] = mapped_column()
    max_balance: Mapped[Optional[Decimal]] = mapped_column()
    has_pets: Mapped[Optional[bool]] = mapped_column()
    min_pets_count: Mapped[Optional[int]] = mapped_column()
    has_deposits: Mapped[Optional[bool]] = mapped_column()
    min_deposit_total: Mapped[Optional[Decimal]] = mapped_column()
    registered_after: Mapped[Optional[datetime]] = mapped_column()
    registered_before: Mapped[Optional[datetime]] = mapped_column()
    language_codes: Mapped[Optional[List[str]]] = mapped_column(JSON)  # ["en", "ru"]
    custom_user_ids: Mapped[Optional[List[int]]] = mapped_column(JSON)  # For CUSTOM target

    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column()  # None = immediate

    # Status
    status: Mapped[BroadcastStatus] = mapped_column(default=BroadcastStatus.DRAFT)

    # Statistics
    total_recipients: Mapped[int] = mapped_column(default=0)
    sent_count: Mapped[int] = mapped_column(default=0)
    delivered_count: Mapped[int] = mapped_column(default=0)
    failed_count: Mapped[int] = mapped_column(default=0)
    blocked_count: Mapped[int] = mapped_column(default=0)

    # Metadata
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id"))
    started_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by: Mapped[Optional["Admin"]] = relationship("Admin", backref="broadcasts")
    logs: Mapped[List["BroadcastLog"]] = relationship(
        "BroadcastLog", back_populates="broadcast", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_broadcasts_status", "status"),
        Index("idx_broadcasts_scheduled_at", "scheduled_at"),
        Index("idx_broadcasts_created_at", "created_at"),
    )


class BroadcastLog(Base):
    """
    Individual delivery log for each user in a broadcast.
    """
    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    broadcast_id: Mapped[int] = mapped_column(ForeignKey("broadcasts.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(BigInteger)  # Denormalized for quick access

    # Delivery status
    sent: Mapped[bool] = mapped_column(default=False)
    delivered: Mapped[bool] = mapped_column(default=False)
    blocked: Mapped[bool] = mapped_column(default=False)
    error: Mapped[Optional[str]] = mapped_column(Text)

    # Telegram message ID (for potential editing/deletion)
    message_id: Mapped[Optional[int]] = mapped_column()

    sent_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    broadcast: Mapped["Broadcast"] = relationship("Broadcast", back_populates="logs")
    user: Mapped["User"] = relationship("User", backref="broadcast_logs")

    __table_args__ = (
        Index("idx_broadcast_logs_broadcast_id", "broadcast_id"),
        Index("idx_broadcast_logs_user_id", "user_id"),
        Index("idx_broadcast_logs_sent", "sent"),
    )
