from datetime import datetime

from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class SystemConfig(Base):
    """
    Key-value store for system configuration.
    Examples:
    - referral_percentages: {"1": 20, "2": 15, "3": 10, "4": 5, "5": 2}
    - referral_unlock_thresholds: {"1": 0, "2": 3, "3": 5, "4": 10, "5": 20}
    - deposit_addresses: {"BEP-20": "0x...", "Solana": "...", "TON": "..."}
    - withdraw_min: 5
    - withdraw_fee_fixed: 1
    - withdraw_fee_percent: 2
    - pet_slots_limit: 3
    """
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
