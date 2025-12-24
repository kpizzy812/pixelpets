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
from app.services.admin.config import (
    get_config_value, DEFAULT_CONFIG, is_broadcast_admin,
    get_auto_repost_enabled, set_auto_repost_enabled,
    get_repost_channel_id, set_repost_channel_id,
)
from app.services import telegram_notify
from app.services.channel_repost import handle_channel_post
from app.services.admin.broadcast import create_broadcast, execute_broadcast, get_target_users_count
from app.models.broadcast import Broadcast
from app.models.enums import BroadcastTargetType
from app.i18n import get_text as t, set_locale

# In-memory storage for pending broadcasts (admin_id -> broadcast_data)
# In production, consider using Redis
PENDING_BROADCASTS: dict[int, dict] = {}

# FSM States for broadcast workflow
class BroadcastState:
    """FSM states for broadcast creation workflow."""
    IDLE = "idle"
    WAITING_CONTENT = "waiting_content"  # Waiting for text/media
    WAITING_BUTTONS = "waiting_buttons"  # Waiting for buttons in format "name - url"
    EDITING = "editing"  # In editing menu, can modify content/buttons

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


def get_admin_menu_keyboard() -> dict:
    """Get main admin menu inline keyboard."""
    return {
        "inline_keyboard": [
            [{"text": "📢 Создать рассылку", "callback_data": "admin:broadcast:new"}],
            [{"text": "📺 Автопост из канала", "callback_data": "admin:repost"}],
            [{"text": "❌ Закрыть", "callback_data": "admin:close"}],
        ]
    }


def get_broadcast_target_keyboard() -> dict:
    """Get broadcast target selection keyboard."""
    return {
        "inline_keyboard": [
            [
                {"text": "👥 Всем пользователям", "callback_data": "bc:target:ALL"},
                {"text": "⚡ Активным", "callback_data": "bc:target:ACTIVE"},
            ],
            [
                {"text": "🐾 С питомцами", "callback_data": "bc:target:WITH_PETS"},
                {"text": "💰 С депозитами", "callback_data": "bc:target:WITH_DEPOSITS"},
            ],
            [
                {"text": "😴 Неактивным", "callback_data": "bc:target:INACTIVE"},
            ],
            [
                {"text": "🔙 Назад", "callback_data": "bc:back_to_edit"},
                {"text": "❌ Отмена", "callback_data": "bc:cancel"},
            ],
        ]
    }


def get_broadcast_edit_keyboard(has_content: bool = False, has_buttons: bool = False) -> dict:
    """Get broadcast editing menu keyboard."""
    content_icon = "✅" if has_content else "📝"
    buttons_icon = "✅" if has_buttons else "🔘"

    keyboard = [
        [{"text": f"{content_icon} Редактировать текст/медиа", "callback_data": "bc:edit:content"}],
        [{"text": f"{buttons_icon} Редактировать кнопки", "callback_data": "bc:edit:buttons"}],
    ]

    if has_content:
        keyboard.append([
            {"text": "👁 Предпросмотр", "callback_data": "bc:preview"},
        ])
        keyboard.append([
            {"text": "📤 Выбрать аудиторию", "callback_data": "bc:select_target"},
        ])

    keyboard.append([{"text": "❌ Отмена", "callback_data": "bc:cancel"}])

    return {"inline_keyboard": keyboard}


def get_confirm_send_keyboard(target_type: str, user_count: int) -> dict:
    """Get confirmation keyboard before sending."""
    return {
        "inline_keyboard": [
            [{"text": f"✅ ОТПРАВИТЬ ({user_count} получателей)", "callback_data": "bc:confirm:send"}],
            [
                {"text": "👁 Превью", "callback_data": "bc:preview"},
                {"text": "🔙 Назад", "callback_data": "bc:back_to_edit"},
            ],
            [{"text": "❌ Отмена", "callback_data": "bc:cancel"}],
        ]
    }


