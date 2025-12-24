"""
Channel repost service for forwarding posts from project channel to all users.
Supports auto-repost toggle and manual repost by link.
"""
import asyncio
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.services.admin.config import get_auto_repost_enabled, get_repost_channel_id

logger = logging.getLogger(__name__)

BOT_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

# Rate limiting
SEND_DELAY_SECONDS = 0.05  # 50ms = ~20 msg/sec
BATCH_SIZE = 100

# In-memory set to track recently processed channel posts (prevents duplicate reposts from webhook retries)
# Format: {(channel_id, message_id), ...}
_PROCESSED_CHANNEL_POSTS: set[tuple[int, int]] = set()
_MAX_PROCESSED_CACHE = 1000  # Keep last N entries to prevent memory leak


async def forward_message(
    chat_id: int,
    from_chat_id: int,
    message_id: int,
) -> tuple[bool, Optional[str]]:
    """
    Forward a message from one chat to another.
    Returns (success, error).
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
            }
            response = await client.post(f"{BOT_API_URL}/forwardMessage", data=payload)
            result = response.json()

            if result.get("ok"):
                return True, None
            else:
                return False, result.get("description", "Unknown error")
    except Exception as e:
        return False, str(e)


async def copy_message(
    chat_id: int,
    from_chat_id: int,
    message_id: int,
) -> tuple[bool, Optional[str]]:
    """
    Copy a message (without 'Forwarded from' header).
    Returns (success, error).
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
            }
            response = await client.post(f"{BOT_API_URL}/copyMessage", data=payload)
            result = response.json()

            if result.get("ok"):
                return True, None
            else:
                return False, result.get("description", "Unknown error")
    except Exception as e:
        return False, str(e)


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


def parse_telegram_link(link: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse Telegram post link to extract channel_id and message_id.
    Supports:
    - https://t.me/channel_name/123
    - https://t.me/c/1234567890/123 (private channels)

    Returns (channel_id_or_username, message_id) or (None, None) if invalid.
    """
    # Public channel: https://t.me/channel_name/123
    public_match = re.match(r"https?://t\.me/([a-zA-Z_][a-zA-Z0-9_]{3,})/(\d+)", link)
    if public_match:
        username = public_match.group(1)
        message_id = int(public_match.group(2))
        return f"@{username}", message_id

    # Private channel: https://t.me/c/1234567890/123
    private_match = re.match(r"https?://t\.me/c/(\d+)/(\d+)", link)
    if private_match:
        # Private channel IDs need -100 prefix
        channel_id = -100 * 10**10 - int(private_match.group(1))
        # Actually, the format is -100 + channel_id
        channel_id = int(f"-100{private_match.group(1)}")
        message_id = int(private_match.group(2))
        return channel_id, message_id

    return None, None


async def get_all_users(db: AsyncSession) -> List[User]:
    """Get all users for broadcast."""
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def get_active_users(db: AsyncSession) -> List[User]:
    """Get users with balance > 0 for broadcast."""
    from decimal import Decimal
    result = await db.execute(
        select(User).where(User.balance_xpet > Decimal("0"))
    )
    return list(result.scalars().all())


async def repost_to_users(
    db: AsyncSession,
    from_chat_id: int | str,
    message_id: int,
    only_active: bool = False,
    use_forward: bool = True,
    progress_callback: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    Repost a message from channel to all (or active) users.

    Args:
        db: Database session
        from_chat_id: Channel ID or @username
        message_id: Message ID in the channel
        only_active: If True, send only to users with balance > 0
        use_forward: If True, use forwardMessage (shows 'Forwarded from')
        progress_callback: Optional callback for progress updates

    Returns:
        Stats dict with sent/delivered/blocked/failed counts
    """
    # Get users
    if only_active:
        users = await get_active_users(db)
    else:
        users = await get_all_users(db)

    if not users:
        return {
            "total": 0,
            "sent": 0,
            "delivered": 0,
            "blocked": 0,
            "failed": 0,
        }

    stats = {
        "total": len(users),
        "sent": 0,
        "delivered": 0,
        "blocked": 0,
        "failed": 0,
    }

    send_func = forward_message if use_forward else copy_message

    for i, user in enumerate(users):
        success, error = await send_func(
            chat_id=user.telegram_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
        )

        stats["sent"] += 1
        if success:
            stats["delivered"] += 1
        elif is_blocked_error(error):
            stats["blocked"] += 1
        else:
            stats["failed"] += 1
            logger.debug(f"Failed to repost to {user.telegram_id}: {error}")

        # Progress callback
        if progress_callback and (i + 1) % BATCH_SIZE == 0:
            await progress_callback(stats, i + 1, len(users))

        # Rate limiting
        await asyncio.sleep(SEND_DELAY_SECONDS)

    return stats


async def handle_channel_post(
    db: AsyncSession,
    channel_post: dict,
) -> Optional[Dict[str, Any]]:
    """
    Handle incoming channel post for auto-repost.
    Called from webhook when a new post is made in the configured channel.

    Returns stats if repost was executed, None if skipped.
    """
    global _PROCESSED_CHANNEL_POSTS

    # Check if auto-repost is enabled
    if not await get_auto_repost_enabled(db):
        return None

    # Get configured channel ID
    repost_channel_id = await get_repost_channel_id(db)
    if not repost_channel_id:
        return None

    # Check if post is from the configured channel
    chat = channel_post.get("chat", {})
    chat_id = chat.get("id")

    if chat_id != repost_channel_id:
        return None

    message_id = channel_post.get("message_id")
    if not message_id:
        return None

    # IMPORTANT: Check if already processed to prevent duplicate reposts from webhook retries
    post_key = (chat_id, message_id)
    if post_key in _PROCESSED_CHANNEL_POSTS:
        logger.info(f"Skipping already processed channel post {message_id} from {chat_id}")
        return None

    # Mark as processed IMMEDIATELY before doing anything
    _PROCESSED_CHANNEL_POSTS.add(post_key)

    # Cleanup old entries to prevent memory leak
    if len(_PROCESSED_CHANNEL_POSTS) > _MAX_PROCESSED_CACHE:
        # Remove oldest entries (convert to list, keep last half)
        entries = list(_PROCESSED_CHANNEL_POSTS)
        _PROCESSED_CHANNEL_POSTS = set(entries[len(entries) // 2:])

    logger.info(f"Auto-reposting channel post {message_id} from {chat_id}")

    # Execute repost to all users
    stats = await repost_to_users(
        db=db,
        from_chat_id=chat_id,
        message_id=message_id,
        only_active=False,  # Send to all users
        use_forward=True,  # Use forward (shows 'Forwarded from')
    )

    logger.info(f"Auto-repost completed: {stats}")
    return stats
