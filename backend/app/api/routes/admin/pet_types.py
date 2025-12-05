from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import (
    get_current_admin,
    require_admin_or_above,
    get_client_ip,
)
from app.models import Admin
from app.schemas.admin import (
    PetTypeResponse,
    PetTypeCreateRequest,
    PetTypeUpdateRequest,
)
from app.services.admin import (
    get_pet_types,
    create_pet_type,
    update_pet_type,
    delete_pet_type,
    log_admin_action,
)
from app.services.admin.pet_types import get_pet_type_by_id
from app.i18n import get_text as t

router = APIRouter(prefix="/pet-types", tags=["admin-pet-types"])


@router.get("", response_model=List[PetTypeResponse])
async def list_pet_types(
    include_inactive: bool = True,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List all pet types."""
    pet_types = await get_pet_types(db, include_inactive=include_inactive)
    return [PetTypeResponse.model_validate(pt) for pt in pet_types]


@router.post("", response_model=PetTypeResponse)
async def create_new_pet_type(
    request: PetTypeCreateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Create new pet type."""
    pet_type = await create_pet_type(
        db,
        name=request.name,
        emoji=request.emoji,
        base_price=request.base_price,
        daily_rate=request.daily_rate,
        roi_cap_multiplier=request.roi_cap_multiplier,
        level_prices=request.level_prices,
        is_active=request.is_active,
    )

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="pet_type.create",
        target_type="pet_type",
        target_id=pet_type.id,
        details={"name": request.name, "base_price": str(request.base_price)},
        ip_address=get_client_ip(http_request),
    )

    return PetTypeResponse.model_validate(pet_type)


@router.patch("/{pet_type_id}", response_model=PetTypeResponse)
async def update_existing_pet_type(
    pet_type_id: int,
    request: PetTypeUpdateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Update pet type."""
    pet_type = await get_pet_type_by_id(db, pet_type_id)

    if not pet_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=t("error.pet_type_not_found"),
        )

    old_values = {
        "name": pet_type.name,
        "base_price": str(pet_type.base_price),
        "daily_rate": str(pet_type.daily_rate),
        "is_active": pet_type.is_active,
    }

    pet_type = await update_pet_type(
        db,
        pet_type,
        name=request.name,
        emoji=request.emoji,
        base_price=request.base_price,
        daily_rate=request.daily_rate,
        roi_cap_multiplier=request.roi_cap_multiplier,
        level_prices=request.level_prices,
        is_active=request.is_active,
    )

    # Convert Decimals to strings for JSON serialization
    changes = request.model_dump(exclude_unset=True, mode="json")

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="pet_type.update",
        target_type="pet_type",
        target_id=pet_type_id,
        details={"old": old_values, "changes": changes},
        ip_address=get_client_ip(http_request),
    )

    return PetTypeResponse.model_validate(pet_type)


@router.delete("/{pet_type_id}")
async def delete_existing_pet_type(
    pet_type_id: int,
    hard_delete: bool = False,
    http_request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Delete pet type (soft delete by default)."""
    pet_type = await get_pet_type_by_id(db, pet_type_id)

    if not pet_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=t("error.pet_type_not_found"),
        )

    await delete_pet_type(db, pet_type, soft_delete=not hard_delete)

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="pet_type.delete",
        target_type="pet_type",
        target_id=pet_type_id,
        details={"name": pet_type.name, "hard_delete": hard_delete},
        ip_address=get_client_ip(http_request) if http_request else None,
    )

    return {"status": "success", "deleted": pet_type_id}