def parse_buttons_text(text: str) -> list[list[dict]] | None:
    """
    Parse buttons from text format:
    название1 - https://example.com
    название2 - https://example2.com

    Returns Telegram inline_keyboard format or None if parsing fails.
    """
    if not text or not text.strip():
        return None

    buttons = []
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Support both " - " and " – " (en-dash)
        separator = None
        if " - " in line:
            separator = " - "
        elif " – " in line:
            separator = " – "
        elif " — " in line:
            separator = " — "

        if not separator:
            continue

        parts = line.split(separator, 1)
        if len(parts) != 2:
            continue

        name, url = parts[0].strip(), parts[1].strip()

        # Basic URL validation
        if not url.startswith(("http://", "https://", "tg://")):
            continue

        if name and url:
            buttons.append([{"text": name, "url": url}])

    return buttons if buttons else None


def format_broadcast_summary(pending: dict) -> str:
    """Format broadcast summary for editing menu."""
    text = pending.get("text", "")
    has_photo = bool(pending.get("photo_file_id"))
    has_video = bool(pending.get("video_file_id"))
    buttons = pending.get("buttons", [])

    # Truncate text for display
    display_text = text[:200] + "..." if len(text) > 200 else text
    if not display_text:
        display_text = "<i>Текст не задан</i>"

    media_info = ""
    if has_photo:
        media_info = "📷 Фото"
    elif has_video:
        media_info = "🎬 Видео"
    else:
        media_info = "📝 Только текст"

    buttons_info = f"🔘 Кнопок: {len(buttons)}" if buttons else "🔘 Без кнопок"

    return (
        f"📢 <b>Редактирование рассылки</b>\n\n"
        f"<b>Медиа:</b> {media_info}\n"
        f"<b>Кнопки:</b> {buttons_info}\n\n"
        f"<b>Текст:</b>\n{display_text}"
    )


def get_broadcast_menu_keyboard() -> dict:
    """Get main broadcast menu inline keyboard (legacy - for /broadcast reply mode)."""
    return {
        "inline_keyboard": [
            [
                {"text": "👥 Всем пользователям", "callback_data": "bc:target:ALL"},
                {"text": "⚡ Активным", "callback_data": "bc:target:ACTIVE"},
            ],
            [
                {"text": "🐾 С питомцами", "callback_data": "bc:target:WITH_PETS"},
                {"text": "💰 С депозитами", "callback_data": "bc:target:WITH_DEPOSITS"},
            ],
            [
                {"text": "😴 Неактивным", "callback_data": "bc:target:INACTIVE"},
            ],
            [
                {"text": "❌ Отмена", "callback_data": "bc:cancel"},
            ],
        ]
    }


def get_confirm_keyboard() -> dict:
    """Get confirmation keyboard."""
    return {
        "inline_keyboard": [
            [
                {"text": "✅ ОТПРАВИТЬ", "callback_data": "bc:confirm:send"},
            ],
            [
                {"text": "👁 Превью", "callback_data": "bc:preview"},
                {"text": "🔙 Назад", "callback_data": "bc:back"},
            ],
            [
                {"text": "❌ Отмена", "callback_data": "bc:cancel"},
            ],
        ]
    }


async def handle_admin_command(message: dict) -> None:
    """
    Handle /admin command.
    Shows admin menu with broadcast and other options.
    """
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    from_user = message.get("from", {})
    telegram_id = from_user.get("id")

    if not chat_id or not telegram_id:
        return

    # Check if user is broadcast admin
    async with async_session() as db:
        is_admin = await is_broadcast_admin(db, telegram_id)

    if not is_admin:
        await telegram_notify.send_message(
            chat_id,
            "❌ У вас нет доступа к этой команде.",
        )
        logger.warning(f"Unauthorized admin attempt from {telegram_id}")
        return

    await telegram_notify.send_message(
        chat_id,
        "⚙️ <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML",
    )


