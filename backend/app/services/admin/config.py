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
    "bot_username": "Pixel_PetsBot",
    "miniapp_url": "https://pixelpets.vercel.app",
    "channel_cis": "PIXELPETS_CISOFFICIAL",  # CIS channel (ru, uk, kk, be, uz)
    "channel_west": "pixelpets_en",  # Western channel (en, de, es, fr, pt, it, etc)
    "chat_general": "pixelpets_chat",  # General chat for all users
    # Auto-repost settings
    "auto_repost_enabled": False,  # Toggle for auto-repost from channel
    "repost_channel_id": None,  # Channel ID to repost from (e.g., -1001234567890)
    # Admin Telegram IDs for broadcast command
    "broadcast_admin_ids": [],  # List of Telegram user IDs who can use /broadcast command
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
    import logging
    logger = logging.getLogger(__name__)

    added_keys = []
    for key, value in DEFAULT_CONFIG.items():
        existing = await get_config(db, key)
        if not existing:
            await set_config(db, key, value, f"Default value for {key}")
            added_keys.append(key)

    if added_keys:
        logger.info(f"Added {len(added_keys)} new config keys: {added_keys}")


async def get_auto_repost_enabled(db: AsyncSession) -> bool:
    """Get auto-repost toggle state."""
    value = await get_config_value(db, "auto_repost_enabled", False)
    return bool(value)


async def set_auto_repost_enabled(db: AsyncSession, enabled: bool) -> bool:
    """Set auto-repost toggle state."""
    await set_config(db, "auto_repost_enabled", enabled, "Auto-repost from channel enabled")
    return enabled


async def get_repost_channel_id(db: AsyncSession) -> int | None:
    """Get channel ID for auto-repost."""
    value = await get_config_value(db, "repost_channel_id", None)
    return int(value) if value else None


async def set_repost_channel_id(db: AsyncSession, channel_id: int | None) -> int | None:
    """Set channel ID for auto-repost."""
    await set_config(db, "repost_channel_id", channel_id, "Channel ID to repost from")
    return channel_id


async def get_broadcast_admin_ids(db: AsyncSession) -> list[int]:
    """Get list of Telegram IDs allowed to use /broadcast command."""
    value = await get_config_value(db, "broadcast_admin_ids", [])
    if isinstance(value, list):
        return [int(x) for x in value]
    return []


async def is_broadcast_admin(db: AsyncSession, telegram_id: int) -> bool:
    """Check if telegram user is allowed to use /broadcast command."""
    admin_ids = await get_broadcast_admin_ids(db)
    return telegram_id in admin_ids


async def add_broadcast_admin(db: AsyncSession, telegram_id: int) -> list[int]:
    """Add telegram ID to broadcast admins list."""
    admin_ids = await get_broadcast_admin_ids(db)
    if telegram_id not in admin_ids:
        admin_ids.append(telegram_id)
        await set_config(db, "broadcast_admin_ids", admin_ids, "Telegram IDs allowed to broadcast")
    return admin_ids


async def remove_broadcast_admin(db: AsyncSession, telegram_id: int) -> list[int]:
    """Remove telegram ID from broadcast admins list."""
    admin_ids = await get_broadcast_admin_ids(db)
    if telegram_id in admin_ids:
        admin_ids.remove(telegram_id)
        await set_config(db, "broadcast_admin_ids", admin_ids, "Telegram IDs allowed to broadcast")
    return admin_ids
