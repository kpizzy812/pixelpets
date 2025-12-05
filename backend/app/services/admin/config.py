from typing import Optional, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SystemConfig


# Default values for system config
DEFAULT_CONFIG = {
    "referral_percentages": {"1": 20, "2": 15, "3": 10, "4": 5, "5": 2},
    "referral_unlock_thresholds": {"1": 0, "2": 3, "3": 5, "4": 10, "5": 20},
    "deposit_addresses": {
        "BEP-20": "",
        "Solana": "",
        "TON": "",
    },
    "withdraw_min": 5,
    "withdraw_fee_fixed": 1,
    "withdraw_fee_percent": 2,
    "pet_slots_limit": 3,
    "sell_penalty_percent": 15,
    "bot_username": "pixelpets_bot",
}


async def get_config(
    db: AsyncSession,
    key: str,
) -> Optional[SystemConfig]:
    """Get config by key."""
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.key == key)
    )
    return result.scalar_one_or_none()


async def get_config_value(
    db: AsyncSession,
    key: str,
    default: Any = None,
) -> Any:
    """Get config value by key, with fallback to default."""
    config = await get_config(db, key)
    if config:
        return config.value
    return DEFAULT_CONFIG.get(key, default)


async def set_config(
    db: AsyncSession,
    key: str,
    value: Any,
    description: Optional[str] = None,
) -> SystemConfig:
    """Set config value (create or update)."""
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.key == key)
    )
    config = result.scalar_one_or_none()

    if config:
        config.value = value
        if description is not None:
            config.description = description
    else:
        config = SystemConfig(
            key=key,
            value=value,
            description=description,
        )
        db.add(config)

    await db.commit()
    await db.refresh(config)
    return config


async def get_all_configs(db: AsyncSession) -> list[SystemConfig]:
    """Get all configs."""
    result = await db.execute(select(SystemConfig).order_by(SystemConfig.key))
    return list(result.scalars().all())


async def get_referral_config(db: AsyncSession) -> dict:
    """Get referral system config."""
    percentages = await get_config_value(
        db, "referral_percentages",
        DEFAULT_CONFIG["referral_percentages"]
    )
    thresholds = await get_config_value(
        db, "referral_unlock_thresholds",
        DEFAULT_CONFIG["referral_unlock_thresholds"]
    )

    return {
        "percentages": percentages,
        "unlock_thresholds": thresholds,
    }


async def update_referral_config(
    db: AsyncSession,
    percentages: Optional[dict] = None,
    unlock_thresholds: Optional[dict] = None,
) -> dict:
    """Update referral system config."""
    if percentages is not None:
        await set_config(
            db, "referral_percentages", percentages,
            "Referral commission percentages by level"
        )

    if unlock_thresholds is not None:
        await set_config(
            db, "referral_unlock_thresholds", unlock_thresholds,
            "Active referrals required to unlock each level"
        )

    return await get_referral_config(db)


async def init_default_configs(db: AsyncSession) -> None:
    """Initialize default configs if they don't exist."""
    for key, value in DEFAULT_CONFIG.items():
        existing = await get_config(db, key)
        if not existing:
            await set_config(db, key, value, f"Default value for {key}")
