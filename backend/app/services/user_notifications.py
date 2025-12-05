"""
User notification service for sending localized messages to users.
"""
import logging
from decimal import Decimal
from typing import Optional

import httpx

from app.core.config import settings
from app.i18n import get_text as t

logger = logging.getLogger(__name__)

BOT_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_user_message(
    chat_id: int,
    text: str,
    parse_mode: str = "HTML",
    reply_markup: Optional[dict] = None,
) -> bool:
    """Send message to user."""
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
                json=payload,
                timeout=10.0,
            )
            return response.json().get("ok", False)
    except Exception as e:
        logger.error(f"Failed to send user message: {e}")
        return False


async def notify_training_complete(
    user_telegram_id: int,
    pet_name: str,
    reward: Decimal,
    locale: str = "en",
) -> bool:
    """Notify user that pet training is complete."""
    message = t("notify.training_complete", locale=locale, pet_name=pet_name, reward=str(reward))
    return await send_user_message(user_telegram_id, message)


async def notify_pet_evolved(
    user_telegram_id: int,
    pet_name: str,
    total_earned: Decimal,
    locale: str = "en",
) -> bool:
    """Notify user that pet has evolved (reached ROI cap)."""
    message = t("notify.pet_evolved", locale=locale, pet_name=pet_name, total=str(total_earned))
    return await send_user_message(user_telegram_id, message)


async def notify_deposit_approved(
    user_telegram_id: int,
    amount: Decimal,
    locale: str = "en",
) -> bool:
    """Notify user that deposit was approved."""
    message = t("notify.deposit_approved", locale=locale, amount=str(amount))
    return await send_user_message(user_telegram_id, message)


async def notify_deposit_rejected(
    user_telegram_id: int,
    locale: str = "en",
) -> bool:
    """Notify user that deposit was rejected."""
    message = t("notify.deposit_rejected", locale=locale)
    return await send_user_message(user_telegram_id, message)


async def notify_withdrawal_approved(
    user_telegram_id: int,
    amount: Decimal,
    tx_hash: str = "",
    locale: str = "en",
) -> bool:
    """Notify user that withdrawal was approved."""
    message = t("notify.withdrawal_approved", locale=locale, amount=str(amount), tx_hash=tx_hash or "pending")
    return await send_user_message(user_telegram_id, message)


async def notify_withdrawal_rejected(
    user_telegram_id: int,
    amount: Decimal,
    reason: str = "",
    locale: str = "en",
) -> bool:
    """Notify user that withdrawal was rejected."""
    message = t("notify.withdrawal_rejected", locale=locale, amount=str(amount), reason=reason or "N/A")
    return await send_user_message(user_telegram_id, message)


async def notify_referral_reward(
    user_telegram_id: int,
    amount: Decimal,
    level: int,
    locale: str = "en",
) -> bool:
    """Notify user about referral reward."""
    message = t("notify.ref_reward", locale=locale, amount=str(amount), level=str(level))
    return await send_user_message(user_telegram_id, message)
