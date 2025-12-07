"""
Seed database with initial data.
Run: python -m app.scripts.seed
"""
import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models.pet import PetType
from app.models.task import Task
from app.models.admin import Admin
from app.models.config import SystemConfig
from app.models.spin import SpinReward
from app.models.enums import TaskType, AdminRole, SpinRewardType
from app.services.admin.auth import hash_password
from app.services.admin.config import DEFAULT_CONFIG


PET_TYPES_DATA = [
    {
        "name": "Bubble Slime",
        "emoji": "🫧",
        "image_key": "bubble",
        "base_price": Decimal("5"),
        "daily_rate": Decimal("0.01"),  # 1%
        "roi_cap_multiplier": Decimal("1.5"),  # 150%
        "level_prices": {"BABY": 5, "ADULT": 20, "MYTHIC": 50},
    },
    {
        "name": "Pixel Fox",
        "emoji": "🦊",
        "image_key": "fox",
        "base_price": Decimal("50"),
        "daily_rate": Decimal("0.012"),  # 1.2%
        "roi_cap_multiplier": Decimal("1.6"),  # 160%
        "level_prices": {"BABY": 50, "ADULT": 200, "MYTHIC": 500},
    },
    {
        "name": "Glitch Cat",
        "emoji": "🐱",
        "image_key": "cat",
        "base_price": Decimal("100"),
        "daily_rate": Decimal("0.015"),  # 1.5%
        "roi_cap_multiplier": Decimal("1.7"),  # 170%
        "level_prices": {"BABY": 100, "ADULT": 400, "MYTHIC": 1000},
    },
    {
        "name": "Robo-Bunny",
        "emoji": "🤖",
        "image_key": "rabbit",
        "base_price": Decimal("250"),
        "daily_rate": Decimal("0.02"),  # 2%
        "roi_cap_multiplier": Decimal("1.8"),  # 180%
        "level_prices": {"BABY": 250, "ADULT": 1000, "MYTHIC": 2500},
    },
    {
        "name": "Crystal Turtle",
        "emoji": "🐢",
        "image_key": "turtle",
        "base_price": Decimal("500"),
        "daily_rate": Decimal("0.022"),  # 2.2%
        "roi_cap_multiplier": Decimal("1.9"),  # 190%
        "level_prices": {"BABY": 500, "ADULT": 2000, "MYTHIC": 5000},
    },
    {
        "name": "Ember Dragon",
        "emoji": "🐉",
        "image_key": "dragon",
        "base_price": Decimal("1000"),
        "daily_rate": Decimal("0.025"),  # 2.5%
        "roi_cap_multiplier": Decimal("2.0"),  # 200%
        "level_prices": {"BABY": 1000, "ADULT": 4000, "MYTHIC": 10000},
    },
]

TASKS_DATA = [
    {
        "title": "Join Telegram Channel",
        "description": "Subscribe to our official channel",
        "reward_xpet": Decimal("0.30"),
        "link": "https://t.me/pixelpets_official",
        "task_type": TaskType.TELEGRAM_CHANNEL,
        "verification_data": {"channel_id": "@pixelpets_official"},
        "order": 1,
    },
    {
        "title": "Join Telegram Chat",
        "description": "Join community chat",
        "reward_xpet": Decimal("0.20"),
        "link": "https://t.me/pixelpets_chat",
        "task_type": TaskType.TELEGRAM_CHAT,
        "verification_data": {"channel_id": "@pixelpets_chat"},
        "order": 2,
    },
    {
        "title": "Follow on Twitter",
        "description": "Follow @pixelpetsapp",
        "reward_xpet": Decimal("0.20"),
        "link": "https://twitter.com/pixelpetsapp",
        "task_type": TaskType.TWITTER,
        "order": 3,
    },
]

