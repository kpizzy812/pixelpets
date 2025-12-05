from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.spin import (
    SpinWheelResponse,
    SpinRewardResponse,
    SpinRequest,
    SpinResultResponse,
    SpinHistoryResponse,
    SpinHistoryEntry,
)
from app.services import spin as spin_service

router = APIRouter(prefix="/spin", tags=["spin"])


@router.get("/wheel", response_model=SpinWheelResponse)
async def get_wheel(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get spin wheel configuration and user's spin status."""
    rewards = await spin_service.get_spin_rewards(db)
    status = await spin_service.get_spin_status(db, current_user.id)

    return SpinWheelResponse(
        rewards=[SpinRewardResponse.model_validate(r) for r in rewards],
        can_free_spin=status["can_free_spin"],
        next_free_spin_at=status["next_free_spin_at"],
        paid_spin_cost=status["paid_spin_cost"],
        spins_today=status["spins_today"],
        winnings_today=status["winnings_today"],
    )


@router.post("/spin", response_model=SpinResultResponse)
async def do_spin(
    request: SpinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform a spin (free or paid)."""
    try:
        user_spin, reward, amount_won = await spin_service.perform_spin(
            db, current_user, is_free=request.is_free
        )

        # Get all rewards to find winning index
        rewards = await spin_service.get_spin_rewards(db)
        winning_index = next(
            (i for i, r in enumerate(rewards) if r.id == reward.id),
            0
        )

        return SpinResultResponse(
            reward=SpinRewardResponse.model_validate(reward),
            amount_won=amount_won,
            new_balance=current_user.balance_xpet,
            was_free_spin=request.is_free,
            winning_index=winning_index,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history", response_model=SpinHistoryResponse)
async def get_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's spin history."""
    spins = await spin_service.get_spin_history(db, current_user.id, limit)

    total_spent = sum(s.cost_xpet for s in spins)
    total_won = sum(s.reward_value for s in spins)

    entries = []
    for spin in spins:
        entries.append(SpinHistoryEntry(
            id=spin.id,
            reward_type=spin.reward_type,
            reward_label=spin.reward.label if spin.reward else "Unknown",
            reward_emoji=spin.reward.emoji if spin.reward else "?",
            amount_won=spin.reward_value,
            cost=spin.cost_xpet,
            was_free=spin.is_free_spin,
            created_at=spin.created_at,
        ))

    return SpinHistoryResponse(
        spins=entries,
        total_spent=total_spent,
        total_won=total_won,
    )
