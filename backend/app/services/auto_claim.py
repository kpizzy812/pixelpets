"""
Auto-claim service: Automatically claims profits for users with active subscriptions.

This service should be called by a scheduler (cron job) every few minutes.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.pet import UserPet
from app.models.boost import AutoClaimSubscription
from app.models.enums import PetStatus
from app.services.pets import claim_profit, check_training_status

logger = logging.getLogger(__name__)


async def get_pets_ready_for_auto_claim(db: AsyncSession) -> list[tuple[User, UserPet]]:
    """
    Get all pets that are ready for auto-claim:
    - Pet status is TRAINING and training has ended
    - Owner has active auto-claim subscription
    """
    now = datetime.now(timezone.utc)

    # Get users with active auto-claim subscriptions
    active_subs_result = await db.execute(
        select(AutoClaimSubscription.user_id).where(
            and_(
                AutoClaimSubscription.is_active == True,
                AutoClaimSubscription.expires_at > now,
            )
        )
    )
    active_user_ids = set(active_subs_result.scalars().all())

    if not active_user_ids:
        return []

    # Get pets that are training and training has ended
    result = await db.execute(
        select(UserPet)
        .options(selectinload(UserPet.pet_type), selectinload(UserPet.user))
        .where(
            and_(
                UserPet.user_id.in_(active_user_ids),
                UserPet.status == PetStatus.TRAINING,
                UserPet.training_ends_at <= now,
            )
        )
    )
    pets = result.scalars().all()

    return [(pet.user, pet) for pet in pets]


async def process_auto_claims(db: AsyncSession) -> dict:
    """
    Process all pending auto-claims.

    Returns statistics about the processing.
    """
    stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "errors": [],
    }

    pets_to_claim = await get_pets_ready_for_auto_claim(db)
    stats["processed"] = len(pets_to_claim)

    for user, pet in pets_to_claim:
        try:
            # Claim with auto-claim flag (applies 3% commission)
            result = await claim_profit(db, user, pet.id, is_auto_claim=True)
            stats["success"] += 1

            logger.info(
                f"Auto-claimed {result['profit_claimed']} XPET for user {user.id}, "
                f"pet {pet.id} (commission: {result.get('auto_claim_commission', 0)})"
            )

        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append({
                "user_id": user.id,
                "pet_id": pet.id,
                "error": str(e),
            })
            logger.error(f"Auto-claim failed for user {user.id}, pet {pet.id}: {e}")

    return stats


async def run_auto_claim_job(db: AsyncSession) -> dict:
    """
    Main entry point for auto-claim cron job.
    """
    logger.info("Starting auto-claim job...")

    try:
        stats = await process_auto_claims(db)
        logger.info(
            f"Auto-claim job completed: {stats['success']}/{stats['processed']} successful"
        )
        return stats
    except Exception as e:
        logger.error(f"Auto-claim job failed: {e}")
        raise
