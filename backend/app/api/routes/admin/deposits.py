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
    DepositListResponse,
    DepositDetailResponse,
    DepositActionRequest,
)
from app.services.admin import (
    get_deposits_list,
    approve_deposit,
    reject_deposit,
    log_admin_action,
)

router = APIRouter(prefix="/deposits", tags=["admin-deposits"])


@router.get("", response_model=DepositListResponse)
async def list_deposits(
    page: int = 1,
    per_page: int = 20,
    status: RequestStatus = None,
    network: NetworkType = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List deposit requests with filters."""
    deposits, total = await get_deposits_list(
        db,
        page=page,
        per_page=per_page,
        status=status,
        network=network,
        user_id=user_id,
    )

    total_pages = (total + per_page - 1) // per_page

    return DepositListResponse(
        deposits=[DepositDetailResponse(**d) for d in deposits],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/{deposit_id}/action")
async def process_deposit(
    deposit_id: int,
    request: DepositActionRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Approve or reject deposit request."""
    try:
        if request.action == "approve":
            deposit = await approve_deposit(db, deposit_id, admin.id)
            action_name = "deposit.approve"
        else:
            deposit = await reject_deposit(db, deposit_id, admin.id, request.note)
            action_name = "deposit.reject"
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
        target_type="deposit_request",
        target_id=deposit_id,
        details={
            "amount": str(deposit.amount),
            "network": deposit.network.value,
            "note": request.note,
        },
        ip_address=get_client_ip(http_request),
    )

    return {
        "status": "success",
        "deposit_id": deposit_id,
        "new_status": deposit.status.value,
    }
