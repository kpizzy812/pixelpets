from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_security import (
    create_admin_access_token,
    get_current_admin,
    require_super_admin,
)
from app.models import Admin, AdminRole
from app.schemas.admin import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminResponse,
    AdminCreateRequest,
    AdminUpdateRequest,
)
from app.services.admin import (
    authenticate_admin,
    create_admin,
    update_admin,
    get_admin_by_id,
)
from app.services.admin.auth import get_admin_by_username

router = APIRouter()


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Admin login."""
    admin = await authenticate_admin(db, request.username, request.password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_admin_access_token(admin.id)

    return AdminLoginResponse(
        access_token=token,
        admin=AdminResponse.model_validate(admin),
    )


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_profile(
    admin: Admin = Depends(get_current_admin),
):
    """Get current admin profile."""
    return AdminResponse.model_validate(admin)


@router.post("/admins", response_model=AdminResponse)
async def create_new_admin(
    request: AdminCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(require_super_admin),
):
    """Create new admin (super_admin only)."""
    # Check if username exists
    existing = await get_admin_by_username(db, request.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    admin = await create_admin(
        db,
        username=request.username,
        password=request.password,
        email=request.email,
        role=request.role,
    )

    return AdminResponse.model_validate(admin)


@router.patch("/admins/{admin_id}", response_model=AdminResponse)
async def update_admin_user(
    admin_id: int,
    request: AdminUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(require_super_admin),
):
    """Update admin (super_admin only)."""
    admin = await get_admin_by_id(db, admin_id)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )

    # Cannot demote yourself
    if admin.id == current_admin.id and request.role and request.role != admin.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    admin = await update_admin(
        db,
        admin,
        email=request.email,
        role=request.role,
        is_active=request.is_active,
        password=request.password,
    )

    return AdminResponse.model_validate(admin)
