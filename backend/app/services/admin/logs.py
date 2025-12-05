from typing import Optional, List, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Admin
from app.models.admin_log import AdminActionLog


async def log_admin_action(
    db: AsyncSession,
    admin_id: int,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AdminActionLog:
    """Log an admin action for audit trail."""
    log = AdminActionLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def get_admin_logs(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """Get paginated admin action logs."""
    query = (
        select(AdminActionLog)
        .options(joinedload(AdminActionLog.admin))
        .order_by(desc(AdminActionLog.created_at))
    )

    # Filters
    if admin_id:
        query = query.where(AdminActionLog.admin_id == admin_id)
    if action:
        query = query.where(AdminActionLog.action == action)
    if target_type:
        query = query.where(AdminActionLog.target_type == target_type)

    # Count total
    count_query = select(func.count()).select_from(
        select(AdminActionLog.id)
        .where(
            *(
                [AdminActionLog.admin_id == admin_id] if admin_id else []
            ) + (
                [AdminActionLog.action == action] if action else []
            ) + (
                [AdminActionLog.target_type == target_type] if target_type else []
            )
        )
        .subquery()
    )
    total = (await db.execute(count_query)).scalar() or 0

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    logs = result.scalars().unique().all()

    # Transform to dicts
    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "admin_id": log.admin_id,
            "admin_username": log.admin.username,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        })

    return items, total
