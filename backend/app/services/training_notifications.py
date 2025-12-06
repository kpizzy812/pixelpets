"""
Training notification service: Sends notifications when pet training is complete.

This service should be called by the scheduler to notify users about ready-to-claim pets.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.pet import UserPet
from app.models.enums import PetStatus
from app.services.user_notifications import notify_training_complete

logger = logging.getLogger(__name__)


async def get_pets_ready_to_notify(db: AsyncSession) -> list[tuple[User, UserPet]]:
    """
    Get all pets that finished training and need notification:
    - Pet status is TRAINING and training has ended
    - No recent notification sent (to avoid spam)
    """
    now = datetime.utcnow()

    # Get pets that are training and training has ended
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type), selectinload(UserPet.user))
        .where(
            and_(
                UserPet.status == PetStatus.TRAINING,
                UserPet.training_ends_at <= now,
                # Could add a "last_notified_at" field to avoid duplicate notifications
            )
        )
    )
    pets = result.scalars().all()

    return [(pet.user, pet) for pet in pets]


async def send_training_complete_notifications(db: AsyncSession) -> dict:
    """
    Send notifications to users whose pets finished training.

    Returns statistics about notifications sent.
    """
    stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "errors": [],
    }

    pets_to_notify = await get_pets_ready_to_notify(db)
    stats["processed"] = len(pets_to_notify)

    for user, pet in pets_to_notify:
        try:
            # Calculate profit to show in notification
            from app.services.pets import calculate_daily_profit
            from app.services.boosts import get_active_snack

            daily_profit = calculate_daily_profit(pet.invested_total, pet.pet_type.daily_rate)

            # Check for snack bonus
            snack = await get_active_snack(db, pet.id)
            if snack:
                snack_bonus = daily_profit * snack.bonus_percent
                daily_profit += snack_bonus

            # Send notification (fire-and-forget)
            asyncio.create_task(
                notify_training_complete(
                    user_telegram_id=user.telegram_id,
                    pet_name=pet.pet_type.name,
                    reward=daily_profit,
                    locale=user.language_code or "en",
                )
            )

            stats["success"] += 1
            logger.info(f"Sent training complete notification to user {user.id} for pet {pet.id}")

        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append({
                "user_id": user.id,
                "pet_id": pet.id,
                "error": str(e),
            })
            logger.error(f"Failed to send training notification for user {user.id}, pet {pet.id}: {e}")

    return stats


async def run_training_notification_job(db: AsyncSession) -> dict:
    """
    Main entry point for training notification cron job.
    """
    logger.info("Starting training notification job...")

    try:
        stats = await send_training_complete_notifications(db)
        if stats["processed"] > 0:
            logger.info(
                f"Training notification job completed: {stats['success']}/{stats['processed']} sent"
            )
        return stats
    except Exception as e:
        logger.error(f"Training notification job failed: {e}")
        raise
