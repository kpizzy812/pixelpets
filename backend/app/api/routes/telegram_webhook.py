"""
Telegram webhook handler for inline button callbacks.
"""
import logging
from typing import Optional

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
from app.services import telegram_notify

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


class TelegramUser(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None


class TelegramMessage(BaseModel):
    message_id: int
    chat: dict


class CallbackQuery(BaseModel):
    id: str
    from_: TelegramUser
    message: Optional[TelegramMessage] = None
    data: Optional[str] = None

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class TelegramUpdate(BaseModel):
    update_id: int
    callback_query: Optional[CallbackQuery] = None


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
    Handle Telegram webhook updates (callback queries from inline buttons).
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Only process callback queries
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
        await telegram_notify.answer_callback_query(callback_id, "Invalid callback")
        return {"ok": True}

    # Parse callback data: "deposit:approve:123" or "withdraw:complete:456"
    parts = callback_data.split(":")
    if len(parts) != 3:
        await telegram_notify.answer_callback_query(callback_id, "Invalid action")
        return {"ok": True}

    action_type, action, request_id_str = parts

    try:
        request_id = int(request_id_str)
    except ValueError:
        await telegram_notify.answer_callback_query(callback_id, "Invalid request ID")
        return {"ok": True}

    # Get admin (for now, use first admin - in production, verify telegram_id)
    admin = await get_admin_by_telegram_id(telegram_user_id)
    if not admin:
        await telegram_notify.answer_callback_query(
            callback_id, "You are not authorized", show_alert=True
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
                await telegram_notify.answer_callback_query(callback_id, "Unknown action type")

        except ValueError as e:
            await telegram_notify.answer_callback_query(callback_id, str(e), show_alert=True)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            await telegram_notify.answer_callback_query(
                callback_id, "Internal error", show_alert=True
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
        await telegram_notify.answer_callback_query(callback_id, "Deposit not found", show_alert=True)
        return

    if deposit.status != RequestStatus.PENDING:
        await telegram_notify.answer_callback_query(
            callback_id, f"Already {deposit.status.value}", show_alert=True
        )
        return

    if action == "approve":
        await approve_deposit(db, deposit_id, admin_id)
        status = RequestStatus.APPROVED
        await telegram_notify.answer_callback_query(callback_id, "Deposit approved!")
    elif action == "reject":
        await reject_deposit(db, deposit_id, admin_id)
        status = RequestStatus.REJECTED
        await telegram_notify.answer_callback_query(callback_id, "Deposit rejected")
    else:
        await telegram_notify.answer_callback_query(callback_id, "Unknown action")
        return

    # Update message to remove buttons and show who processed
    await telegram_notify.update_deposit_message(
        message_id=message_id,
        request_id=deposit_id,
        user_telegram_id=deposit.user.telegram_id,
        username=deposit.user.username,
        amount=deposit.amount,
        network=deposit.network,
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
        await telegram_notify.answer_callback_query(callback_id, "Withdrawal not found", show_alert=True)
        return

    if withdrawal.status != RequestStatus.PENDING:
        await telegram_notify.answer_callback_query(
            callback_id, f"Already {withdrawal.status.value}", show_alert=True
        )
        return

    if action == "complete":
        await complete_withdrawal(db, withdrawal_id, admin_id)
        status = RequestStatus.COMPLETED
        await telegram_notify.answer_callback_query(callback_id, "Withdrawal completed!")
    elif action == "reject":
        await reject_withdrawal(db, withdrawal_id, admin_id)
        status = RequestStatus.REJECTED
        await telegram_notify.answer_callback_query(callback_id, "Withdrawal rejected, balance refunded")
    elif action == "copy":
        # Just show the full address
        await telegram_notify.answer_callback_query(
            callback_id, withdrawal.wallet_address, show_alert=True
        )
        return
    else:
        await telegram_notify.answer_callback_query(callback_id, "Unknown action")
        return

    # Update message to remove buttons and show who processed
    await telegram_notify.update_withdrawal_message(
        message_id=message_id,
        request_id=withdrawal_id,
        user_telegram_id=withdrawal.user.telegram_id,
        username=withdrawal.user.username,
        amount=withdrawal.amount,
        fee=withdrawal.fee,
        network=withdrawal.network,
        wallet_address=withdrawal.wallet_address,
        status=status,
        admin_username=admin_username,
    )
