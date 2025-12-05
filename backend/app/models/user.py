from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    language_code: Mapped[str] = mapped_column(String(10), default="en")
    balance_xpet: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    ref_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    referrer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    ref_levels_unlocked: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    referrer: Mapped[Optional["User"]] = relationship("User", remote_side=[id], backref="referrals")

    __table_args__ = (
        Index("idx_users_telegram_id", "telegram_id"),
        Index("idx_users_ref_code", "ref_code"),
        Index("idx_users_referrer_id", "referrer_id"),
    )
