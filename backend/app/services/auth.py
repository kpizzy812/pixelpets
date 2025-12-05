import asyncio
import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import parse_qs

from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.services.user_notifications import notify_partner_joined


def generate_ref_code(length: int = 8) -> str:
    """Generate a unique referral code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def validate_telegram_init_data(init_data: str) -> Optional[dict]:
    """
    Validate Telegram Mini App initData.
    Returns parsed data if valid, None otherwise.
    """
    try:
        parsed = parse_qs(init_data)

        # Extract hash
        received_hash = parsed.get("hash", [None])[0]
        if not received_hash:
            return None

        # Build data check string (sorted, without hash)
        data_pairs = []
        for key, values in parsed.items():
            if key != "hash":
                data_pairs.append(f"{key}={values[0]}")
        data_pairs.sort()
        data_check_string = "\n".join(data_pairs)

        # Calculate secret key
        secret_key = hmac.new(
            b"WebAppData",
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare hashes
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        # Parse user data
        import json
        user_data = parsed.get("user", [None])[0]
        if user_data:
            return json.loads(user_data)

        return None
    except Exception:
        return None


def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    """Decode JWT access token and return user_id."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return int(user_id)
        return None
    except Exception:
        return None


async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    language_code: str,
    ref_code_from_link: Optional[str] = None,
) -> User:
    """Get existing user or create a new one."""
    # Try to find existing user
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user:
        # Update user info
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.language_code = language_code
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return user

    # Create new user
    referrer = None
    referrer_id = None
    if ref_code_from_link:
        # Find referrer by ref_code
        result = await db.execute(select(User).where(User.ref_code == ref_code_from_link))
        referrer = result.scalar_one_or_none()
        if referrer:
            referrer_id = referrer.id

    # Generate unique ref_code
    while True:
        new_ref_code = generate_ref_code()
        result = await db.execute(select(User).where(User.ref_code == new_ref_code))
        if not result.scalar_one_or_none():
            break

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code,
        ref_code=new_ref_code,
        referrer_id=referrer_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Notify referrer about new partner (fire-and-forget)
    if referrer:
        asyncio.create_task(
            notify_partner_joined(
                user_telegram_id=referrer.telegram_id,
                partner_username=username,
                partner_id=telegram_id,
                locale=referrer.language_code or "en",
            )
        )

    return user
