from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.task import (
    TasksListResponse,
    TaskResponse,
    TaskCheckRequest,
    TaskCheckResponse,
)
from app.services.tasks import get_tasks_for_user, check_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TasksListResponse)
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks with completion status."""
    data = await get_tasks_for_user(db, current_user.id)

    return TasksListResponse(
        tasks=[TaskResponse(**t) for t in data["tasks"]],
        total_earned=data["total_earned"],
        available_count=data["available_count"],
        completed_count=data["completed_count"],
    )


@router.post("/check", response_model=TaskCheckResponse)
async def check_task_endpoint(
    request: TaskCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check/complete a task and receive reward."""
    try:
        result = await check_task(db, current_user, request.task_id)
        return TaskCheckResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
