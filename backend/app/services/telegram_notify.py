"""
Telegram notification service for admin alerts.
Sends notifications to admin group with inline keyboard buttons.
"""
import logging
from decimal import Decimal
from typing import Optional

import httpx

from app.core.config import settings
from app.models.enums import NetworkType, RequestStatus

logger = logging.getLogger(__name__)

BOT_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_message(
    chat_id: int,
    text: str,
    reply_markup: Optional[dict] = None,
    parse_mode: str = "HTML",
) -> Optional[int]:
    """
    Send a message to Telegram chat.
    Returns message_id on success, None on failure.
    """
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BOT_API_URL}/sendMessage",
                json=payload,  # Use json= for proper nested object serialization
                timeout=10.0,
            )
            result = response.json()
            if result.get("ok"):
                return result["result"]["message_id"]
            else:
                logger.error(f"Telegram API error: {result}")
                return None
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return None


async def edit_message(
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: Optional[dict] = None,
    parse_mode: str = "HTML",
) -> bool:
    """
    Edit an existing message.
    Returns True on success, False on failure.
    """
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BOT_API_URL}/editMessageText",
                json=payload,  # Use json= for proper nested object serialization
                timeout=10.0,
            )
            result = response.json()
            if result.get("ok"):
                return True
            else:
                logger.error(f"Telegram API error on edit: {result}")
                return False
    except Exception as e:
        logger.error(f"Failed to edit Telegram message: {e}")
        return False


def _network_emoji(network: NetworkType) -> str:
    """Get emoji for network type."""
    return {
        NetworkType.BEP20: "🟡",  # BSC yellow
        NetworkType.SOLANA: "🟣",  # Solana purple
        NetworkType.TON: "🔵",  # TON blue
    }.get(network, "💰")


async def notify_new_deposit(
    request_id: int,
    user_telegram_id: int,
    username: Optional[str],
    amount: Decimal,
    network: NetworkType,
) -> Optional[int]:
    """
    Send notification about new deposit request to admin group.
    Returns message_id for later editing.
    """
    emoji = _network_emoji(network)
    user_display = f"@{username}" if username else f"ID: {user_telegram_id}"

    text = (
        f"💵 <b>Новая заявка на депозит #{request_id}</b>\n\n"
        f"👤 Пользователь: {user_display}\n"
        f"💰 Сумма: <b>{amount} USDT</b>\n"
        f"{emoji} Сеть: <b>{network.value}</b>\n\n"
        f"⏳ Ожидает подтверждения..."
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Подтвердить", "callback_data": f"deposit:approve:{request_id}"},
                {"text": "❌ Отклонить", "callback_data": f"deposit:reject:{request_id}"},
            ]
        ]
    }

    return await send_message(settings.ADMIN_CHAT_ID, text, keyboard)


async def notify_new_withdrawal(
    request_id: int,
    user_telegram_id: int,
    username: Optional[str],
    amount: Decimal,
    fee: Decimal,
    network: NetworkType,
    wallet_address: str,
) -> Optional[int]:
    """
    Send notification about new withdrawal request to admin group.
    Returns message_id for later editing.
    """
    emoji = _network_emoji(network)
    user_display = f"@{username}" if username else f"ID: {user_telegram_id}"

    # Calculate amount to send (amount - fee)
    amount_to_send = amount - fee

    text = (
        f"💸 <b>Новая заявка на вывод #{request_id}</b>\n\n"
        f"👤 Пользователь: {user_display}\n"
        f"💰 Сумма заявки: <b>{amount} USDT</b>\n"
        f"💳 Комиссия: {fee} USDT\n"
        f"📤 <b>К отправке: {amount_to_send} USDT</b>\n"
        f"{emoji} Сеть: <b>{network.value}</b>\n\n"
        f"📬 Кошелек:\n<code>{wallet_address}</code>\n\n"
        f"⏳ Ожидает обработки..."
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Выполнить", "callback_data": f"withdraw:complete:{request_id}"},
                {"text": "❌ Отклонить", "callback_data": f"withdraw:reject:{request_id}"},
            ]
        ]
    }

    return await send_message(settings.ADMIN_CHAT_ID, text, keyboard)


async def update_deposit_message(
    message_id: int,
    request_id: int,
    user_telegram_id: int,
    username: Optional[str],
    amount: Decimal,
    network: NetworkType,
    status: RequestStatus,
    admin_username: str,
) -> bool:
    """Update deposit notification after processing."""
    emoji = _network_emoji(network)
    user_display = f"@{username}" if username else f"ID: {user_telegram_id}"

    if status == RequestStatus.APPROVED:
        status_text = "✅ <b>ПОДТВЕРЖДЕНО</b>"
        status_emoji = "✅"
    else:
        status_text = "❌ <b>ОТКЛОНЕНО</b>"
        status_emoji = "❌"

    text = (
        f"💵 <b>Заявка на депозит #{request_id}</b>\n\n"
        f"👤 Пользователь: {user_display}\n"
        f"💰 Сумма: <b>{amount} USDT</b>\n"
        f"{emoji} Сеть: <b>{network.value}</b>\n\n"
        f"{status_text}\n"
        f"👨‍💼 Обработал: @{admin_username}"
    )

    return await edit_message(settings.ADMIN_CHAT_ID, message_id, text)


async def update_withdrawal_message(
    message_id: int,
    request_id: int,
    user_telegram_id: int,
    username: Optional[str],
    amount: Decimal,
    fee: Decimal,
    network: NetworkType,
    wallet_address: str,
    status: RequestStatus,
    admin_username: str,
) -> bool:
    """Update withdrawal notification after processing."""
    emoji = _network_emoji(network)
    user_display = f"@{username}" if username else f"ID: {user_telegram_id}"
    amount_to_send = amount - fee

    if status == RequestStatus.COMPLETED:
        status_text = "✅ <b>ВЫПОЛНЕНО</b>"
    else:
        status_text = "❌ <b>ОТКЛОНЕНО</b>"

    text = (
        f"💸 <b>Заявка на вывод #{request_id}</b>\n\n"
        f"👤 Пользователь: {user_display}\n"
        f"💰 Сумма заявки: <b>{amount} USDT</b>\n"
        f"💳 Комиссия: {fee} USDT\n"
        f"📤 К отправке: {amount_to_send} USDT\n"
        f"{emoji} Сеть: <b>{network.value}</b>\n\n"
        f"📬 Кошелек:\n<code>{wallet_address}</code>\n\n"
        f"{status_text}\n"
        f"👨‍💼 Обработал: @{admin_username}"
    )

    return await edit_message(settings.ADMIN_CHAT_ID, message_id, text)


async def answer_callback_query(
    callback_query_id: str,
    text: Optional[str] = None,
    show_alert: bool = False,
) -> bool:
    """Answer callback query to remove loading state from button."""
    payload = {
        "callback_query_id": callback_query_id,
    }
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BOT_API_URL}/answerCallbackQuery",
                data=payload,
                timeout=10.0,
            )
            return response.json().get("ok", False)
    except Exception as e:
        logger.error(f"Failed to answer callback query: {e}")
        return False
