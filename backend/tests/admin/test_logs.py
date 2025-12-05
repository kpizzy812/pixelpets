"""Tests for admin action logs."""
import pytest

from app.models import AdminActionLog


class TestAdminLogsRoute:
    """Tests for admin logs endpoint."""

    @pytest.mark.asyncio
    async def test_get_logs_empty(self, client, super_admin_headers, db_session):
        """Test getting logs when empty."""
        response = await client.get("/admin/logs", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["logs"] == []

    @pytest.mark.asyncio
    async def test_action_creates_log(self, client, admin_headers, admin_user, user, db_session):
        """Test admin action creates audit log."""
        # Perform an action that logs
        await client.post(
            f"/admin/users/{user.id}/balance",
            headers=admin_headers,
            json={"amount": "10.00", "reason": "Test log creation"}
        )

        # Check logs as super admin
        from app.core.admin_security import create_admin_access_token
        from sqlalchemy import select
        from app.models import Admin, AdminRole

        # Create a super admin for this test
        super_admin = Admin(
            username="logtester",
            password_hash="test",
            role=AdminRole.SUPER_ADMIN,
            is_active=True,
        )
        db_session.add(super_admin)
        await db_session.commit()
        await db_session.refresh(super_admin)

        token = create_admin_access_token(super_admin.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/admin/logs", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(log["action"] == "user.balance_adjust" for log in data["logs"])

    @pytest.mark.asyncio
    async def test_admin_cannot_view_logs(self, client, admin_headers, db_session):
        """Test regular admin cannot view logs."""
        response = await client.get("/admin/logs", headers=admin_headers)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_moderator_cannot_view_logs(self, client, moderator_headers, db_session):
        """Test moderator cannot view logs."""
        response = await client.get("/admin/logs", headers=moderator_headers)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_logs_pagination(self, client, super_admin_headers, user, db_session):
        """Test logs pagination."""
        # Create multiple logs via balance adjustments
        for i in range(5):
            await client.post(
                f"/admin/users/{user.id}/balance",
                headers=super_admin_headers,
                json={"amount": "1.00", "reason": f"Test {i}"}
            )

        response = await client.get(
            "/admin/logs",
            params={"page": 1, "per_page": 2},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 2
        assert data["total"] >= 5
        assert data["total_pages"] >= 3

    @pytest.mark.asyncio
    async def test_filter_logs_by_action(self, client, super_admin_headers, user, db_session):
        """Test filtering logs by action type."""
        # Create a log
        await client.post(
            f"/admin/users/{user.id}/balance",
            headers=super_admin_headers,
            json={"amount": "5.00", "reason": "Test filter"}
        )

        response = await client.get(
            "/admin/logs",
            params={"action": "user.balance_adjust"},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(log["action"] == "user.balance_adjust" for log in data["logs"])
