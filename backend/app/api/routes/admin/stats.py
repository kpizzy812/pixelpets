from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import get_current_admin
from app.models import Admin
from app.schemas.admin import DashboardStatsResponse
from app.services.admin import get_dashboard_stats

router = APIRouter(prefix="/stats", tags=["admin-stats"])


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_stats_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Get dashboard statistics."""
    stats = await get_dashboard_stats(db)

    return DashboardStatsResponse(
        total_users=stats["total_users"],
        new_users_today=stats["new_users_today"],
        new_users_week=stats["new_users_week"],
        active_users_today=stats["active_users_today"],
        total_balance_xpet=stats["total_balance_xpet"],
        pending_deposits_count=stats["pending_deposits_count"],
        pending_deposits_amount=stats["pending_deposits_amount"],
        pending_withdrawals_count=stats["pending_withdrawals_count"],
        pending_withdrawals_amount=stats["pending_withdrawals_amount"],
        total_deposited=stats["total_deposited"],
        total_withdrawn=stats["total_withdrawn"],
        total_pets_active=stats["total_pets_active"],
        total_pets_evolved=stats["total_pets_evolved"],
        total_claimed_xpet=stats["total_claimed_xpet"],
        total_ref_rewards_paid=stats["total_ref_rewards_paid"],
        total_task_rewards_paid=stats["total_task_rewards_paid"],
    )
