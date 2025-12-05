from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class AdminActionLog(Base):
    """
    Audit log for all admin actions.
    Tracks who did what, when, and to whom.
    """
    __tablename__ = "admin_action_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g., "user.balance_adjust", "deposit.approve", "pet_type.update"
    target_type: Mapped[Optional[str]] = mapped_column(String(50))
    # e.g., "user", "deposit_request", "pet_type"
    target_id: Mapped[Optional[int]] = mapped_column()
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    # e.g., {"old_balance": 100, "new_balance": 150, "reason": "Compensation"}
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    admin: Mapped["Admin"] = relationship("Admin", backref="action_logs")

    __table_args__ = (
        Index("idx_admin_logs_admin_id", "admin_id"),
        Index("idx_admin_logs_action", "action"),
        Index("idx_admin_logs_created_at", "created_at"),
    )


# Import Admin here to avoid circular import
from app.models.admin import Admin
