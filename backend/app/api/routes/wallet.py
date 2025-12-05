import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.enums import TxType
from app.schemas.wallet import (
    WalletResponse,
    DepositRequestCreate,
    DepositRequestResponse,
    WithdrawRequestCreate,
    WithdrawRequestResponse,
    TransactionResponse,
    TransactionsListResponse,
)
from app.services.wallet import (
    get_wallet_info,
    create_deposit_request,
    create_withdraw_request,
    get_transactions,
)

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get wallet balance and pending requests count."""
    wallet_info = await get_wallet_info(db, current_user.id, current_user.balance_xpet)
    return WalletResponse(**wallet_info)


@router.post("/deposit-request", response_model=DepositRequestResponse)
async def create_deposit(
    request: DepositRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a deposit request."""
    deposit_request = await create_deposit_request(
        db=db,
        user=current_user,
        amount=request.amount,
        network=request.network,
    )
    return DepositRequestResponse(
        request_id=deposit_request.id,
        amount=deposit_request.amount,
        network=deposit_request.network,
        deposit_address=deposit_request.deposit_address,
        status=deposit_request.status,
        created_at=deposit_request.created_at,
    )


@router.post("/withdraw-request", response_model=WithdrawRequestResponse)
async def create_withdrawal(
    request: WithdrawRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a withdrawal request."""
    try:
        withdraw_request, new_balance = await create_withdraw_request(
            db=db,
            user=current_user,
            amount=request.amount,
            network=request.network,
            wallet_address=request.wallet_address,
        )
        return WithdrawRequestResponse(
            request_id=withdraw_request.id,
            amount=withdraw_request.amount,
            fee=withdraw_request.fee,
            total_deducted=withdraw_request.amount,  # Fee is inside amount now
            network=withdraw_request.network,
            wallet_address=withdraw_request.wallet_address,
            status=withdraw_request.status,
            new_balance=new_balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/transactions", response_model=TransactionsListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[TxType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated transaction history."""
    transactions, total = await get_transactions(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        tx_type=type,
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    return TransactionsListResponse(
        transactions=[TransactionResponse.model_validate(tx) for tx in transactions],
        total=total,
        page=page,
        pages=pages,
    )
