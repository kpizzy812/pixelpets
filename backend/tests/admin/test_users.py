"""Tests for admin user management."""
import pytest
from decimal import Decimal

from sqlalchemy import select
from app.models import User, Transaction, TxType


class TestAdminUsersListRoute:
    """Tests for admin users list endpoint."""

    @pytest.mark.asyncio
    async def test_list_users(self, client, super_admin_headers, user, db_session):
        """Test listing users."""
        response = await client.get("/admin/users", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["users"]) >= 1
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client, super_admin_headers, user, rich_user, db_session):
        """Test users pagination."""
        response = await client.get(
            "/admin/users",
            params={"page": 1, "per_page": 1},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 1
        assert data["total"] >= 2
        assert data["total_pages"] >= 2

    @pytest.mark.asyncio
    async def test_search_users_by_username(self, client, super_admin_headers, user, db_session):
        """Test searching users by username."""
        response = await client.get(
            "/admin/users",
            params={"search": "testuser"},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(u["username"] == "testuser" for u in data["users"])

    @pytest.mark.asyncio
    async def test_search_users_by_telegram_id(self, client, super_admin_headers, user, db_session):
        """Test searching users by telegram_id."""
        response = await client.get(
            "/admin/users",
            params={"search": str(user.telegram_id)},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_users_moderator_can_view(self, client, moderator_headers, user, db_session):
        """Test moderator can view users."""
        response = await client.get("/admin/users", headers=moderator_headers)

        assert response.status_code == 200


class TestAdminUserDetailRoute:
    """Tests for admin user detail endpoint."""

    @pytest.mark.asyncio
    async def test_get_user_detail(self, client, super_admin_headers, user, db_session):
        """Test getting user details with stats."""
        response = await client.get(
            f"/admin/users/{user.id}",
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["telegram_id"] == user.telegram_id
        assert data["username"] == user.username
        assert "total_deposited" in data
        assert "total_withdrawn" in data
        assert "total_claimed" in data
        assert "total_ref_earned" in data
        assert "active_pets_count" in data
        assert "referrals_count" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, client, super_admin_headers, db_session):
        """Test getting non-existent user."""
        response = await client.get(
            "/admin/users/99999",
            headers=super_admin_headers
        )

        assert response.status_code == 404


class TestAdminBalanceAdjustRoute:
    """Tests for admin balance adjustment endpoint."""

    @pytest.mark.asyncio
    async def test_add_balance(self, client, admin_headers, user, db_session):
        """Test adding balance to user."""
        old_balance = user.balance_xpet

        response = await client.post(
            f"/admin/users/{user.id}/balance",
            headers=admin_headers,
            json={
                "amount": "50.00",
                "reason": "Test bonus"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["old_balance"]) == old_balance
        assert Decimal(data["new_balance"]) == old_balance + Decimal("50")
        assert data["reason"] == "Test bonus"
        assert "transaction_id" in data

    @pytest.mark.asyncio
    async def test_subtract_balance(self, client, admin_headers, user, db_session):
        """Test subtracting balance from user."""
        old_balance = user.balance_xpet

        response = await client.post(
            f"/admin/users/{user.id}/balance",
            headers=admin_headers,
            json={
                "amount": "-20.00",
                "reason": "Test deduction"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["new_balance"]) == old_balance - Decimal("20")

    @pytest.mark.asyncio
    async def test_subtract_more_than_balance(self, client, admin_headers, user, db_session):
        """Test cannot subtract more than balance."""
        response = await client.post(
            f"/admin/users/{user.id}/balance",
            headers=admin_headers,
            json={
                "amount": "-99999.00",
                "reason": "Too much"
            }
        )

        assert response.status_code == 400
        assert "negative" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_balance_adjust_creates_transaction(self, client, admin_headers, user, db_session):
        """Test balance adjustment creates transaction record."""
        response = await client.post(
            f"/admin/users/{user.id}/balance",
            headers=admin_headers,
            json={
                "amount": "25.00",
                "reason": "Test transaction creation"
            }
        )

        assert response.status_code == 200
        tx_id = response.json()["transaction_id"]

        # Verify transaction exists
        result = await db_session.execute(
            select(Transaction).where(Transaction.id == tx_id)
        )
        tx = result.scalar_one()
        assert tx.type == TxType.ADMIN_ADJUST
        assert tx.amount_xpet == Decimal("25")

    @pytest.mark.asyncio
    async def test_moderator_cannot_adjust_balance(self, client, moderator_headers, user, db_session):
        """Test moderator cannot adjust balance."""
        response = await client.post(
            f"/admin/users/{user.id}/balance",
            headers=moderator_headers,
            json={
                "amount": "50.00",
                "reason": "Should fail"
            }
        )

        assert response.status_code == 403
