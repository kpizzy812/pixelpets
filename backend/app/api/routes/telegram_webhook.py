"""
Telegram webhook handler for /start command and inline button callbacks.
"""
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import async_session
from app.core.config import settings
from app.models import DepositRequest, WithdrawRequest, Admin
from app.models.enums import RequestStatus
from app.services.admin.deposits import approve_deposit, reject_deposit
from app.services.admin.withdrawals import complete_withdrawal, reject_withdrawal
from app.services.admin.config import get_config_value, DEFAULT_CONFIG, is_broadcast_admin
from app.services import telegram_notify
from app.services.channel_repost import handle_channel_post
from app.services.admin.broadcast import create_broadcast, execute_broadcast
from app.models.enums import BroadcastTargetType
from app.i18n import get_text as t, set_locale

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

# CIS language codes (Russian-speaking countries)
CIS_LANGUAGES = {"ru", "uk", "kk", "be", "uz", "tg", "ky", "az", "hy", "ka"}

# Localized button labels (kept simple - not in main i18n system)
BUTTON_LABELS = {
    "en": {"launch": "Launch App", "channel": "Channel", "chat": "Chat"},
    "ru": {"launch": "Запустить", "channel": "Канал", "chat": "Чат"},
}


class TelegramUser(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    type: str


class TelegramMessage(BaseModel):
    message_id: int
    chat: TelegramChat
    from_user: Optional[TelegramUser] = None
    text: Optional[str] = None

    model_config = {"populate_by_name": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict) and "from" in obj:
            obj = {**obj, "from_user": obj.pop("from")}
        return super().model_validate(obj, **kwargs)


class CallbackQuery(BaseModel):
    id: str
    from_user: TelegramUser
    message: Optional[TelegramMessage] = None
    data: Optional[str] = None

    model_config = {"populate_by_name": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict) and "from" in obj:
            obj = {**obj, "from_user": obj.pop("from")}
        return super().model_validate(obj, **kwargs)


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    callback_query: Optional[CallbackQuery] = None


def get_language(lang_code: Optional[str]) -> str:
    """Get supported language or fallback to English."""
    if not lang_code:
        return "en"
    # Take first 2 chars (e.g., "en-US" -> "en")
    lang = lang_code[:2].lower()
    # Only support en and ru
    return lang if lang in ("en", "ru") else "en"


def is_cis_language(lang_code: Optional[str]) -> bool:
    """Check if language code belongs to CIS region."""
    if not lang_code:
        return False
    lang = lang_code[:2].lower()
    return lang in CIS_LANGUAGES


async def send_photo_with_buttons(
    chat_id: int,
    photo_url: str,
    caption: str,
    keyboard: list,
) -> Optional[int]:
    """Send photo with inline keyboard to Telegram chat. Returns message_id on success."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendPhoto"

    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": keyboard},
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to send photo: {response.text}")
                return None
            data = response.json()
            return data.get("result", {}).get("message_id")
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return None


async def pin_message(chat_id: int, message_id: int) -> bool:
    """Pin a message in chat (silently, without notification)."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/pinChatMessage"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "disable_notification": True,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to pin message: {response.text}")
                return False
            return True
    except Exception as e:
        logger.error(f"Error pinning message: {e}")
        return False


async def set_message_reaction(chat_id: int, message_id: int, emoji: str = "🔥") -> bool:
    """Set a reaction on a message."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setMessageReaction"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to set reaction: {response.text}")
                return False
            return True
    except Exception as e:
        logger.error(f"Error setting reaction: {e}")
        return False


async def send_welcome_to_user(
    telegram_id: int,
    language_code: Optional[str] = None,
    ref_code: Optional[str] = None,
) -> None:
    """
    Send welcome message to user when they first open the Mini App.
    Sends banner image with localized message and inline buttons, pins it and adds reaction.
    """
    lang = get_language(language_code)
    is_cis = is_cis_language(language_code)

    # Get config values from database
    async with async_session() as db:
        bot_username = await get_config_value(db, "bot_username", DEFAULT_CONFIG["bot_username"])
        miniapp_url = await get_config_value(db, "miniapp_url", DEFAULT_CONFIG["miniapp_url"])
        channel_cis = await get_config_value(db, "channel_cis", DEFAULT_CONFIG["channel_cis"])
        channel_west = await get_config_value(db, "channel_west", DEFAULT_CONFIG["channel_west"])
        chat_general = await get_config_value(db, "chat_general", DEFAULT_CONFIG["chat_general"])

    # Choose channel based on language
    channel = channel_cis if is_cis else channel_west

    # Build Mini App launch URL with ref code
    if ref_code:
        miniapp_launch_url = f"https://t.me/{bot_username}?startapp=ref_{ref_code}"
    else:
        miniapp_launch_url = f"https://t.me/{bot_username}?startapp"

    # Set locale for translations and get localized strings
    set_locale(lang)
    welcome_message = t("bot.welcome")
    labels = BUTTON_LABELS.get(lang, BUTTON_LABELS["en"])

    # Build inline keyboard
    keyboard = [
        [{"text": f"🎮 {labels['launch']}", "url": miniapp_launch_url}],
        [
            {"text": f"📢 {labels['channel']}", "url": f"https://t.me/{channel}"},
            {"text": f"💬 {labels['chat']}", "url": f"https://t.me/{chat_general}"},
        ],
    ]

    # Send banner with buttons
    banner_url = f"{miniapp_url}/banner.png"

    message_id = await send_photo_with_buttons(
        chat_id=telegram_id,
        photo_url=banner_url,
        caption=welcome_message,
        keyboard=keyboard,
    )

    if not message_id:
        # Fallback: send text message if photo fails
        await telegram_notify.send_message(telegram_id, welcome_message, keyboard)
    else:
        # Pin the message and add fire reaction
        await pin_message(telegram_id, message_id)
        await set_message_reaction(telegram_id, message_id, "🔥")

    logger.info(
        f"Sent welcome message to new user {telegram_id} "
        f"(lang: {language_code})"
    )


async def handle_broadcast_command(message: dict) -> None:
    """
    Handle /broadcast command.
    Admin replies to a message with /broadcast to send it to all users.
    Preserves original formatting via entities.

    Usage:
    1. Reply to any message with /broadcast - sends to ALL users
    2. Reply with /broadcast active - sends only to active users (with pets/balance)
    """
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    from_user = message.get("from", {})
    telegram_id = from_user.get("id")
    text = message.get("text", "")

    if not chat_id or not telegram_id:
        return

    # Check if user is broadcast admin
    async with async_session() as db:
        is_admin = await is_broadcast_admin(db, telegram_id)

    if not is_admin:
        await telegram_notify.send_message(
            chat_id,
            "❌ You are not authorized to use this command.\n\nContact the owner to get broadcast access.",
        )
        logger.warning(f"Unauthorized broadcast attempt from {telegram_id}")
        return

    # Check if message is a reply to another message
    reply_to = message.get("reply_to_message")
    if not reply_to:
        await telegram_notify.send_message(
            chat_id,
            "📢 <b>Broadcast Command</b>\n\n"
            "Reply to a message with <code>/broadcast</code> to send it to all users.\n\n"
            "<b>Options:</b>\n"
            "• <code>/broadcast</code> - send to ALL users\n"
            "• <code>/broadcast active</code> - only active users (with pets/balance)\n"
            "• <code>/broadcast pets</code> - only users with pets\n"
            "• <code>/broadcast deposits</code> - only users who deposited\n\n"
            "<b>Supports:</b> text, photos, videos with formatting preserved",
            parse_mode="HTML",
        )
        return

    # Parse target type from command
    parts = text.strip().split()
    target_type = BroadcastTargetType.ALL
    if len(parts) > 1:
        target_arg = parts[1].lower()
        if target_arg == "active":
            target_type = BroadcastTargetType.ACTIVE
        elif target_arg == "pets":
            target_type = BroadcastTargetType.WITH_PETS
        elif target_arg == "deposits":
            target_type = BroadcastTargetType.WITH_DEPOSITS

    # Extract content from replied message
    broadcast_text = reply_to.get("text") or reply_to.get("caption") or ""
    entities = reply_to.get("entities") or reply_to.get("caption_entities")

    # Get photo/video file_id if present
    photo_file_id = None
    video_file_id = None

    photo = reply_to.get("photo")
    if photo and isinstance(photo, list) and len(photo) > 0:
        # Get highest resolution photo (last in array)
        photo_file_id = photo[-1].get("file_id")

    video = reply_to.get("video")
    if video:
        video_file_id = video.get("file_id")

    if not broadcast_text and not photo_file_id and not video_file_id:
        await telegram_notify.send_message(
            chat_id,
            "❌ The replied message has no content to broadcast.",
        )
        return

    # Send progress message
    await telegram_notify.send_message(
        chat_id,
        f"📤 Starting broadcast ({target_type.value})...\nPlease wait.",
    )

    # Create and execute broadcast
    async with async_session() as db:
        try:
            broadcast = await create_broadcast(
                db=db,
                text=broadcast_text,
                target_type=target_type,
                photo_file_id=photo_file_id,
                video_file_id=video_file_id,
                entities=entities,
            )

            stats = await execute_broadcast(db, broadcast.id)

            # Send result
            success_rate = (stats["delivered"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result_message = (
                f"✅ <b>Broadcast Complete!</b>\n\n"
                f"📊 <b>Statistics:</b>\n"
                f"• Total: {stats['total']}\n"
                f"• Delivered: {stats['delivered']}\n"
                f"• Blocked: {stats['blocked']}\n"
                f"• Failed: {stats['failed']}\n"
                f"• Success rate: {success_rate:.1f}%"
            )
            await telegram_notify.send_message(chat_id, result_message, parse_mode="HTML")

            logger.info(
                f"Broadcast #{broadcast.id} completed by admin {telegram_id}: "
                f"{stats['delivered']}/{stats['total']} delivered"
            )

        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            await telegram_notify.send_message(
                chat_id,
                f"❌ Broadcast failed: {str(e)}",
            )


async def handle_start_command(message: dict) -> None:
    """
    Handle /start command with optional referral code.
    Sends banner image with localized message and inline buttons.
    """
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    from_user = message.get("from", {})
    text = message.get("text", "")

    if not chat_id:
        return

    # Extract language from user
    lang_code = from_user.get("language_code")

    # Extract ref_code from /start parameter (e.g., "/start ABC123")
    ref_code = None
    if text.startswith("/start "):
        ref_code = text.split(" ", 1)[1].strip()

    # Use shared function to send welcome
    await send_welcome_to_user(
        telegram_id=chat_id,
        language_code=lang_code,
        ref_code=ref_code,
    )

    logger.info(
        f"Processed /start for user {from_user.get('id')} "
        f"(lang: {lang_code}, ref: {ref_code})"
    )


async def get_admin_by_telegram_id(telegram_id: int) -> Optional[Admin]:
    """Find admin by their Telegram ID (stored in email or separate field)."""
    # For now, we'll just get the first super_admin
    # In production, you'd link admin accounts to telegram IDs
    async with async_session() as db:
        result = await db.execute(select(Admin).limit(1))
        return result.scalar_one_or_none()


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Handle Telegram webhook updates:
    - /start command with optional referral code
    - Callback queries from inline buttons (admin actions)
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail=t("webhook.invalid_json"))

    # Handle /start command
    message = data.get("message")
    if message:
        text = message.get("text", "")
        if text.startswith("/start"):
            await handle_start_command(message)
            return {"ok": True}
        if text.startswith("/broadcast"):
            await handle_broadcast_command(message)
            return {"ok": True}

    # Handle channel posts (for auto-repost feature)
    channel_post = data.get("channel_post")
    if channel_post:
        async with async_session() as db:
            await handle_channel_post(db, channel_post)
        return {"ok": True}

    # Handle callback queries (admin inline buttons)
    callback_query = data.get("callback_query")
    if not callback_query:
        return {"ok": True}

    callback_id = callback_query.get("id")
    callback_data = callback_query.get("data", "")
    from_user = callback_query.get("from", {})
    message = callback_query.get("message", {})
    message_id = message.get("message_id")

    telegram_user_id = from_user.get("id")
    telegram_username = from_user.get("username", "unknown")

    if not callback_data or not message_id:
        await telegram_notify.answer_callback_query(callback_id, t("webhook.invalid_callback"))
        return {"ok": True}

    # Parse callback data: "deposit:approve:123" or "withdraw:complete:456"
    parts = callback_data.split(":")
    if len(parts) != 3:
        await telegram_notify.answer_callback_query(callback_id, t("webhook.invalid_action"))
        return {"ok": True}

    action_type, action, request_id_str = parts

    try:
        request_id = int(request_id_str)
    except ValueError:
        await telegram_notify.answer_callback_query(callback_id, t("webhook.invalid_request_id"))
        return {"ok": True}

    # Get admin (for now, use first admin - in production, verify telegram_id)
    admin = await get_admin_by_telegram_id(telegram_user_id)
    if not admin:
        await telegram_notify.answer_callback_query(
            callback_id, t("webhook.unauthorized"), show_alert=True
        )
        return {"ok": True}

    async with async_session() as db:
        try:
            if action_type == "deposit":
                await handle_deposit_callback(
                    db, action, request_id, admin.id, telegram_username, message_id, callback_id
                )
            elif action_type == "withdraw":
                await handle_withdrawal_callback(
                    db, action, request_id, admin.id, telegram_username, message_id, callback_id
                )
            else:
                await telegram_notify.answer_callback_query(callback_id, t("webhook.unknown_action"))

        except ValueError as e:
            await telegram_notify.answer_callback_query(callback_id, str(e), show_alert=True)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            await telegram_notify.answer_callback_query(
                callback_id, t("webhook.internal_error"), show_alert=True
            )

    return {"ok": True}


async def handle_deposit_callback(
    db,
    action: str,
    deposit_id: int,
    admin_id: int,
    admin_username: str,
    message_id: int,
    callback_id: str,
):
    """Handle deposit approve/reject from inline button."""
    # Get deposit with user info
    result = await db.execute(
        select(DepositRequest)
        .options(joinedload(DepositRequest.user))
        .where(DepositRequest.id == deposit_id)
    )
    deposit = result.scalar_one_or_none()

    if not deposit:
        await telegram_notify.answer_callback_query(callback_id, t("error.deposit_not_found"), show_alert=True)
        return

    if deposit.status != RequestStatus.PENDING:
        status_label = t(f"status.{deposit.status.value.lower()}")
        await telegram_notify.answer_callback_query(
            callback_id, t("error.already_status", status=status_label), show_alert=True
        )
        return

    # Store user info before approve (session will be invalidated after commit)
    user_telegram_id = deposit.user.telegram_id
    user_username = deposit.user.username
    deposit_amount = deposit.amount
    deposit_network = deposit.network

    if action == "approve":
        await approve_deposit(db, deposit_id, admin_id)
        status = RequestStatus.APPROVED
        await telegram_notify.answer_callback_query(callback_id, t("webhook.deposit_approved"))
    elif action == "reject":
        await reject_deposit(db, deposit_id, admin_id)
        status = RequestStatus.REJECTED
        await telegram_notify.answer_callback_query(callback_id, t("webhook.deposit_rejected"))
    else:
        await telegram_notify.answer_callback_query(callback_id, t("webhook.unknown_action"))
        return

    # Update message to remove buttons and show who processed
    await telegram_notify.update_deposit_message(
        message_id=message_id,
        request_id=deposit_id,
        user_telegram_id=user_telegram_id,
        username=user_username,
        amount=deposit_amount,
        network=deposit_network,
        status=status,
        admin_username=admin_username,
    )


async def handle_withdrawal_callback(
    db,
    action: str,
    withdrawal_id: int,
    admin_id: int,
    admin_username: str,
    message_id: int,
    callback_id: str,
):
    """Handle withdrawal complete/reject from inline button."""
    # Get withdrawal with user info
    result = await db.execute(
        select(WithdrawRequest)
        .options(joinedload(WithdrawRequest.user))
        .where(WithdrawRequest.id == withdrawal_id)
    )
    withdrawal = result.scalar_one_or_none()

    if not withdrawal:
        await telegram_notify.answer_callback_query(callback_id, t("error.withdrawal_not_found"), show_alert=True)
        return

    if withdrawal.status != RequestStatus.PENDING:
        status_label = t(f"status.{withdrawal.status.value.lower()}")
        await telegram_notify.answer_callback_query(
            callback_id, t("error.already_status", status=status_label), show_alert=True
        )
        return

    # Store info before processing (session will be invalidated after commit)
    user_telegram_id = withdrawal.user.telegram_id
    user_username = withdrawal.user.username
    withdrawal_amount = withdrawal.amount
    withdrawal_fee = withdrawal.fee
    withdrawal_network = withdrawal.network
    withdrawal_wallet = withdrawal.wallet_address

    if action == "complete":
        await complete_withdrawal(db, withdrawal_id, admin_id)
        status = RequestStatus.COMPLETED
        await telegram_notify.answer_callback_query(callback_id, t("webhook.withdrawal_completed"))
    elif action == "reject":
        await reject_withdrawal(db, withdrawal_id, admin_id)
        status = RequestStatus.REJECTED
        await telegram_notify.answer_callback_query(callback_id, t("webhook.withdrawal_rejected"))
    elif action == "copy":
        # Just show the full address
        await telegram_notify.answer_callback_query(
            callback_id, withdrawal_wallet, show_alert=True
        )
        return
    else:
        await telegram_notify.answer_callback_query(callback_id, t("webhook.unknown_action"))
        return

    # Update message to remove buttons and show who processed
    await telegram_notify.update_withdrawal_message(
        message_id=message_id,
        request_id=withdrawal_id,
        user_telegram_id=user_telegram_id,
        username=user_username,
        amount=withdrawal_amount,
        fee=withdrawal_fee,
        network=withdrawal_network,
        wallet_address=withdrawal_wallet,
        status=status,
        admin_username=admin_username,
    )
