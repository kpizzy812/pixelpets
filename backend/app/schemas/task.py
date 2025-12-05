from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums import TaskType


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    reward_xpet: Decimal
    link: Optional[str]
    task_type: TaskType
    is_completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TasksListResponse(BaseModel):
    tasks: list[TaskResponse]
    total_earned: Decimal
    available_count: int
    completed_count: int


class TaskCheckRequest(BaseModel):
    task_id: int


class TaskCheckResponse(BaseModel):
    success: bool
    reward_xpet: Decimal
    new_balance: Decimal
    message: str
