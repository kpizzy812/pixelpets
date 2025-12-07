"""
Broadcast service for mass Telegram messaging.
Handles targeting, sending, and delivery tracking.
"""
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

import httpx
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.user import User
from app.models.pet import UserPet
from app.models.transaction import DepositRequest
from app.models.broadcast import Broadcast, BroadcastLog
from app.models.enums import (
    BroadcastStatus,
    BroadcastTargetType,
    PetStatus,
    RequestStatus,
)

logger = logging.getLogger(__name__)

BOT_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

# Rate limiting: 30 messages per second max (Telegram limit)
SEND_DELAY_SECONDS = 0.05  # 50ms = ~20 msg/sec
BATCH_SIZE = 100  # Report progress every N users
MAX_TEXT_LENGTH = 4096


async def get_target_users(
    db: AsyncSession,
    broadcast: Broadcast,
) -> List[User]:
    """
    Get list of users matching broadcast targeting criteria.
    """
    query = select(User)

    target_type = broadcast.target_type

    if target_type == BroadcastTargetType.ALL:
        pass  # No filters

    elif target_type == BroadcastTargetType.ACTIVE:
        # Users with pets or balance > 0
        # Subquery for users with pets
        pets_subq = (
            select(UserPet.user_id)
            .where(UserPet.status.in_([PetStatus.OWNED_IDLE, PetStatus.TRAINING, PetStatus.READY_TO_CLAIM]))
            .distinct()
        )
        query = query.where(
            or_(
                User.balance_xpet > Decimal("0"),
                User.id.in_(pets_subq)
            )
        )

    elif target_type == BroadcastTargetType.INACTIVE:
        # Users without pets and balance = 0
        pets_subq = (
            select(UserPet.user_id)
            .where(UserPet.status.in_([PetStatus.OWNED_IDLE, PetStatus.TRAINING, PetStatus.READY_TO_CLAIM]))
            .distinct()
        )
        query = query.where(
            and_(
                User.balance_xpet == Decimal("0"),
                ~User.id.in_(pets_subq)
            )
        )

    elif target_type == BroadcastTargetType.WITH_BALANCE:
        # Filter by balance range
        if broadcast.min_balance is not None:
            query = query.where(User.balance_xpet >= broadcast.min_balance)
        if broadcast.max_balance is not None:
            query = query.where(User.balance_xpet <= broadcast.max_balance)

    elif target_type == BroadcastTargetType.WITH_PETS:
        # Users with active pets
        pets_subq = (
            select(UserPet.user_id)
            .where(UserPet.status.in_([PetStatus.OWNED_IDLE, PetStatus.TRAINING, PetStatus.READY_TO_CLAIM]))
        )
        if broadcast.min_pets_count:
            pets_subq = (
                select(UserPet.user_id)
                .where(UserPet.status.in_([PetStatus.OWNED_IDLE, PetStatus.TRAINING, PetStatus.READY_TO_CLAIM]))
                .group_by(UserPet.user_id)
                .having(func.count(UserPet.id) >= broadcast.min_pets_count)
            )
        query = query.where(User.id.in_(pets_subq))

    elif target_type == BroadcastTargetType.WITH_DEPOSITS:
        # Users who have made approved deposits
        deposits_subq = (
            select(DepositRequest.user_id)
            .where(DepositRequest.status == RequestStatus.APPROVED)
            .distinct()
        )
        if broadcast.min_deposit_total:
            deposits_subq = (
                select(DepositRequest.user_id)
                .where(DepositRequest.status == RequestStatus.APPROVED)
                .group_by(DepositRequest.user_id)
                .having(func.sum(DepositRequest.amount) >= broadcast.min_deposit_total)
            )
        query = query.where(User.id.in_(deposits_subq))

    elif target_type == BroadcastTargetType.BY_LANGUAGE:
        # Filter by language codes
        if broadcast.language_codes:
            query = query.where(User.language_code.in_(broadcast.language_codes))

    elif target_type == BroadcastTargetType.BY_REGISTRATION:
        # Filter by registration date
        if broadcast.registered_after:
            query = query.where(User.created_at >= broadcast.registered_after)
        if broadcast.registered_before:
            query = query.where(User.created_at <= broadcast.registered_before)

    elif target_type == BroadcastTargetType.CUSTOM:
        # Custom list of telegram IDs
        if broadcast.custom_user_ids:
            query = query.where(User.telegram_id.in_(broadcast.custom_user_ids))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_target_users_count(
    db: AsyncSession,
    broadcast: Broadcast,
) -> int:
    """
    Get count of users matching broadcast targeting criteria.
    """
    users = await get_target_users(db, broadcast)
    return len(users)


