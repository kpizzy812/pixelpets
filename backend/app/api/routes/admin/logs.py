from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import get_current_admin, require_super_admin
from app.models import Admin
from app.schemas.admin import AdminActionLogListResponse, AdminActionLogResponse
from app.services.admin import get_admin_logs

router = APIRouter(prefix="/logs", tags=["admin-logs"])


@router.get("", response_model=AdminActionLogListResponse)
async def list_admin_logs(
    page: int = 1,
    per_page: int = 50,
    admin_id: int = None,
    action: str = None,
    target_type: str = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_super_admin),
):
    """List admin action logs (super_admin only)."""
    logs, total = await get_admin_logs(
        db,
        page=page,
        per_page=per_page,
        admin_id=admin_id,
        action=action,
        target_type=target_type,
    )

    total_pages = (total + per_page - 1) // per_page

    return AdminActionLogListResponse(
        logs=[AdminActionLogResponse(**log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
