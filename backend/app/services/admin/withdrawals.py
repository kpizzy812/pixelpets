from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import (
    WithdrawRequest,
    User,
    Transaction,
    TxType,
    RequestStatus,
    NetworkType,
)


async def get_withdrawals_list(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    status: Optional[RequestStatus] = None,
    network: Optional[NetworkType] = None,
    user_id: Optional[int] = None,
) -> Tuple[List[dict], int]:
    """Get paginated list of withdrawal requests."""
    query = (
        select(WithdrawRequest)
        .options(joinedload(WithdrawRequest.user))
        .order_by(desc(WithdrawRequest.created_at))
    )

    # Filters
    if status:
        query = query.where(WithdrawRequest.status == status)
    if network:
        query = query.where(WithdrawRequest.network == network)
    if user_id:
        query = query.where(WithdrawRequest.user_id == user_id)

    # Count total
    count_query = select(func.count()).select_from(
        select(WithdrawRequest.id)
        .where(
            *(
                [WithdrawRequest.status == status] if status else []
            ) + (
                [WithdrawRequest.network == network] if network else []
            ) + (
                [WithdrawRequest.user_id == user_id] if user_id else []
            )
        )
        .subquery()
    )
    total = (await db.execute(count_query)).scalar() or 0

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    withdrawals = result.scalars().unique().all()

    # Transform to dicts with user info
    items = []
    for wd in withdrawals:
        items.append({
            "id": wd.id,
            "user_id": wd.user_id,
            "telegram_id": wd.user.telegram_id,
            "username": wd.user.username,
            "amount": wd.amount,
            "fee": wd.fee,
            "net_amount": wd.amount - wd.fee,
            "network": wd.network,
            "wallet_address": wd.wallet_address,
            "status": wd.status,
            "created_at": wd.created_at,
            "processed_at": wd.processed_at,
            "processed_by": wd.processed_by,
        })

    return items, total


async def complete_withdrawal(
    db: AsyncSession,
    withdrawal_id: int,
    admin_id: int,
    tx_hash: Optional[str] = None,
) -> WithdrawRequest:
    """Mark withdrawal as completed (already sent)."""
    result = await db.execute(
        select(WithdrawRequest).where(WithdrawRequest.id == withdrawal_id)
    )
    withdrawal = result.scalar_one_or_none()

    if not withdrawal:
        raise ValueError("Withdrawal request not found")

    if withdrawal.status != RequestStatus.PENDING:
        raise ValueError(f"Withdrawal is already {withdrawal.status.value}")

    withdrawal.status = RequestStatus.COMPLETED
    withdrawal.processed_at = datetime.utcnow()
    withdrawal.processed_by = admin_id

    # Transaction was already created when user submitted withdrawal
    # Just update meta with tx_hash if provided
    if tx_hash:
        tx_result = await db.execute(
            select(Transaction).where(
                Transaction.user_id == withdrawal.user_id,
                Transaction.type == TxType.WITHDRAW,
                Transaction.meta.contains({"withdraw_request_id": withdrawal_id}),
            )
        )
        tx = tx_result.scalar_one_or_none()
        if tx and tx.meta:
            tx.meta = {**tx.meta, "tx_hash": tx_hash, "completed_by": admin_id}

    await db.commit()
    await db.refresh(withdrawal)

    return withdrawal


async def reject_withdrawal(
    db: AsyncSession,
    withdrawal_id: int,
    admin_id: int,
    note: Optional[str] = None,
) -> WithdrawRequest:
    """Reject withdrawal and refund user balance."""
    result = await db.execute(
        select(WithdrawRequest)
        .options(joinedload(WithdrawRequest.user))
        .where(WithdrawRequest.id == withdrawal_id)
    )
    withdrawal = result.scalar_one_or_none()

    if not withdrawal:
        raise ValueError("Withdrawal request not found")

    if withdrawal.status != RequestStatus.PENDING:
        raise ValueError(f"Withdrawal is already {withdrawal.status.value}")

    # Refund user (full amount was deducted when they created request, fee is inside)
    user = withdrawal.user
    user.balance_xpet += withdrawal.amount  # Refund the full amount that was deducted

    withdrawal.status = RequestStatus.REJECTED
    withdrawal.processed_at = datetime.utcnow()
    withdrawal.processed_by = admin_id

    # Create refund transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.WITHDRAW_REFUND,
        amount_xpet=withdrawal.amount,
        meta={
            "reason": "Withdrawal rejected",
            "withdrawal_request_id": withdrawal_id,
            "admin_id": admin_id,
            "note": note,
        },
    )
    db.add(tx)

    await db.commit()
    await db.refresh(withdrawal)

    return withdrawal
