"""
API endpoint для интеграции с Syntra (Tradient AI)
Позволяет проверить регистрацию пользователя и наличие питомцев
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.pet import UserPet
from app.models.enums import PetStatus
from app.schemas.user import SyntraVerifyResponse

router = APIRouter(prefix="/syntra", tags=["syntra"])


@router.get("/verify/{telegram_id}", response_model=SyntraVerifyResponse)
async def verify_user_for_syntra(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Проверить статус пользователя для Syntra заданий

    Args:
        telegram_id: Telegram ID пользователя

    Returns:
        SyntraVerifyResponse: Информация о регистрации и питомцах
    """
    # Проверяем существование пользователя
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Пользователь не зарегистрирован
        return SyntraVerifyResponse(
            is_registered=False,
            has_pet=False,
            pets_count=0,
            total_invested=Decimal("0"),
            registered_at=None,
        )

    # Считаем питомцев (не проданных)
    pets_result = await db.execute(
        select(func.count(UserPet.id)).where(
            UserPet.user_id == user.id,
            UserPet.status != PetStatus.SOLD,
        )
    )
    pets_count = pets_result.scalar() or 0

    # Считаем общие инвестиции
    invested_result = await db.execute(
        select(func.coalesce(func.sum(UserPet.invested_total), 0)).where(
            UserPet.user_id == user.id,
            UserPet.status != PetStatus.SOLD,
        )
    )
    total_invested = invested_result.scalar() or Decimal("0")

    return SyntraVerifyResponse(
        is_registered=True,
        has_pet=pets_count > 0,
        pets_count=pets_count,
        total_invested=total_invested,
        registered_at=user.created_at,
    )
