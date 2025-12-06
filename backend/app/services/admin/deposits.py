import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import (
    DepositRequest,
    User,
    Transaction,
    TxType,
    RequestStatus,
    NetworkType,
)
from app.services.user_notifications import notify_partner_deposited, notify_deposit_approved
from app.i18n import get_text as t


async def get_deposits_list(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    status: Optional[RequestStatus] = None,
    network: Optional[NetworkType] = None,
    user_id: Optional[int] = None,
) -> Tuple[List[dict], int]:
    """Get paginated list of deposit requests."""
    query = (
        select(DepositRequest)
        .options(joinedload(DepositRequest.user))
        .order_by(desc(DepositRequest.created_at))
    )

    # Filters
    if status:
        query = query.where(DepositRequest.status == status)
    if network:
        query = query.where(DepositRequest.network == network)
    if user_id:
        query = query.where(DepositRequest.user_id == user_id)

    # Count total
    count_query = select(func.count()).select_from(
        select(DepositRequest.id)
        .where(
            *(
                [DepositRequest.status == status] if status else []
            ) + (
                [DepositRequest.network == network] if network else []
            ) + (
                [DepositRequest.user_id == user_id] if user_id else []
            )
        )
        .subquery()
    )
    total = (await db.execute(count_query)).scalar() or 0

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    deposits = result.scalars().unique().all()

    # Transform to dicts with user info
    items = []
    for dep in deposits:
        items.append({
            "id": dep.id,
            "user_id": dep.user_id,
            "telegram_id": dep.user.telegram_id,
            "username": dep.user.username,
            "amount": dep.amount,
            "network": dep.network,
            "deposit_address": dep.deposit_address,
            "status": dep.status,
            "created_at": dep.created_at,
            "confirmed_at": dep.confirmed_at,
            "confirmed_by": dep.confirmed_by,
        })

    return items, total


async def approve_deposit(
    db: AsyncSession,
    deposit_id: int,
    admin_id: int,
) -> DepositRequest:
    """Approve deposit request and credit user balance."""
    result = await db.execute(
        select(DepositRequest)
        .options(joinedload(DepositRequest.user))
        .where(DepositRequest.id == deposit_id)
    )
    deposit = result.scalar_one_or_none()

    if not deposit:
        raise ValueError(t("error.deposit_not_found"))

    if deposit.status != RequestStatus.PENDING:
        status_label = t(f"status.{deposit.status.value.lower()}")
        raise ValueError(t("error.already_status", status=status_label))

    # Update deposit status
    deposit.status = RequestStatus.APPROVED
    deposit.confirmed_at = datetime.utcnow()
    deposit.confirmed_by = admin_id

    # Credit user balance
    user = deposit.user
    user.balance_xpet += deposit.amount

    # Create transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.DEPOSIT,
        amount_xpet=deposit.amount,
        meta={
            "deposit_request_id": deposit_id,
            "network": deposit.network.value,
            "approved_by": admin_id,
        },
    )
    db.add(tx)

    await db.commit()
    await db.refresh(deposit)

    # Notify user about deposit approval (fire-and-forget)
    asyncio.create_task(
        notify_deposit_approved(
            user_telegram_id=user.telegram_id,
            amount=deposit.amount,
            locale=user.language_code or "en",
        )
    )

    # Notify referrer about partner's deposit (fire-and-forget)
    if user.referrer_id:
        referrer_result = await db.execute(
            select(User).where(User.id == user.referrer_id)
        )
        referrer = referrer_result.scalar_one_or_none()
        if referrer:
            asyncio.create_task(
                notify_partner_deposited(
                    user_telegram_id=referrer.telegram_id,
                    partner_username=user.username,
                    partner_id=user.telegram_id,
                    amount=deposit.amount,
                    locale=referrer.language_code or "en",
                )
            )

    return deposit


async def reject_deposit(
    db: AsyncSession,
    deposit_id: int,
    admin_id: int,
    note: Optional[str] = None,
) -> DepositRequest:
    """Reject deposit request."""
    result = await db.execute(
        select(DepositRequest).where(DepositRequest.id == deposit_id)
    )
    deposit = result.scalar_one_or_none()

    if not deposit:
        raise ValueError(t("error.deposit_not_found"))

    if deposit.status != RequestStatus.PENDING:
        status_label = t(f"status.{deposit.status.value.lower()}")
        raise ValueError(t("error.already_status", status=status_label))

    deposit.status = RequestStatus.REJECTED
    deposit.confirmed_at = datetime.utcnow()
    deposit.confirmed_by = admin_id

    await db.commit()
    await db.refresh(deposit)

    return deposit
