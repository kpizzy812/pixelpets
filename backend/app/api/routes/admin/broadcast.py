"""
Admin broadcast routes for mass Telegram messaging.
"""
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import (
    get_current_admin,
    require_admin_or_above,
    get_client_ip,
)
from app.models import Admin, Broadcast, BroadcastLog
from app.models.enums import BroadcastStatus, BroadcastTargetType
from app.schemas.broadcast import (
    BroadcastCreate,
    BroadcastResponse,
    BroadcastListResponse,
    BroadcastPreviewResponse,
    BroadcastSendResponse,
    BroadcastStatsResponse,
)
from app.services.admin.broadcast import (
    create_broadcast,
    get_broadcasts,
    get_broadcast_by_id,
    get_target_users_count,
    execute_broadcast,
    cancel_broadcast,
)
from app.services.admin.config import (
    get_auto_repost_enabled,
    set_auto_repost_enabled,
    get_repost_channel_id,
    set_repost_channel_id,
)
from app.services.channel_repost import repost_to_users, parse_telegram_link
from app.services.admin import log_admin_action

router = APIRouter(prefix="/broadcast", tags=["admin-broadcast"])


@router.post("", response_model=BroadcastResponse)
async def create_new_broadcast(
    data: BroadcastCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Create a new broadcast (draft or scheduled)."""
    # Convert buttons to Telegram format
    buttons_formatted = None
    if data.buttons:
        buttons_formatted = [
            [
                {"text": btn.text, "url": btn.url} if btn.url else {"text": btn.text, "callback_data": btn.callback_data or "noop"}
                for btn in row
            ]
            for row in data.buttons
        ]

    broadcast = await create_broadcast(
        db=db,
        text=data.text,
        target_type=data.target_type,
        photo_file_id=data.photo_file_id,
        video_file_id=data.video_file_id,
        buttons=buttons_formatted,
        min_balance=data.min_balance,
        max_balance=data.max_balance,
        has_pets=data.has_pets,
        min_pets_count=data.min_pets_count,
        has_deposits=data.has_deposits,
        min_deposit_total=data.min_deposit_total,
        registered_after=data.registered_after,
        registered_before=data.registered_before,
        language_codes=data.language_codes,
        custom_user_ids=data.custom_user_ids,
        scheduled_at=data.scheduled_at,
        admin_id=admin.id,
    )

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.create",
        target_type="broadcast",
        target_id=broadcast.id,
        details={
            "target_type": data.target_type.value,
            "scheduled": data.scheduled_at is not None,
        },
        ip_address=get_client_ip(request),
    )

    return BroadcastResponse.model_validate(broadcast)


@router.get("", response_model=BroadcastListResponse)
async def list_broadcasts(
    limit: int = 50,
    offset: int = 0,
    status: Optional[BroadcastStatus] = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List all broadcasts with optional status filter."""
    broadcasts = await get_broadcasts(db, limit=limit, offset=offset, status=status)

    # Get total count
    query = select(func.count(Broadcast.id))
    if status:
        query = query.where(Broadcast.status == status)
    result = await db.execute(query)
    total = result.scalar()

    return BroadcastListResponse(
        items=[BroadcastResponse.model_validate(b) for b in broadcasts],
        total=total,
    )


@router.get("/stats", response_model=BroadcastStatsResponse)
async def get_broadcast_stats(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Get overall broadcast statistics."""
    # Total broadcasts
    result = await db.execute(select(func.count(Broadcast.id)))
    total_broadcasts = result.scalar()

    # Aggregate stats from completed broadcasts
    result = await db.execute(
        select(
            func.sum(Broadcast.sent_count),
            func.sum(Broadcast.delivered_count),
            func.sum(Broadcast.blocked_count),
            func.sum(Broadcast.failed_count),
        ).where(Broadcast.status == BroadcastStatus.COMPLETED)
    )
    row = result.one()
    total_sent = row[0] or 0
    total_delivered = row[1] or 0
    total_blocked = row[2] or 0
    total_failed = row[3] or 0

    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0

    return BroadcastStatsResponse(
        total_broadcasts=total_broadcasts,
        total_messages_sent=total_sent,
        total_delivered=total_delivered,
        total_blocked=total_blocked,
        total_failed=total_failed,
        overall_delivery_rate=round(delivery_rate, 2),
    )


@router.get("/{broadcast_id}", response_model=BroadcastResponse)
async def get_broadcast(
    broadcast_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Get broadcast details."""
    broadcast = await get_broadcast_by_id(db, broadcast_id)

    if not broadcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broadcast not found",
        )

    return BroadcastResponse.model_validate(broadcast)


@router.get("/{broadcast_id}/preview", response_model=BroadcastPreviewResponse)
async def preview_broadcast(
    broadcast_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Preview broadcast with recipient count."""
    broadcast = await get_broadcast_by_id(db, broadcast_id)

    if not broadcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broadcast not found",
        )

    recipient_count = await get_target_users_count(db, broadcast)

    return BroadcastPreviewResponse(
        broadcast_id=broadcast.id,
        target_type=broadcast.target_type,
        recipient_count=recipient_count,
        text_preview=broadcast.text[:200] + "..." if len(broadcast.text) > 200 else broadcast.text,
    )


@router.post("/{broadcast_id}/send", response_model=BroadcastSendResponse)
async def send_broadcast(
    broadcast_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """
    Send a broadcast immediately.
    Note: For large broadcasts, this runs in background and returns initial status.
    """
    broadcast = await get_broadcast_by_id(db, broadcast_id)

    if not broadcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broadcast not found",
        )

    if broadcast.status not in [BroadcastStatus.DRAFT, BroadcastStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Broadcast is already {broadcast.status.value}",
        )

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.send",
        target_type="broadcast",
        target_id=broadcast.id,
        details={"target_type": broadcast.target_type.value},
        ip_address=get_client_ip(request),
    )

    # Execute broadcast
    try:
        stats = await execute_broadcast(db, broadcast_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh broadcast for updated stats
    await db.refresh(broadcast)

    success_rate = (stats["delivered"] / stats["total"] * 100) if stats["total"] > 0 else 0

    return BroadcastSendResponse(
        broadcast_id=broadcast.id,
        status=broadcast.status,
        total=stats["total"],
        sent=stats["sent"],
        delivered=stats["delivered"],
        blocked=stats["blocked"],
        failed=stats["failed"],
        success_rate=round(success_rate, 2),
    )


@router.post("/{broadcast_id}/cancel")
async def cancel_broadcast_route(
    broadcast_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Cancel a scheduled broadcast."""
    success = await cancel_broadcast(db, broadcast_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel broadcast (not found or already sent)",
        )

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.cancel",
        target_type="broadcast",
        target_id=broadcast_id,
        details={},
        ip_address=get_client_ip(request),
    )

    return {"success": True, "message": "Broadcast cancelled"}


@router.delete("/{broadcast_id}")
async def delete_broadcast(
    broadcast_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Delete a broadcast (only drafts or cancelled)."""
    broadcast = await get_broadcast_by_id(db, broadcast_id)

    if not broadcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broadcast not found",
        )

    if broadcast.status not in [BroadcastStatus.DRAFT, BroadcastStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete draft or cancelled broadcasts",
        )

    await db.delete(broadcast)
    await db.commit()

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.delete",
        target_type="broadcast",
        target_id=broadcast_id,
        details={},
        ip_address=get_client_ip(request),
    )

    return {"success": True, "message": "Broadcast deleted"}


# ============== Auto-Repost from Channel ==============

class AutoRepostSettingsResponse(BaseModel):
    """Auto-repost settings response."""
    enabled: bool
    channel_id: Optional[int]


class AutoRepostToggleRequest(BaseModel):
    """Toggle auto-repost."""
    enabled: bool


class AutoRepostChannelRequest(BaseModel):
    """Set channel for auto-repost."""
    channel_id: Optional[int] = None


class RepostLinkRequest(BaseModel):
    """Repost by link."""
    link: str
    only_active: bool = False
    use_forward: bool = True


class RepostResponse(BaseModel):
    """Repost result."""
    total: int
    sent: int
    delivered: int
    blocked: int
    failed: int
    success_rate: float


@router.get("/repost/settings", response_model=AutoRepostSettingsResponse)
async def get_repost_settings(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Get current auto-repost settings."""
    enabled = await get_auto_repost_enabled(db)
    channel_id = await get_repost_channel_id(db)

    return AutoRepostSettingsResponse(
        enabled=enabled,
        channel_id=channel_id,
    )


@router.post("/repost/toggle", response_model=AutoRepostSettingsResponse)
async def toggle_auto_repost(
    data: AutoRepostToggleRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Toggle auto-repost on/off."""
    await set_auto_repost_enabled(db, data.enabled)
    channel_id = await get_repost_channel_id(db)

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.auto_repost_toggle",
        target_type="config",
        target_id=0,
        details={"enabled": data.enabled},
        ip_address=get_client_ip(request),
    )

    return AutoRepostSettingsResponse(
        enabled=data.enabled,
        channel_id=channel_id,
    )


@router.post("/repost/channel", response_model=AutoRepostSettingsResponse)
async def set_repost_channel(
    data: AutoRepostChannelRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Set channel ID for auto-repost."""
    await set_repost_channel_id(db, data.channel_id)
    enabled = await get_auto_repost_enabled(db)

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.set_repost_channel",
        target_type="config",
        target_id=0,
        details={"channel_id": data.channel_id},
        ip_address=get_client_ip(request),
    )

    return AutoRepostSettingsResponse(
        enabled=enabled,
        channel_id=data.channel_id,
    )


@router.post("/repost/link", response_model=RepostResponse)
async def repost_by_link(
    data: RepostLinkRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """
    Repost a message from channel by Telegram link.
    Supports:
    - https://t.me/channel_name/123
    - https://t.me/c/1234567890/123 (private channels)
    """
    # Parse the link
    from_chat_id, message_id = parse_telegram_link(data.link)

    if not from_chat_id or not message_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Telegram link format. Use https://t.me/channel/123",
        )

    # Log action
    await log_admin_action(
        db,
        admin_id=admin.id,
        action="broadcast.repost_by_link",
        target_type="channel",
        target_id=0,
        details={
            "link": data.link,
            "only_active": data.only_active,
        },
        ip_address=get_client_ip(request),
    )

    # Execute repost
    stats = await repost_to_users(
        db=db,
        from_chat_id=from_chat_id,
        message_id=message_id,
        only_active=data.only_active,
        use_forward=data.use_forward,
    )

    success_rate = (stats["delivered"] / stats["total"] * 100) if stats["total"] > 0 else 0

    return RepostResponse(
        total=stats["total"],
        sent=stats["sent"],
        delivered=stats["delivered"],
        blocked=stats["blocked"],
        failed=stats["failed"],
        success_rate=round(success_rate, 2),
    )
