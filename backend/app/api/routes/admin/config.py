from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import (
    get_current_admin,
    require_super_admin,
    get_client_ip,
)
from app.models import Admin
from app.schemas.admin import (
    ConfigItemResponse,
    ConfigUpdateRequest,
    ReferralConfigResponse,
    ReferralConfigUpdateRequest,
)
from app.services.admin import (
    get_referral_config,
    update_referral_config,
    log_admin_action,
)
from app.services.admin.config import get_all_configs, set_config

router = APIRouter(prefix="/config", tags=["admin-config"])


@router.get("", response_model=List[ConfigItemResponse])
async def list_configs(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List all system configs."""
    configs = await get_all_configs(db)
    return [ConfigItemResponse.model_validate(c) for c in configs]


# Referral routes MUST come before /{key} to avoid routing conflict
@router.get("/referrals", response_model=ReferralConfigResponse)
async def get_referrals_config(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Get referral system configuration."""
    config = await get_referral_config(db)
    return ReferralConfigResponse(**config)


@router.put("/referrals", response_model=ReferralConfigResponse)
async def update_referrals_config(
    request: ReferralConfigUpdateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_super_admin),
):
    """Update referral system configuration (super_admin only)."""
    config = await update_referral_config(
        db,
        percentages=request.percentages,
        unlock_thresholds=request.unlock_thresholds,
    )

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="config.referrals_update",
        target_type="config",
        target_id=None,
        details={
            "percentages": request.percentages,
            "unlock_thresholds": request.unlock_thresholds,
        },
        ip_address=get_client_ip(http_request),
    )

    return ReferralConfigResponse(**config)


@router.put("/{key}", response_model=ConfigItemResponse)
async def update_config(
    key: str,
    request: ConfigUpdateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_super_admin),
):
    """Update system config (super_admin only)."""
    config = await set_config(db, key, request.value, request.description)

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="config.update",
        target_type="config",
        target_id=None,
        details={"key": key, "value": request.value},
        ip_address=get_client_ip(http_request),
    )

    return ConfigItemResponse.model_validate(config)
