from decimal import Decimal
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, UserTask, TaskType, TaskStatus


async def get_all_tasks(
    db: AsyncSession,
    include_inactive: bool = True,
) -> List[Tuple[Task, int]]:
    """Get all tasks with completion counts."""
    query = select(Task).order_by(Task.order, Task.id)

    if not include_inactive:
        query = query.where(Task.is_active == True)

    result = await db.execute(query)
    tasks = list(result.scalars().all())

    # Get completion counts
    tasks_with_counts = []
    for task in tasks:
        count_result = await db.execute(
            select(func.count()).where(
                UserTask.task_id == task.id,
                UserTask.status == TaskStatus.COMPLETED,
            )
        )
        count = count_result.scalar() or 0
        tasks_with_counts.append((task, count))

    return tasks_with_counts


async def get_task_by_id(
    db: AsyncSession,
    task_id: int,
) -> Optional[Task]:
    """Get task by ID."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    title: str,
    reward_xpet: Decimal,
    description: Optional[str] = None,
    link: Optional[str] = None,
    task_type: TaskType = TaskType.OTHER,
    verification_data: Optional[dict] = None,
    is_active: bool = True,
    order: int = 0,
) -> Task:
    """Create new task."""
    task = Task(
        title=title,
        description=description,
        reward_xpet=reward_xpet,
        link=link,
        task_type=task_type,
        verification_data=verification_data,
        is_active=is_active,
        order=order,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession,
    task: Task,
    title: Optional[str] = None,
    description: Optional[str] = None,
    reward_xpet: Optional[Decimal] = None,
    link: Optional[str] = None,
    task_type: Optional[TaskType] = None,
    verification_data: Optional[dict] = None,
    is_active: Optional[bool] = None,
    order: Optional[int] = None,
) -> Task:
    """Update task."""
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if reward_xpet is not None:
        task.reward_xpet = reward_xpet
    if link is not None:
        task.link = link
    if task_type is not None:
        task.task_type = task_type
    if verification_data is not None:
        task.verification_data = verification_data
    if is_active is not None:
        task.is_active = is_active
    if order is not None:
        task.order = order

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession,
    task: Task,
    soft_delete: bool = True,
) -> bool:
    """
    Delete task.
    By default, soft-delete (set is_active=False).
    """
    if soft_delete:
        task.is_active = False
        await db.commit()
    else:
        await db.delete(task)
        await db.commit()

    return True
