from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.models.task import Task, UserTask
from app.models.transaction import Transaction
from app.models.enums import TaskStatus, TaskType, TxType


async def get_tasks_for_user(db: AsyncSession, user_id: int) -> dict:
    """Get all active tasks with user's completion status."""
    # Get all active tasks
    result = await db.execute(
        select(Task)
        .where(Task.is_active == True)
        .order_by(Task.order, Task.id)
    )
    tasks = list(result.scalars().all())

    # Get user's completed tasks
    result = await db.execute(
        select(UserTask)
        .where(
            UserTask.user_id == user_id,
            UserTask.status == TaskStatus.COMPLETED,
        )
    )
    completed_user_tasks = {ut.task_id: ut for ut in result.scalars().all()}

    # Build response
    tasks_data = []
    total_earned = Decimal("0")
    completed_count = 0

    for task in tasks:
        user_task = completed_user_tasks.get(task.id)
        is_completed = user_task is not None

        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "reward_xpet": task.reward_xpet,
            "link": task.link,
            "task_type": task.task_type,
            "is_completed": is_completed,
            "completed_at": user_task.completed_at if user_task else None,
        }
        tasks_data.append(task_data)

        if is_completed:
            total_earned += task.reward_xpet
            completed_count += 1

    return {
        "tasks": tasks_data,
        "total_earned": total_earned,
        "available_count": len(tasks) - completed_count,
        "completed_count": completed_count,
    }


async def check_task(
    db: AsyncSession,
    user: User,
    task_id: int,
) -> dict:
    """
    Check/complete a task and award XPET.
    Returns result dict or raises ValueError.
    """
    # Get task
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.is_active == True)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise ValueError("Task not found")

    # Check if already completed
    result = await db.execute(
        select(UserTask).where(
            UserTask.user_id == user.id,
            UserTask.task_id == task_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing and existing.status == TaskStatus.COMPLETED:
        raise ValueError("Task already completed")

    # Optional: verify task completion (e.g., Telegram channel subscription)
    # For now, we trust the client
    # verified = await verify_task_completion(user, task)
    # if not verified:
    #     raise ValueError("Task verification failed")

    # Create or update user task
    now = datetime.utcnow()
    if existing:
        existing.status = TaskStatus.COMPLETED
        existing.completed_at = now
    else:
        user_task = UserTask(
            user_id=user.id,
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            completed_at=now,
        )
        db.add(user_task)

    # Credit reward
    user.balance_xpet += task.reward_xpet

    # Record transaction
    tx = Transaction(
        user_id=user.id,
        type=TxType.TASK_REWARD,
        amount_xpet=task.reward_xpet,
        meta={"task_id": task_id, "task_title": task.title},
    )
    db.add(tx)

    await db.commit()

    return {
        "success": True,
        "reward_xpet": task.reward_xpet,
        "new_balance": user.balance_xpet,
        "message": "Task completed!",
    }


async def verify_telegram_subscription(
    user_telegram_id: int,
    channel_username: str,
) -> bool:
    """
    Verify if user is subscribed to a Telegram channel.
    Requires bot to be admin in the channel.
    """
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getChatMember"
        params = {
            "chat_id": f"@{channel_username}",
            "user_id": user_telegram_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("ok"):
            status = data["result"]["status"]
            return status in ["member", "administrator", "creator"]

        return False
    except Exception:
        return False


async def verify_task_completion(user: User, task: Task) -> bool:
    """
    Verify task completion based on task type.
    Returns True if verified or verification not required.
    """
    if task.task_type == TaskType.TELEGRAM_CHANNEL:
        if task.verification_data and task.verification_data.get("channel_id"):
            channel = task.verification_data["channel_id"].lstrip("@")
            return await verify_telegram_subscription(user.telegram_id, channel)

    # For other task types, trust the client
    return True
