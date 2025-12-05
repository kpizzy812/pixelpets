from decimal import Decimal
from typing import Optional
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.transaction import Transaction, DepositRequest, WithdrawRequest
from app.models.enums import NetworkType, RequestStatus, TxType
from app.services import telegram_notify

logger = logging.getLogger(__name__)

WITHDRAW_MIN = Decimal("5")
WITHDRAW_FEE_FIXED = Decimal("1")
WITHDRAW_FEE_PERCENT = Decimal("0.02")

# Deposit addresses per network (in production, these would be dynamically generated)
DEPOSIT_ADDRESSES = {
    NetworkType.BEP20: "0x1234567890abcdef1234567890abcdef12345678",
    NetworkType.SOLANA: "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    NetworkType.TON: "EQDtFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74p4q2",
}


def calculate_withdraw_fee(amount: Decimal) -> Decimal:
    """Calculate withdrawal fee: $1 + 2%."""
    return WITHDRAW_FEE_FIXED + (amount * WITHDRAW_FEE_PERCENT)


async def get_wallet_info(db: AsyncSession, user_id: int, balance_xpet: Decimal) -> dict:
    """Get wallet info including pending requests count."""
    # Count pending deposits
    deposits_result = await db.execute(
        select(func.count(DepositRequest.id)).where(
            DepositRequest.user_id == user_id,
            DepositRequest.status == RequestStatus.PENDING,
        )
    )
    pending_deposits = deposits_result.scalar() or 0

    # Count pending withdrawals
    withdrawals_result = await db.execute(
        select(func.count(WithdrawRequest.id)).where(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == RequestStatus.PENDING,
        )
    )
    pending_withdrawals = withdrawals_result.scalar() or 0

    return {
        "balance_xpet": balance_xpet,
        "balance_usd": balance_xpet,  # 1 XPET = $1 USD
        "pending_deposits": pending_deposits,
        "pending_withdrawals": pending_withdrawals,
    }


async def create_deposit_request(
    db: AsyncSession,
    user: User,
    amount: Decimal,
    network: NetworkType,
) -> DepositRequest:
    """Create a new deposit request."""
    deposit_address = DEPOSIT_ADDRESSES.get(network)

    deposit_request = DepositRequest(
        user_id=user.id,
        amount=amount,
        network=network,
        deposit_address=deposit_address,
        status=RequestStatus.PENDING,
    )
    db.add(deposit_request)
    await db.commit()
    await db.refresh(deposit_request)

    # Send notification to admin group
    try:
        message_id = await telegram_notify.notify_new_deposit(
            request_id=deposit_request.id,
            user_telegram_id=user.telegram_id,
            username=user.username,
            amount=amount,
            network=network,
        )
        if message_id:
            deposit_request.notification_message_id = message_id
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to send deposit notification: {e}")

    return deposit_request


async def create_withdraw_request(
    db: AsyncSession,
    user: User,
    amount: Decimal,
    network: NetworkType,
    wallet_address: str,
) -> tuple[WithdrawRequest, Decimal]:
    """
    Create a withdrawal request.
    Returns (request, new_balance) or raises ValueError.
    """
    if amount < WITHDRAW_MIN:
        raise ValueError(f"Minimum withdrawal is {WITHDRAW_MIN} XPET")

    fee = calculate_withdraw_fee(amount)
    net_amount = amount - fee  # User receives this amount

    if user.balance_xpet < amount:
        raise ValueError("Insufficient balance")

    # Deduct from balance (fee is inside the amount)
    user.balance_xpet -= amount

    # Create request
    withdraw_request = WithdrawRequest(
        user_id=user.id,
        amount=amount,
        fee=fee,
        network=network,
        wallet_address=wallet_address,
        status=RequestStatus.PENDING,
    )
    db.add(withdraw_request)

    # Record transaction (amount is what user requested, fee stored separately)
    tx = Transaction(
        user_id=user.id,
        type=TxType.WITHDRAW,
        amount_xpet=-amount,
        fee=fee,
        meta={
            "network": network.value,
            "wallet_address": wallet_address,
            "request_id": withdraw_request.id,
            "net_amount": float(net_amount),
        },
    )
    db.add(tx)

    await db.commit()
    await db.refresh(withdraw_request)

    # Send notification to admin group
    try:
        message_id = await telegram_notify.notify_new_withdrawal(
            request_id=withdraw_request.id,
            user_telegram_id=user.telegram_id,
            username=user.username,
            amount=amount,
            fee=fee,
            network=network,
            wallet_address=wallet_address,
        )
        if message_id:
            withdraw_request.notification_message_id = message_id
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to send withdrawal notification: {e}")

    return withdraw_request, user.balance_xpet


async def get_transactions(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    limit: int = 20,
    tx_type: Optional[TxType] = None,
) -> tuple[list[Transaction], int]:
    """Get paginated transactions for a user."""
    query = select(Transaction).where(Transaction.user_id == user_id)

    if tx_type:
        query = query.where(Transaction.type == tx_type)

    # Get total count
    count_query = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
    if tx_type:
        count_query = count_query.where(Transaction.type == tx_type)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    offset = (page - 1) * limit
    query = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    transactions = list(result.scalars().all())

    return transactions, total
