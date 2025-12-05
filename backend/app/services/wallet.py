from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.transaction import Transaction, DepositRequest, WithdrawRequest
from app.models.enums import NetworkType, RequestStatus, TxType

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
    total_deducted = amount + fee

    if user.balance_xpet < total_deducted:
        raise ValueError("Insufficient balance")

    # Deduct from balance
    user.balance_xpet -= total_deducted

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

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.WITHDRAW,
        amount_xpet=-total_deducted,
        fee=fee,
        meta={
            "network": network.value,
            "wallet_address": wallet_address,
            "request_id": withdraw_request.id,
        },
    )
    db.add(tx)

    await db.commit()
    await db.refresh(withdraw_request)

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
