from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import (
    get_current_admin,
    require_admin_or_above,
    get_client_ip,
)
from app.models import Admin, RequestStatus, NetworkType
from app.schemas.admin import (
    WithdrawalListResponse,
    WithdrawalDetailResponse,
    WithdrawalActionRequest,
)
from app.services.admin import (
    get_withdrawals_list,
    complete_withdrawal,
    reject_withdrawal,
    log_admin_action,
)

router = APIRouter(prefix="/withdrawals", tags=["admin-withdrawals"])


@router.get("", response_model=WithdrawalListResponse)
async def list_withdrawals(
    page: int = 1,
    per_page: int = 20,
    status: RequestStatus = None,
    network: NetworkType = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List withdrawal requests with filters."""
    withdrawals, total = await get_withdrawals_list(
        db,
        page=page,
        per_page=per_page,
        status=status,
        network=network,
        user_id=user_id,
    )

    total_pages = (total + per_page - 1) // per_page

    return WithdrawalListResponse(
        withdrawals=[WithdrawalDetailResponse(**w) for w in withdrawals],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/{withdrawal_id}/action")
async def process_withdrawal(
    withdrawal_id: int,
    request: WithdrawalActionRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Complete or reject withdrawal request."""
    try:
        if request.action == "complete":
            withdrawal = await complete_withdrawal(
                db, withdrawal_id, admin.id, request.tx_hash
            )
            action_name = "withdrawal.complete"
        else:
            withdrawal = await reject_withdrawal(
                db, withdrawal_id, admin.id, request.note
            )
            action_name = "withdrawal.reject"
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action=action_name,
        target_type="withdraw_request",
        target_id=withdrawal_id,
        details={
            "amount": str(withdrawal.amount),
            "network": withdrawal.network.value,
            "wallet_address": withdrawal.wallet_address,
            "tx_hash": request.tx_hash,
            "note": request.note,
        },
        ip_address=get_client_ip(http_request),
    )

    return {
        "status": "success",
        "withdrawal_id": withdrawal_id,
        "new_status": withdrawal.status.value,
    }
