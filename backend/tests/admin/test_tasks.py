"""Tests for admin tasks management."""
import pytest
from decimal import Decimal

from sqlalchemy import select
from app.models import Task, TaskType


class TestAdminTasksListRoute:
    """Tests for admin tasks list endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks(self, client, super_admin_headers, tasks, db_session):
        """Test listing tasks."""
        response = await client.get("/admin/tasks", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2  # 2 active tasks in fixture
        assert len(data["tasks"]) >= 2

    @pytest.mark.asyncio
    async def test_tasks_include_completion_count(self, client, super_admin_headers, tasks, db_session):
        """Test tasks include completion count."""
        response = await client.get("/admin/tasks", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert "completions_count" in task

    @pytest.mark.asyncio
    async def test_list_tasks_includes_inactive(self, client, super_admin_headers, tasks, db_session):
        """Test listing includes inactive tasks."""
        response = await client.get(
            "/admin/tasks",
            params={"include_inactive": True},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert any(t["is_active"] is False for t in data["tasks"])


class TestAdminTasksCreateRoute:
    """Tests for admin tasks create endpoint."""

    @pytest.mark.asyncio
    async def test_create_task(self, client, admin_headers, db_session):
        """Test creating a new task."""
        response = await client.post(
            "/admin/tasks",
            headers=admin_headers,
            json={
                "title": "New Task",
                "description": "Test description",
                "reward_xpet": "0.50",
                "link": "https://example.com",
                "task_type": TaskType.WEBSITE.value,
                "is_active": True,
                "order": 10
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Task"
        assert Decimal(data["reward_xpet"]) == Decimal("0.5")
        assert data["task_type"] == TaskType.WEBSITE.value

    @pytest.mark.asyncio
    async def test_create_task_with_verification_data(self, client, admin_headers, db_session):
        """Test creating task with verification data."""
        response = await client.post(
            "/admin/tasks",
            headers=admin_headers,
            json={
                "title": "Join Channel",
                "reward_xpet": "0.30",
                "link": "https://t.me/test",
                "task_type": TaskType.TELEGRAM_CHANNEL.value,
                "verification_data": {"channel_id": "@testchannel"}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["verification_data"]["channel_id"] == "@testchannel"

    @pytest.mark.asyncio
    async def test_moderator_cannot_create_task(self, client, moderator_headers, db_session):
        """Test moderator cannot create tasks."""
        response = await client.post(
            "/admin/tasks",
            headers=moderator_headers,
            json={
                "title": "Test",
                "reward_xpet": "0.10"
            }
        )

        assert response.status_code == 403


class TestAdminTasksUpdateRoute:
    """Tests for admin tasks update endpoint."""

    @pytest.mark.asyncio
    async def test_update_task(self, client, admin_headers, tasks, db_session):
        """Test updating a task."""
        task = tasks[0]

        response = await client.patch(
            f"/admin/tasks/{task.id}",
            headers=admin_headers,
            json={"title": "Updated Task", "reward_xpet": "0.40"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert Decimal(data["reward_xpet"]) == Decimal("0.4")

    @pytest.mark.asyncio
    async def test_deactivate_task(self, client, admin_headers, tasks, db_session):
        """Test deactivating a task."""
        task = tasks[0]

        response = await client.patch(
            f"/admin/tasks/{task.id}",
            headers=admin_headers,
            json={"is_active": False}
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_task_order(self, client, admin_headers, tasks, db_session):
        """Test updating task order."""
        task = tasks[0]

        response = await client.patch(
            f"/admin/tasks/{task.id}",
            headers=admin_headers,
            json={"order": 99}
        )

        assert response.status_code == 200
        assert response.json()["order"] == 99

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self, client, admin_headers, db_session):
        """Test updating non-existent task."""
        response = await client.patch(
            "/admin/tasks/99999",
            headers=admin_headers,
            json={"title": "Test"}
        )

        assert response.status_code == 404


class TestAdminTasksDeleteRoute:
    """Tests for admin tasks delete endpoint."""

    @pytest.mark.asyncio
    async def test_soft_delete_task(self, client, admin_headers, tasks, db_session):
        """Test soft deleting a task."""
        task = tasks[0]

        response = await client.delete(
            f"/admin/tasks/{task.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        assert response.json()["deleted"] == task.id

        # Verify soft deleted
        await db_session.refresh(task)
        assert task.is_active is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, client, admin_headers, db_session):
        """Test deleting non-existent task."""
        response = await client.delete(
            "/admin/tasks/99999",
            headers=admin_headers
        )

        assert response.status_code == 404