async def send_telegram_message(
    chat_id: int,
    text: str,
    photo_file_id: Optional[str] = None,
    video_file_id: Optional[str] = None,
    buttons: Optional[dict] = None,
) -> tuple[bool, Optional[int], Optional[str]]:
    """
    Send a message to a Telegram user.
    Returns (success, message_id, error).
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            reply_markup = None
            if buttons:
                reply_markup = {"inline_keyboard": buttons}

            if photo_file_id:
                # Send photo with caption
                payload = {
                    "chat_id": chat_id,
                    "photo": photo_file_id,
                    "caption": text,
                    "parse_mode": "HTML",
                }
                if reply_markup:
                    import json
                    payload["reply_markup"] = json.dumps(reply_markup)
                response = await client.post(f"{BOT_API_URL}/sendPhoto", data=payload)

            elif video_file_id:
                # Send video with caption
                payload = {
                    "chat_id": chat_id,
                    "video": video_file_id,
                    "caption": text,
                    "parse_mode": "HTML",
                }
                if reply_markup:
                    import json
                    payload["reply_markup"] = json.dumps(reply_markup)
                response = await client.post(f"{BOT_API_URL}/sendVideo", data=payload)

            else:
                # Send text message
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                }
                if reply_markup:
                    import json
                    payload["reply_markup"] = json.dumps(reply_markup)
                response = await client.post(f"{BOT_API_URL}/sendMessage", data=payload)

            result = response.json()

            if result.get("ok"):
                return True, result["result"]["message_id"], None
            else:
                error_desc = result.get("description", "Unknown error")
                return False, None, error_desc

    except Exception as e:
        return False, None, str(e)


def is_blocked_error(error: str) -> bool:
    """Check if error indicates user blocked the bot."""
    if not error:
        return False
    blocked_indicators = [
        "bot was blocked",
        "user is deactivated",
        "chat not found",
        "bot can't initiate",
        "Forbidden",
        "PEER_ID_INVALID",
    ]
    return any(indicator.lower() in error.lower() for indicator in blocked_indicators)


async def execute_broadcast(
    db: AsyncSession,
    broadcast_id: int,
    progress_callback: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    Execute a broadcast, sending messages to all target users.
    Returns statistics dict.
    """
    # Get broadcast
    result = await db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()

    if not broadcast:
        raise ValueError(f"Broadcast {broadcast_id} not found")

    if broadcast.status not in [BroadcastStatus.DRAFT, BroadcastStatus.SCHEDULED]:
        raise ValueError(f"Broadcast {broadcast_id} is already {broadcast.status.value}")

    # Validate text length
    if len(broadcast.text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Text exceeds maximum length ({len(broadcast.text)}/{MAX_TEXT_LENGTH})")

    # Get target users
    users = await get_target_users(db, broadcast)

    if not users:
        broadcast.status = BroadcastStatus.COMPLETED
        broadcast.completed_at = datetime.utcnow()
        await db.commit()
        return {
            "total": 0,
            "sent": 0,
            "delivered": 0,
            "blocked": 0,
            "failed": 0,
        }

    # Update broadcast status
    broadcast.status = BroadcastStatus.SENDING
    broadcast.started_at = datetime.utcnow()
    broadcast.total_recipients = len(users)
    await db.commit()

    stats = {
        "total": len(users),
        "sent": 0,
        "delivered": 0,
        "blocked": 0,
        "failed": 0,
    }

    # Send messages
    for i, user in enumerate(users):
        # Send message
        success, message_id, error = await send_telegram_message(
            chat_id=user.telegram_id,
            text=broadcast.text,
            photo_file_id=broadcast.photo_file_id,
            video_file_id=broadcast.video_file_id,
            buttons=broadcast.buttons,
        )

        # Create log entry
        log = BroadcastLog(
            broadcast_id=broadcast.id,
            user_id=user.id,
            telegram_id=user.telegram_id,
            sent=True,
            delivered=success,
            blocked=is_blocked_error(error) if error else False,
            error=error,
            message_id=message_id,
            sent_at=datetime.utcnow(),
        )
        db.add(log)

        # Update stats
        stats["sent"] += 1
        if success:
            stats["delivered"] += 1
        elif is_blocked_error(error):
            stats["blocked"] += 1
        else:
            stats["failed"] += 1

        # Update broadcast counts
        broadcast.sent_count = stats["sent"]
        broadcast.delivered_count = stats["delivered"]
        broadcast.blocked_count = stats["blocked"]
        broadcast.failed_count = stats["failed"]

        # Report progress every BATCH_SIZE users
        if progress_callback and (i + 1) % BATCH_SIZE == 0:
            await db.commit()
            await progress_callback(stats, i + 1, len(users))

        # Rate limiting
        await asyncio.sleep(SEND_DELAY_SECONDS)

    # Mark as completed
    broadcast.status = BroadcastStatus.COMPLETED
    broadcast.completed_at = datetime.utcnow()
    await db.commit()

    return stats


async def create_broadcast(
    db: AsyncSession,
    text: str,
    target_type: BroadcastTargetType = BroadcastTargetType.ALL,
    photo_file_id: Optional[str] = None,
    video_file_id: Optional[str] = None,
    buttons: Optional[List[List[dict]]] = None,
    min_balance: Optional[Decimal] = None,
    max_balance: Optional[Decimal] = None,
    has_pets: Optional[bool] = None,
    min_pets_count: Optional[int] = None,
    has_deposits: Optional[bool] = None,
    min_deposit_total: Optional[Decimal] = None,
    registered_after: Optional[datetime] = None,
    registered_before: Optional[datetime] = None,
    language_codes: Optional[List[str]] = None,
    custom_user_ids: Optional[List[int]] = None,
    scheduled_at: Optional[datetime] = None,
    admin_id: Optional[int] = None,
) -> Broadcast:
    """
    Create a new broadcast.
    """
    broadcast = Broadcast(
        text=text,
        target_type=target_type,
        photo_file_id=photo_file_id,
        video_file_id=video_file_id,
        buttons=buttons,
        min_balance=min_balance,
        max_balance=max_balance,
        has_pets=has_pets,
        min_pets_count=min_pets_count,
        has_deposits=has_deposits,
        min_deposit_total=min_deposit_total,
        registered_after=registered_after,
        registered_before=registered_before,
        language_codes=language_codes,
        custom_user_ids=custom_user_ids,
        scheduled_at=scheduled_at,
        status=BroadcastStatus.SCHEDULED if scheduled_at else BroadcastStatus.DRAFT,
        created_by_admin_id=admin_id,
    )
    db.add(broadcast)
    await db.commit()
    await db.refresh(broadcast)
    return broadcast


async def get_broadcasts(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    status: Optional[BroadcastStatus] = None,
) -> List[Broadcast]:
    """
    Get list of broadcasts with optional status filter.
    """
    query = select(Broadcast).order_by(Broadcast.created_at.desc())

    if status:
        query = query.where(Broadcast.status == status)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_broadcast_by_id(
    db: AsyncSession,
    broadcast_id: int,
) -> Optional[Broadcast]:
    """
    Get broadcast by ID.
    """
    result = await db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    return result.scalar_one_or_none()


async def cancel_broadcast(
    db: AsyncSession,
    broadcast_id: int,
) -> bool:
    """
    Cancel a scheduled broadcast.
    Returns True if cancelled, False if not found or already sent.
    """
    result = await db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()

    if not broadcast:
        return False

    if broadcast.status not in [BroadcastStatus.DRAFT, BroadcastStatus.SCHEDULED]:
        return False

    broadcast.status = BroadcastStatus.CANCELLED
    await db.commit()
    return True


async def get_scheduled_broadcasts(
    db: AsyncSession,
) -> List[Broadcast]:
    """
    Get broadcasts scheduled for sending (scheduled_at <= now).
    """
    now = datetime.utcnow()
    result = await db.execute(
        select(Broadcast)
        .where(
            and_(
                Broadcast.status == BroadcastStatus.SCHEDULED,
                Broadcast.scheduled_at <= now,
            )
        )
        .order_by(Broadcast.scheduled_at)
    )
    return list(result.scalars().all())


async def run_broadcast_scheduler(db: AsyncSession) -> Dict[str, int]:
    """
    Run scheduled broadcasts that are due.
    Returns stats about processed broadcasts.
    """
    scheduled = await get_scheduled_broadcasts(db)

    stats = {
        "processed": 0,
        "total_sent": 0,
        "total_delivered": 0,
    }

    for broadcast in scheduled:
        try:
            result = await execute_broadcast(db, broadcast.id)
            stats["processed"] += 1
            stats["total_sent"] += result.get("sent", 0)
            stats["total_delivered"] += result.get("delivered", 0)
            logger.info(f"Scheduled broadcast {broadcast.id} completed: {result}")
        except Exception as e:
            logger.error(f"Failed to execute scheduled broadcast {broadcast.id}: {e}")
            broadcast.status = BroadcastStatus.FAILED
            await db.commit()

    return stats
