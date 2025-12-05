from datetime import datetime, timezone
from typing import Optional

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Admin, AdminRole


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


async def authenticate_admin(
    db: AsyncSession,
    username: str,
    password: str,
) -> Optional[Admin]:
    """Authenticate admin by username and password."""
    result = await db.execute(
        select(Admin).where(
            Admin.username == username,
            Admin.is_active == True,
        )
    )
    admin = result.scalar_one_or_none()

    if admin and verify_password(password, admin.password_hash):
        admin.last_login_at = datetime.utcnow()
        await db.commit()
        return admin

    return None


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Optional[Admin]:
    """Get admin by ID."""
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    return result.scalar_one_or_none()


async def get_admin_by_username(db: AsyncSession, username: str) -> Optional[Admin]:
    """Get admin by username."""
    result = await db.execute(select(Admin).where(Admin.username == username))
    return result.scalar_one_or_none()


async def create_admin(
    db: AsyncSession,
    username: str,
    password: str,
    email: Optional[str] = None,
    role: AdminRole = AdminRole.MODERATOR,
) -> Admin:
    """Create new admin user."""
    admin = Admin(
        username=username,
        password_hash=hash_password(password),
        email=email,
        role=role,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


async def update_admin(
    db: AsyncSession,
    admin: Admin,
    email: Optional[str] = None,
    role: Optional[AdminRole] = None,
    is_active: Optional[bool] = None,
    password: Optional[str] = None,
) -> Admin:
    """Update admin user."""
    if email is not None:
        admin.email = email
    if role is not None:
        admin.role = role
    if is_active is not None:
        admin.is_active = is_active
    if password is not None:
        admin.password_hash = hash_password(password)

    await db.commit()
    await db.refresh(admin)
    return admin