async def handle_admin_callback(callback_query: dict) -> None:
    """Handle admin menu callbacks."""
    callback_id = callback_query.get("id")
    callback_data = callback_query.get("data", "")
    from_user = callback_query.get("from", {})
    telegram_id = from_user.get("id")
    message = callback_query.get("message", {})
    message_id = message.get("message_id")
    chat_id = message.get("chat", {}).get("id")

    if not telegram_id or not callback_data.startswith("admin:"):
        return

    # Check admin access
    async with async_session() as db:
        is_admin = await is_broadcast_admin(db, telegram_id)

    if not is_admin:
        await telegram_notify.answer_callback_query(callback_id, "❌ Нет доступа", show_alert=True)
        return

    parts = callback_data.split(":")
    action = parts[1] if len(parts) > 1 else ""

    if action == "close":
        await telegram_notify.edit_message(
            chat_id, message_id,
            "⚙️ Админ-панель закрыта.",
            reply_markup=None,
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    if action == "repost":
        # Show repost settings
        async with async_session() as db:
            enabled = await get_auto_repost_enabled(db)
            channel_id = await get_repost_channel_id(db)

        status = "🟢 Включен" if enabled else "🔴 Выключен"
        channel_text = f"<code>{channel_id}</code>" if channel_id else "❌ Не указан"

        await telegram_notify.edit_message(
            chat_id, message_id,
            f"📺 <b>Автопост из канала</b>\n\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>ID канала:</b> {channel_text}\n\n"
            f"<i>Чтобы указать канал:</i>\n"
            f"<code>/repost -100123456789</code>",
            reply_markup=get_repost_menu_keyboard(enabled, channel_id),
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    if action == "broadcast" and len(parts) > 2 and parts[2] == "new":
        # Initialize new broadcast FSM
        PENDING_BROADCASTS[telegram_id] = {
            "state": BroadcastState.EDITING,
            "text": "",
            "entities": None,
            "photo_file_id": None,
            "video_file_id": None,
            "buttons": [],
            "target_type": None,
            "chat_id": chat_id,
            "menu_message_id": message_id,
        }

        await telegram_notify.edit_message(
            chat_id, message_id,
            format_broadcast_summary(PENDING_BROADCASTS[telegram_id]),
            reply_markup=get_broadcast_edit_keyboard(has_content=False, has_buttons=False),
        )
        await telegram_notify.answer_callback_query(callback_id)
        return


async def handle_fsm_message(message: dict) -> bool:
    """
    Handle incoming messages for FSM states.
    Returns True if message was handled, False otherwise.
    """
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    from_user = message.get("from", {})
    telegram_id = from_user.get("id")

    if not chat_id or not telegram_id:
        return False

    # Check if user has pending broadcast
    pending = PENDING_BROADCASTS.get(telegram_id)
    if not pending:
        return False

    state = pending.get("state", BroadcastState.IDLE)

    # Handle WAITING_CONTENT state
    if state == BroadcastState.WAITING_CONTENT:
        # Extract content from message
        text = message.get("text") or message.get("caption") or ""
        entities = message.get("entities") or message.get("caption_entities")

        # Get photo/video file_id if present
        photo_file_id = None
        video_file_id = None

        photo = message.get("photo")
        if photo and isinstance(photo, list) and len(photo) > 0:
            photo_file_id = photo[-1].get("file_id")

        video = message.get("video")
        if video:
            video_file_id = video.get("file_id")

        if not text and not photo_file_id and not video_file_id:
            await telegram_notify.send_message(
                chat_id,
                "❌ Сообщение пустое. Отправьте текст, фото или видео с текстом.",
            )
            return True

        # Update pending broadcast
        pending["text"] = text
        pending["entities"] = entities
        pending["photo_file_id"] = photo_file_id
        pending["video_file_id"] = video_file_id
        pending["state"] = BroadcastState.EDITING

        # Update menu message
        menu_message_id = pending.get("menu_message_id")
        if menu_message_id:
            has_content = bool(text or photo_file_id or video_file_id)
            has_buttons = bool(pending.get("buttons"))
            await telegram_notify.edit_message(
                chat_id, menu_message_id,
                format_broadcast_summary(pending),
                reply_markup=get_broadcast_edit_keyboard(has_content=has_content, has_buttons=has_buttons),
            )

        await telegram_notify.send_message(
            chat_id,
            "✅ Контент сохранён!",
        )
        return True

    # Handle WAITING_BUTTONS state
    if state == BroadcastState.WAITING_BUTTONS:
        text = message.get("text", "")

        # Check for "skip" command
        if text.lower() in ["пропустить", "skip", "-", "нет"]:
            pending["buttons"] = []
            pending["state"] = BroadcastState.EDITING

            menu_message_id = pending.get("menu_message_id")
            if menu_message_id:
                has_content = bool(pending.get("text") or pending.get("photo_file_id") or pending.get("video_file_id"))
                await telegram_notify.edit_message(
                    chat_id, menu_message_id,
                    format_broadcast_summary(pending),
                    reply_markup=get_broadcast_edit_keyboard(has_content=has_content, has_buttons=False),
                )

            await telegram_notify.send_message(
                chat_id,
                "✅ Кнопки убраны.",
            )
            return True

        # Parse buttons
        buttons = parse_buttons_text(text)
        if not buttons:
            await telegram_notify.send_message(
                chat_id,
                "❌ Не удалось распознать кнопки.\n\n"
                "<b>Формат:</b>\n"
                "<code>Название - https://example.com</code>\n"
                "<code>Вторая кнопка - https://t.me/channel</code>\n\n"
                "Или отправьте <b>пропустить</b> чтобы убрать кнопки.",
                parse_mode="HTML",
            )
            return True

        # Update pending broadcast
        pending["buttons"] = buttons
        pending["state"] = BroadcastState.EDITING

        # Update menu message
        menu_message_id = pending.get("menu_message_id")
        if menu_message_id:
            has_content = bool(pending.get("text") or pending.get("photo_file_id") or pending.get("video_file_id"))
            await telegram_notify.edit_message(
                chat_id, menu_message_id,
                format_broadcast_summary(pending),
                reply_markup=get_broadcast_edit_keyboard(has_content=has_content, has_buttons=True),
            )

        await telegram_notify.send_message(
            chat_id,
            f"✅ Добавлено кнопок: {len(buttons)}",
        )
        return True

    return False


async def handle_broadcast_command(message: dict) -> None:
    """
    Handle /broadcast command (legacy mode).
    Admin replies to a message with /broadcast to show target selection menu.
    Preserves original formatting via entities.
    """
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    from_user = message.get("from", {})
    telegram_id = from_user.get("id")

    if not chat_id or not telegram_id:
        return

    # Check if user is broadcast admin
    async with async_session() as db:
        is_admin = await is_broadcast_admin(db, telegram_id)

    if not is_admin:
        await telegram_notify.send_message(
            chat_id,
            "❌ У вас нет доступа к этой команде.",
        )
        logger.warning(f"Unauthorized broadcast attempt from {telegram_id}")
        return

    # Check if message is a reply to another message
    reply_to = message.get("reply_to_message")
    if not reply_to:
        await telegram_notify.send_message(
            chat_id,
            "📢 <b>Рассылка</b>\n\n"
            "Ответьте на сообщение командой /broadcast чтобы разослать его пользователям.\n\n"
            "<b>Поддерживается:</b> текст, фото, видео с форматированием",
            parse_mode="HTML",
        )
        return

    # Extract content from replied message
    broadcast_text = reply_to.get("text") or reply_to.get("caption") or ""
    entities = reply_to.get("entities") or reply_to.get("caption_entities")

    # Get photo/video file_id if present
    photo_file_id = None
    video_file_id = None

    photo = reply_to.get("photo")
    if photo and isinstance(photo, list) and len(photo) > 0:
        photo_file_id = photo[-1].get("file_id")

    video = reply_to.get("video")
    if video:
        video_file_id = video.get("file_id")

    if not broadcast_text and not photo_file_id and not video_file_id:
        await telegram_notify.send_message(
            chat_id,
            "❌ Сообщение пустое, нечего рассылать.",
        )
        return

    # Store pending broadcast data
    PENDING_BROADCASTS[telegram_id] = {
        "text": broadcast_text,
        "entities": entities,
        "photo_file_id": photo_file_id,
        "video_file_id": video_file_id,
        "target_type": None,
        "chat_id": chat_id,
    }

    # Show target selection menu
    await telegram_notify.send_message(
        chat_id,
        "📢 <b>Выберите аудиторию рассылки:</b>",
        reply_markup=get_broadcast_menu_keyboard(),
        parse_mode="HTML",
    )


async def handle_broadcast_callback(callback_query: dict) -> None:
    """Handle broadcast menu callback queries."""
    callback_id = callback_query.get("id")
    callback_data = callback_query.get("data", "")
    from_user = callback_query.get("from", {})
    telegram_id = from_user.get("id")
    message = callback_query.get("message", {})
    message_id = message.get("message_id")
    chat_id = message.get("chat", {}).get("id")

    if not telegram_id or not callback_data.startswith("bc:"):
        return

    # Check admin access
    async with async_session() as db:
        is_admin = await is_broadcast_admin(db, telegram_id)

    if not is_admin:
        await telegram_notify.answer_callback_query(callback_id, "❌ Нет доступа", show_alert=True)
        return

    parts = callback_data.split(":")
    action = parts[1] if len(parts) > 1 else ""

    # Cancel action
    if action == "cancel":
        PENDING_BROADCASTS.pop(telegram_id, None)
        await telegram_notify.edit_message(
            chat_id, message_id,
            "❌ Рассылка отменена.",
            reply_markup=None,
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Back to menu (legacy /broadcast mode)
    if action == "back":
        await telegram_notify.edit_message(
            chat_id, message_id,
            "📢 <b>Выберите аудиторию рассылки:</b>",
            reply_markup=get_broadcast_menu_keyboard(),
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Back to edit menu
    if action == "back_to_edit":
        pending = PENDING_BROADCASTS.get(telegram_id)
        if not pending:
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла", show_alert=True
            )
            return

        pending["state"] = BroadcastState.EDITING
        has_content = bool(pending.get("text") or pending.get("photo_file_id") or pending.get("video_file_id"))
        has_buttons = bool(pending.get("buttons"))

        await telegram_notify.edit_message(
            chat_id, message_id,
            format_broadcast_summary(pending),
            reply_markup=get_broadcast_edit_keyboard(has_content=has_content, has_buttons=has_buttons),
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Edit content
    if action == "edit" and len(parts) > 2 and parts[2] == "content":
        pending = PENDING_BROADCASTS.get(telegram_id)
        if not pending:
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла", show_alert=True
            )
            return

        pending["state"] = BroadcastState.WAITING_CONTENT
        pending["menu_message_id"] = message_id

        await telegram_notify.edit_message(
            chat_id, message_id,
            "📝 <b>Отправьте текст для рассылки</b>\n\n"
            "Вы можете отправить:\n"
            "• Текст с форматированием (жирный, курсив, ссылки)\n"
            "• Фото с подписью\n"
            "• Видео с подписью\n\n"
            "<i>Форматирование будет сохранено!</i>",
            reply_markup={
                "inline_keyboard": [[{"text": "❌ Отмена", "callback_data": "bc:cancel"}]]
            },
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Edit buttons
    if action == "edit" and len(parts) > 2 and parts[2] == "buttons":
        pending = PENDING_BROADCASTS.get(telegram_id)
        if not pending:
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла", show_alert=True
            )
            return

        pending["state"] = BroadcastState.WAITING_BUTTONS
        pending["menu_message_id"] = message_id

        current_buttons = pending.get("buttons", [])
        current_info = ""
        if current_buttons:
            buttons_text = "\n".join([f"• {btn[0]['text']} → {btn[0]['url']}" for btn in current_buttons])
            current_info = f"\n\n<b>Текущие кнопки:</b>\n{buttons_text}"

        await telegram_notify.edit_message(
            chat_id, message_id,
            f"🔘 <b>Настройка кнопок</b>\n\n"
            f"Отправьте кнопки в формате:\n"
            f"<code>Название - https://ссылка.com</code>\n"
            f"<code>Вторая кнопка - https://t.me/channel</code>\n\n"
            f"Каждая кнопка на новой строке.\n"
            f"Отправьте <b>пропустить</b> чтобы убрать кнопки."
            f"{current_info}",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "🔙 Назад", "callback_data": "bc:back_to_edit"}],
                    [{"text": "❌ Отмена", "callback_data": "bc:cancel"}],
                ]
            },
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Select target audience
    if action == "select_target":
        pending = PENDING_BROADCASTS.get(telegram_id)
        if not pending:
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла", show_alert=True
            )
            return

        pending["menu_message_id"] = message_id

        await telegram_notify.edit_message(
            chat_id, message_id,
            "📢 <b>Выберите аудиторию рассылки:</b>",
            reply_markup=get_broadcast_target_keyboard(),
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Target selection
    if action == "target":
        target_type_str = parts[2] if len(parts) > 2 else "ALL"
        pending = PENDING_BROADCASTS.get(telegram_id)

        if not pending:
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла. Начните заново с /admin", show_alert=True
            )
            return

        target_type = BroadcastTargetType(target_type_str)
        pending["target_type"] = target_type

        # Get user count for this target
        async with async_session() as db:
            # Create temp broadcast to count users
            temp_broadcast = Broadcast(
                text="",
                target_type=target_type,
            )
            user_count = await get_target_users_count(db, temp_broadcast)

        target_labels = {
            "ALL": "👥 Всем пользователям",
            "ACTIVE": "⚡ Активным пользователям",
            "WITH_PETS": "🐾 Пользователям с питомцами",
            "WITH_DEPOSITS": "💰 Пользователям с депозитами",
            "INACTIVE": "😴 Неактивным пользователям",
        }

        # Include buttons info if present
        buttons_count = len(pending.get("buttons", []))
        buttons_info = f"<b>Кнопок:</b> {buttons_count}\n" if buttons_count > 0 else ""

        confirm_text = (
            f"📢 <b>Подтверждение рассылки</b>\n\n"
            f"<b>Аудитория:</b> {target_labels.get(target_type_str, target_type_str)}\n"
            f"<b>Получателей:</b> {user_count}\n"
            f"{buttons_info}\n"
            f"Нажмите <b>Превью</b> чтобы посмотреть сообщение\n"
            f"Нажмите <b>ОТПРАВИТЬ</b> чтобы начать рассылку"
        )

        await telegram_notify.edit_message(
            chat_id, message_id,
            confirm_text,
            reply_markup=get_confirm_send_keyboard(target_type_str, user_count),
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    # Preview
    if action == "preview":
        pending = PENDING_BROADCASTS.get(telegram_id)
        if not pending:
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла", show_alert=True
            )
            return

        # Send preview message with buttons
        from app.services.admin.broadcast import send_telegram_message
        await send_telegram_message(
            chat_id=chat_id,
            text=pending["text"],
            photo_file_id=pending.get("photo_file_id"),
            video_file_id=pending.get("video_file_id"),
            entities=pending.get("entities"),
            buttons=pending.get("buttons"),
        )
        await telegram_notify.answer_callback_query(callback_id, "👆 Превью отправлено выше")
        return

    # Confirm send
    if action == "confirm" and len(parts) > 2 and parts[2] == "send":
        pending = PENDING_BROADCASTS.get(telegram_id)
        if not pending or not pending.get("target_type"):
            await telegram_notify.answer_callback_query(
                callback_id, "❌ Сессия истекла. Начните заново с /admin", show_alert=True
            )
            return

        # Update message to show progress
        await telegram_notify.edit_message(
            chat_id, message_id,
            "📤 <b>Рассылка запущена...</b>\n\nПожалуйста, подождите.",
            reply_markup=None,
        )
        await telegram_notify.answer_callback_query(callback_id)

        # Execute broadcast
        async with async_session() as db:
            try:
                broadcast = await create_broadcast(
                    db=db,
                    text=pending["text"],
                    target_type=pending["target_type"],
                    photo_file_id=pending.get("photo_file_id"),
                    video_file_id=pending.get("video_file_id"),
                    entities=pending.get("entities"),
                    buttons=pending.get("buttons"),
                )

                stats = await execute_broadcast(db, broadcast.id)

                success_rate = (stats["delivered"] / stats["total"] * 100) if stats["total"] > 0 else 0

                # Format buttons info for report
                buttons_count = len(pending.get("buttons", []))
                buttons_info = f"• Кнопок: {buttons_count}\n" if buttons_count > 0 else ""

                result_message = (
                    f"✅ <b>Рассылка завершена!</b>\n\n"
                    f"📊 <b>Статистика:</b>\n"
                    f"• Всего: {stats['total']}\n"
                    f"• Доставлено: {stats['delivered']}\n"
                    f"• Заблокировано: {stats['blocked']}\n"
                    f"• Ошибок: {stats['failed']}\n"
                    f"{buttons_info}"
                    f"• Успешность: {success_rate:.1f}%"
                )

                await telegram_notify.edit_message(
                    chat_id, message_id,
                    result_message,
                    reply_markup=None,
                )

                logger.info(
                    f"Broadcast #{broadcast.id} completed by admin {telegram_id}: "
                    f"{stats['delivered']}/{stats['total']} delivered"
                )

            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await telegram_notify.edit_message(
                    chat_id, message_id,
                    f"❌ Ошибка рассылки: {str(e)}",
                    reply_markup=None,
                )

        # Clean up
        PENDING_BROADCASTS.pop(telegram_id, None)
        return


