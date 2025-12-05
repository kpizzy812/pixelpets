from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import Admin, AdminRole
from app.services.admin.auth import get_admin_by_id


security = HTTPBearer()

ADMIN_TOKEN_EXPIRE_HOURS = 24


def create_admin_access_token(admin_id: int) -> str:
    """Create JWT token for admin."""
    expire = datetime.now(timezone.utc) + timedelta(hours=ADMIN_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "sub": str(admin_id),
        "type": "admin",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    """Get current admin from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        admin_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if admin_id is None or token_type != "admin":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    admin = await get_admin_by_id(db, int(admin_id))

    if admin is None:
        raise credentials_exception

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled",
        )

    return admin


def require_role(*allowed_roles: AdminRole):
    """Dependency factory to require specific admin roles."""
    async def role_checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[r.value for r in allowed_roles]}",
            )
        return admin
    return role_checker


# Convenience dependencies
require_super_admin = require_role(AdminRole.SUPER_ADMIN)
require_admin_or_above = require_role(AdminRole.SUPER_ADMIN, AdminRole.ADMIN)
require_any_admin = require_role(AdminRole.SUPER_ADMIN, AdminRole.ADMIN, AdminRole.MODERATOR)


def get_client_ip(request: Request) -> Optional[str]:
    """Get client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