# Spin wheel rewards - 8 segments
# No empty rewards - always win something!
# House edge ~35%, EV = 0.652 XPET per 1 XPET spin
SPIN_REWARDS_DATA = [
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("0.10"),
        "label": "0.10",
        "emoji": "🪙",
        "color": "#FFD700",  # Gold
        "probability": Decimal("28"),  # 28% chance
        "order": 0,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("0.20"),
        "label": "0.20",
        "emoji": "✨",
        "color": "#FFA500",  # Orange
        "probability": Decimal("25"),  # 25% chance
        "order": 1,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("0.40"),
        "label": "0.40",
        "emoji": "💰",
        "color": "#32CD32",  # Lime green
        "probability": Decimal("20"),  # 20% chance
        "order": 2,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("0.80"),
        "label": "0.80",
        "emoji": "💎",
        "color": "#1E90FF",  # Dodger blue
        "probability": Decimal("13"),  # 13% chance
        "order": 3,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("1.50"),
        "label": "1.50",
        "emoji": "🎁",
        "color": "#9932CC",  # Dark orchid
        "probability": Decimal("8"),  # 8% chance
        "order": 4,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("3.00"),
        "label": "3.00",
        "emoji": "🎉",
        "color": "#FF1493",  # Deep pink
        "probability": Decimal("4"),  # 4% chance
        "order": 5,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("5.00"),
        "label": "5.00",
        "emoji": "🔥",
        "color": "#FF4500",  # Orange red
        "probability": Decimal("1.5"),  # 1.5% chance
        "order": 6,
    },
    {
        "reward_type": SpinRewardType.XPET,
        "value": Decimal("15.00"),
        "label": "15.00",
        "emoji": "👑",
        "color": "#8B00FF",  # Violet (JACKPOT)
        "probability": Decimal("0.5"),  # 0.5% chance
        "order": 7,
    },
]


async def seed_pet_types():
    """Seed pet types if not exist."""
    async with async_session() as db:
        result = await db.execute(select(PetType))
        existing = result.scalars().all()

        if existing:
            print(f"Pet types already exist ({len(existing)} found), skipping...")
            return

        for data in PET_TYPES_DATA:
            pet_type = PetType(**data)
            db.add(pet_type)

        await db.commit()
        print(f"Created {len(PET_TYPES_DATA)} pet types")


async def seed_tasks():
    """Seed tasks if not exist."""
    async with async_session() as db:
        result = await db.execute(select(Task))
        existing = result.scalars().all()

        if existing:
            print(f"Tasks already exist ({len(existing)} found), skipping...")
            return

        for data in TASKS_DATA:
            task = Task(**data)
            db.add(task)

        await db.commit()
        print(f"Created {len(TASKS_DATA)} tasks")


async def seed_super_admin():
    """Create default super admin if not exists."""
    async with async_session() as db:
        result = await db.execute(select(Admin))
        existing = result.scalars().first()

        if existing:
            print("Admin already exists, skipping...")
            return

        admin = Admin(
            username="admin",
            password_hash=hash_password("admin123"),  # Change in production!
            email="admin@pixelpets.io",
            role=AdminRole.SUPER_ADMIN,
        )
        db.add(admin)
        await db.commit()
        print("Created super admin (username: admin, password: admin123)")
        print("!!! CHANGE PASSWORD IN PRODUCTION !!!")


async def seed_system_config():
    """Seed default system config - adds missing keys without overwriting existing."""
    async with async_session() as db:
        result = await db.execute(select(SystemConfig))
        existing = result.scalars().all()
        existing_keys = {config.key for config in existing}

        added = 0
        for key, value in DEFAULT_CONFIG.items():
            if key not in existing_keys:
                config = SystemConfig(
                    key=key,
                    value=value,
                    description=f"Default value for {key}",
                )
                db.add(config)
                added += 1

        if added > 0:
            await db.commit()
            print(f"Added {added} new system config entries (total: {len(existing) + added})")
        else:
            print(f"System config is up to date ({len(existing)} keys)")


async def seed_spin_rewards():
    """Seed spin wheel rewards if not exist."""
    async with async_session() as db:
        result = await db.execute(select(SpinReward))
        existing = result.scalars().all()

        if existing:
            print(f"Spin rewards already exist ({len(existing)} found), skipping...")
            return

        for data in SPIN_REWARDS_DATA:
            reward = SpinReward(**data)
            db.add(reward)

        await db.commit()
        print(f"Created {len(SPIN_REWARDS_DATA)} spin rewards")


async def main():
    print("Seeding database...")
    try:
        await seed_pet_types()
        await seed_tasks()
        await seed_super_admin()
        await seed_system_config()
        await seed_spin_rewards()
        print("Done!")
    except Exception as e:
        print(f"Seed error (tables may not exist yet): {e}")
        print("Skipping seed - will retry on next restart")


if __name__ == "__main__":
    asyncio.run(main())