def get_repost_menu_keyboard(enabled: bool, channel_id: int | None) -> dict:
    """Get repost settings inline keyboard."""
    toggle_text = "🔴 Выключить" if enabled else "🟢 Включить"
    return {
        "inline_keyboard": [
            [
                {"text": toggle_text, "callback_data": "repost:toggle"},
            ],
            [
                {"text": "📺 Указать канал", "callback_data": "repost:set_channel"},
            ],
            [
                {"text": "❌ Закрыть", "callback_data": "repost:close"},
            ],
        ]
    }


async def handle_repost_command(message: dict) -> None:
    """
    Handle /repost command - manage auto-repost settings.
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
            "❌ У вас нет доступа к этой команде.",
        )
        return

    # Check if setting channel ID: /repost -100123456789
    parts = text.split()
    if len(parts) > 1:
        try:
            channel_id = int(parts[1])
            async with async_session() as db:
                await set_repost_channel_id(db, channel_id)
            await telegram_notify.send_message(
                chat_id,
                f"✅ ID канала установлен: <code>{channel_id}</code>\n\n"
                f"Теперь посты из этого канала будут пересылаться пользователям (если включен автопост).",
                parse_mode="HTML",
            )
            return
        except ValueError:
            pass

    # Show current settings
    async with async_session() as db:
        enabled = await get_auto_repost_enabled(db)
        channel_id = await get_repost_channel_id(db)

    status = "🟢 Включен" if enabled else "🔴 Выключен"
    channel_text = f"<code>{channel_id}</code>" if channel_id else "❌ Не указан"

    await telegram_notify.send_message(
        chat_id,
        f"📺 <b>Автопост из канала</b>\n\n"
        f"<b>Статус:</b> {status}\n"
        f"<b>ID канала:</b> {channel_text}\n\n"
        f"<i>Чтобы указать канал:</i>\n"
        f"<code>/repost -100123456789</code>\n\n"
        f"<i>Как узнать ID канала:</i>\n"
        f"Перешлите любой пост из канала боту @getmyid_bot",
        reply_markup=get_repost_menu_keyboard(enabled, channel_id),
        parse_mode="HTML",
    )


async def handle_repost_callback(callback_query: dict) -> None:
    """Handle repost settings callbacks."""
    callback_id = callback_query.get("id")
    callback_data = callback_query.get("data", "")
    from_user = callback_query.get("from", {})
    telegram_id = from_user.get("id")
    message = callback_query.get("message", {})
    message_id = message.get("message_id")
    chat_id = message.get("chat", {}).get("id")

    if not telegram_id or not callback_data.startswith("repost:"):
        return

    # Check admin access
    async with async_session() as db:
        is_admin = await is_broadcast_admin(db, telegram_id)

    if not is_admin:
        await telegram_notify.answer_callback_query(callback_id, "❌ Нет доступа", show_alert=True)
        return

    action = callback_data.split(":")[1]

    if action == "close":
        await telegram_notify.edit_message(
            chat_id, message_id,
            "📺 Настройки автопоста закрыты.",
            reply_markup=None,
        )
        await telegram_notify.answer_callback_query(callback_id)
        return

    if action == "toggle":
        async with async_session() as db:
            current = await get_auto_repost_enabled(db)
            new_value = not current
            await set_auto_repost_enabled(db, new_value)
            channel_id = await get_repost_channel_id(db)

        status = "🟢 Включен" if new_value else "🔴 Выключен"
        channel_text = f"<code>{channel_id}</code>" if channel_id else "❌ Не указан"

        await telegram_notify.edit_message(
            chat_id, message_id,
            f"📺 <b>Автопост из канала</b>\n\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>ID канала:</b> {channel_text}\n\n"
            f"<i>Чтобы указать канал:</i>\n"
            f"<code>/repost -100123456789</code>",
            reply_markup=get_repost_menu_keyboard(new_value, channel_id),
        )
        await telegram_notify.answer_callback_query(
            callback_id,
            f"Автопост {'включен' if new_value else 'выключен'}!"
        )
        return

    if action == "set_channel":
        await telegram_notify.answer_callback_query(
            callback_id,
            "Отправьте команду:\n/repost -100123456789\n\nГде число - ID вашего канала",
            show_alert=True,
        )
        return


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

    # Handle messages
    message = data.get("message")
    if message:
        text = message.get("text", "")

        # Handle commands
        if text.startswith("/start"):
            await handle_start_command(message)
            return {"ok": True}
        if text.startswith("/admin"):
            await handle_admin_command(message)
            return {"ok": True}
        if text.startswith("/broadcast"):
            await handle_broadcast_command(message)
            return {"ok": True}
        if text.startswith("/repost"):
            await handle_repost_command(message)
            return {"ok": True}

        # Handle FSM states (for broadcast creation workflow)
        if await handle_fsm_message(message):
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

    # Handle admin menu callbacks (admin:*)
    if callback_data.startswith("admin:"):
        await handle_admin_callback(callback_query)
        return {"ok": True}

    # Handle broadcast callbacks (bc:*)
    if callback_data.startswith("bc:"):
        await handle_broadcast_callback(callback_query)
        return {"ok": True}

    # Handle repost callbacks (repost:*)
    if callback_data.startswith("repost:"):
        await handle_repost_callback(callback_query)
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
