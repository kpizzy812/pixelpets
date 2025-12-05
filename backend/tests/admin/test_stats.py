"""Tests for admin dashboard stats."""
import pytest
from decimal import Decimal


class TestAdminDashboardStatsRoute:
    """Tests for admin dashboard stats endpoint."""

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self, client, super_admin_headers, db_session):
        """Test getting dashboard stats."""
        response = await client.get("/admin/stats/dashboard", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()

        # Check all expected fields
        assert "total_users" in data
        assert "new_users_today" in data
        assert "new_users_week" in data
        assert "active_users_today" in data
        assert "total_balance_xpet" in data
        assert "pending_deposits_count" in data
        assert "pending_deposits_amount" in data
        assert "pending_withdrawals_count" in data
        assert "pending_withdrawals_amount" in data
        assert "total_deposited" in data
        assert "total_withdrawn" in data
        assert "total_pets_active" in data
        assert "total_pets_evolved" in data
        assert "total_claimed_xpet" in data
        assert "total_ref_rewards_paid" in data
        assert "total_task_rewards_paid" in data

    @pytest.mark.asyncio
    async def test_dashboard_stats_with_users(self, client, super_admin_headers, user, rich_user, db_session):
        """Test dashboard stats reflect users."""
        response = await client.get("/admin/stats/dashboard", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] >= 2

    @pytest.mark.asyncio
    async def test_dashboard_stats_with_pending_deposits(
        self, client, super_admin_headers, pending_deposit, db_session
    ):
        """Test dashboard stats reflect pending deposits."""
        response = await client.get("/admin/stats/dashboard", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pending_deposits_count"] >= 1
        assert Decimal(data["pending_deposits_amount"]) >= pending_deposit.amount

    @pytest.mark.asyncio
    async def test_dashboard_stats_with_pending_withdrawals(
        self, client, super_admin_headers, pending_withdrawal, db_session
    ):
        """Test dashboard stats reflect pending withdrawals."""
        response = await client.get("/admin/stats/dashboard", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pending_withdrawals_count"] >= 1

    @pytest.mark.asyncio
    async def test_dashboard_stats_with_pets(
        self, client, super_admin_headers, user_pet, db_session
    ):
        """Test dashboard stats reflect active pets."""
        response = await client.get("/admin/stats/dashboard", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_pets_active"] >= 1

    @pytest.mark.asyncio
    async def test_moderator_can_view_stats(self, client, moderator_headers, db_session):
        """Test moderator can view dashboard stats."""
        response = await client.get("/admin/stats/dashboard", headers=moderator_headers)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_stats_require_auth(self, client, db_session):
        """Test dashboard stats require authentication."""
        response = await client.get("/admin/stats/dashboard")

        assert response.status_code == 401
