"""
Tests for tasks service and routes.
"""
import pytest
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select

from app.models import User, Task, UserTask, Transaction, TaskType, TaskStatus, TxType
from app.services.tasks import (
    get_tasks_for_user,
    check_task,
    verify_telegram_subscription,
    verify_task_completion,
)


class TestTasksService:
    """Tests for tasks service functions."""

    @pytest.mark.asyncio
    async def test_get_tasks_for_user_no_tasks(self, db_session, user):
        """Test getting tasks when none exist."""
        result = await get_tasks_for_user(db_session, user.id)
        assert result["tasks"] == []
        assert result["total_earned"] == Decimal("0")
        assert result["available_count"] == 0
        assert result["completed_count"] == 0

    @pytest.mark.asyncio
    async def test_get_tasks_for_user_with_tasks(self, db_session, user, tasks):
        """Test getting tasks with data."""
        result = await get_tasks_for_user(db_session, user.id)

        # Should only include active tasks (2 out of 3)
        assert len(result["tasks"]) == 2
        assert result["available_count"] == 2
        assert result["completed_count"] == 0

    @pytest.mark.asyncio
    async def test_get_tasks_for_user_shows_completion_status(self, db_session, user, tasks):
        """Test that tasks show completion status."""
        # Complete one task
        user_task = UserTask(
            user_id=user.id,
            task_id=tasks[0].id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow(),
        )
        db_session.add(user_task)
        await db_session.commit()

        result = await get_tasks_for_user(db_session, user.id)

        completed_tasks = [t for t in result["tasks"] if t["is_completed"]]
        assert len(completed_tasks) == 1
        assert result["completed_count"] == 1
        assert result["available_count"] == 1

    @pytest.mark.asyncio
    async def test_get_tasks_for_user_calculates_total_earned(self, db_session, user, tasks):
        """Test total earned calculation."""
        # Complete first task (0.30 XPET)
        user_task = UserTask(
            user_id=user.id,
            task_id=tasks[0].id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow(),
        )
        db_session.add(user_task)
        await db_session.commit()

        result = await get_tasks_for_user(db_session, user.id)
        assert result["total_earned"] == Decimal("0.30")

    @pytest.mark.asyncio
    async def test_get_tasks_excludes_inactive(self, db_session, user, tasks):
        """Test that inactive tasks are not returned."""
        result = await get_tasks_for_user(db_session, user.id)
        task_ids = [t["id"] for t in result["tasks"]]
        # The inactive task (tasks[2]) should not be in the list
        assert tasks[2].id not in task_ids


class TestCheckTask:
    """Tests for task completion."""

    @pytest.mark.asyncio
    async def test_check_task_success(self, db_session, user, tasks):
        """Test successful task completion."""
        initial_balance = user.balance_xpet
        task = tasks[0]  # 0.30 XPET reward

        result = await check_task(db_session, user, task.id)

        assert result["success"] is True
        assert result["reward_xpet"] == task.reward_xpet
        assert result["new_balance"] == initial_balance + task.reward_xpet
        assert "message" in result

    @pytest.mark.asyncio
    async def test_check_task_creates_user_task(self, db_session, user, tasks):
        """Test that UserTask record is created."""
        task = tasks[0]

        await check_task(db_session, user, task.id)

        result = await db_session.execute(
            select(UserTask).where(
                UserTask.user_id == user.id,
                UserTask.task_id == task.id
            )
        )
        user_task = result.scalar_one()
        assert user_task.status == TaskStatus.COMPLETED
        assert user_task.completed_at is not None

    @pytest.mark.asyncio
    async def test_check_task_creates_transaction(self, db_session, user, tasks):
        """Test that transaction is recorded."""
        task = tasks[0]

        await check_task(db_session, user, task.id)

        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.type == TxType.TASK_REWARD
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet == task.reward_xpet
        assert tx.meta["task_id"] == task.id

    @pytest.mark.asyncio
    async def test_check_task_credits_balance(self, db_session, user, tasks):
        """Test that balance is credited."""
        initial_balance = user.balance_xpet
        task = tasks[0]

        await check_task(db_session, user, task.id)

        await db_session.refresh(user)
        assert user.balance_xpet == initial_balance + task.reward_xpet

    @pytest.mark.asyncio
    async def test_check_task_not_found(self, db_session, user):
        """Test checking non-existent task."""
        with pytest.raises(ValueError, match="Task not found"):
            await check_task(db_session, user, 99999)

    @pytest.mark.asyncio
    async def test_check_task_inactive(self, db_session, user, tasks):
        """Test checking inactive task."""
        inactive_task = tasks[2]  # The inactive one

        with pytest.raises(ValueError, match="Task not found"):
            await check_task(db_session, user, inactive_task.id)

    @pytest.mark.asyncio
    async def test_check_task_already_completed(self, db_session, user, tasks):
        """Test cannot complete task twice."""
        task = tasks[0]

        # Complete once
        await check_task(db_session, user, task.id)

        # Try to complete again
        with pytest.raises(ValueError, match="already completed"):
            await check_task(db_session, user, task.id)

    @pytest.mark.asyncio
    async def test_check_task_updates_existing_pending(self, db_session, user, tasks):
        """Test completing task with existing PENDING record."""
        task = tasks[0]

        # Create pending user task
        user_task = UserTask(
            user_id=user.id,
            task_id=task.id,
            status=TaskStatus.PENDING,
        )
        db_session.add(user_task)
        await db_session.commit()

        # Complete it
        result = await check_task(db_session, user, task.id)

        assert result["success"] is True

        # Verify status updated
        await db_session.refresh(user_task)
        assert user_task.status == TaskStatus.COMPLETED


