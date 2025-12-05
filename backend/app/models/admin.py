from datetime import datetime
from typing import Optional

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.enums import AdminRole


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[AdminRole] = mapped_column(default=AdminRole.MODERATOR)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_admins_username", "username"),
        Index("idx_admins_role", "role"),
    )
