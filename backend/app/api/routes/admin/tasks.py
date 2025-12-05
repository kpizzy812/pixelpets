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
    TaskResponse,
    TaskListResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
)
from app.services.admin import (
    get_all_tasks,
    create_task,
    update_task,
    delete_task,
    log_admin_action,
)
from app.services.admin.tasks import get_task_by_id

router = APIRouter(prefix="/tasks", tags=["admin-tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    include_inactive: bool = True,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """List all tasks with completion counts."""
    tasks_with_counts = await get_all_tasks(db, include_inactive=include_inactive)

    task_responses = []
    for task, count in tasks_with_counts:
        response = TaskResponse.model_validate(task)
        response.completions_count = count
        task_responses.append(response)

    return TaskListResponse(
        tasks=task_responses,
        total=len(task_responses),
    )


@router.post("", response_model=TaskResponse)
async def create_new_task(
    request: TaskCreateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Create new task."""
    task = await create_task(
        db,
        title=request.title,
        description=request.description,
        reward_xpet=request.reward_xpet,
        link=request.link,
        task_type=request.task_type,
        verification_data=request.verification_data,
        is_active=request.is_active,
        order=request.order,
    )

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="task.create",
        target_type="task",
        target_id=task.id,
        details={"title": request.title, "reward": str(request.reward_xpet)},
        ip_address=get_client_ip(http_request),
    )

    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
    task_id: int,
    request: TaskUpdateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Update task."""
    task = await get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    old_values = {
        "title": task.title,
        "reward": str(task.reward_xpet),
        "is_active": task.is_active,
    }

    task = await update_task(
        db,
        task,
        title=request.title,
        description=request.description,
        reward_xpet=request.reward_xpet,
        link=request.link,
        task_type=request.task_type,
        verification_data=request.verification_data,
        is_active=request.is_active,
        order=request.order,
    )

    # Convert Decimals to strings for JSON serialization
    changes = request.model_dump(exclude_unset=True, mode="json")

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="task.update",
        target_type="task",
        target_id=task_id,
        details={"old": old_values, "changes": changes},
        ip_address=get_client_ip(http_request),
    )

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}")
async def delete_existing_task(
    task_id: int,
    hard_delete: bool = False,
    http_request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_admin_or_above),
):
    """Delete task (soft delete by default)."""
    task = await get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await delete_task(db, task, soft_delete=not hard_delete)

    await log_admin_action(
        db,
        admin_id=admin.id,
        action="task.delete",
        target_type="task",
        target_id=task_id,
        details={"title": task.title, "hard_delete": hard_delete},
        ip_address=get_client_ip(http_request) if http_request else None,
    )

    return {"status": "success", "deleted": task_id}