class TestTaskVerification:
    """Tests for task verification (integration tests require real API)."""

    @pytest.mark.asyncio
    async def test_verify_task_completion_non_telegram(self, db_session):
        """Test verification for non-Telegram tasks."""
        task = Task(
            title="Test Website",
            reward_xpet=Decimal("0.10"),
            task_type=TaskType.WEBSITE,
            is_active=True,
        )
        db_session.add(task)
        await db_session.commit()

        user = User(
            telegram_id=123,
            ref_code="VERIFY",
            language_code="en",
        )
        db_session.add(user)
        await db_session.commit()

        # Non-Telegram tasks should auto-verify
        result = await verify_task_completion(user, task)
        assert result is True


class TestTaskRoutes:
    """Tests for task API routes."""

    @pytest.mark.asyncio
    async def test_get_tasks(self, client, user, auth_headers, tasks):
        """Test getting task list."""
        response = await client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total_earned" in data
        assert "available_count" in data
        assert "completed_count" in data

    @pytest.mark.asyncio
    async def test_get_tasks_structure(self, client, user, auth_headers, tasks):
        """Test task response structure."""
        response = await client.get("/tasks", headers=auth_headers)
        data = response.json()

        for task in data["tasks"]:
            assert "id" in task
            assert "title" in task
            assert "reward_xpet" in task
            assert "task_type" in task
            assert "is_completed" in task

    @pytest.mark.asyncio
    async def test_get_tasks_only_active(self, client, user, auth_headers, tasks):
        """Test only active tasks returned."""
        response = await client.get("/tasks", headers=auth_headers)
        data = response.json()

        # Should have 2 active tasks
        assert len(data["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_check_task_route(self, client, user, auth_headers, tasks):
        """Test completing task via API."""
        task = tasks[0]

        response = await client.post(
            "/tasks/check",
            headers=auth_headers,
            json={"task_id": task.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["reward_xpet"] == str(task.reward_xpet)

    @pytest.mark.asyncio
    async def test_check_task_not_found_route(self, client, user, auth_headers):
        """Test completing non-existent task via API."""
        response = await client.post(
            "/tasks/check",
            headers=auth_headers,
            json={"task_id": 99999}
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_check_task_already_completed_route(self, client, user, auth_headers, tasks, db_session):
        """Test completing already completed task via API."""
        task = tasks[0]

        # Complete it first
        user_task = UserTask(
            user_id=user.id,
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow(),
        )
        db_session.add(user_task)
        await db_session.commit()

        response = await client.post(
            "/tasks/check",
            headers=auth_headers,
            json={"task_id": task.id}
        )
        assert response.status_code == 400
        assert "already completed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_tasks_unauthorized(self, client):
        """Test task routes require auth."""
        response = await client.get("/tasks")
        assert response.status_code == 401

        response = await client.post("/tasks/check", json={"task_id": 1})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_complete_multiple_tasks(self, client, user, auth_headers, tasks, db_session):
        """Test completing multiple tasks."""
        # Complete both active tasks
        for task in tasks[:2]:
            response = await client.post(
                "/tasks/check",
                headers=auth_headers,
                json={"task_id": task.id}
            )
            assert response.status_code == 200

        # Check stats
        response = await client.get("/tasks", headers=auth_headers)
        data = response.json()
        assert data["completed_count"] == 2
        assert data["available_count"] == 0
        # 0.30 + 0.20 = 0.50
        assert Decimal(data["total_earned"]) == Decimal("0.50")
