"""Tests for admin deposit management."""
import pytest
from decimal import Decimal

from sqlalchemy import select
from app.models import DepositRequest, User, Transaction, RequestStatus, TxType


class TestAdminDepositsListRoute:
    """Tests for admin deposits list endpoint."""

    @pytest.mark.asyncio
    async def test_list_deposits(self, client, super_admin_headers, pending_deposit, db_session):
        """Test listing deposits."""
        response = await client.get("/admin/deposits", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["deposits"]) >= 1

    @pytest.mark.asyncio
    async def test_list_deposits_filter_by_status(self, client, super_admin_headers, pending_deposit, db_session):
        """Test filtering deposits by status."""
        response = await client.get(
            "/admin/deposits",
            params={"status": "pending"},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(d["status"] == "pending" for d in data["deposits"])

    @pytest.mark.asyncio
    async def test_list_deposits_filter_by_user(self, client, super_admin_headers, pending_deposit, user, db_session):
        """Test filtering deposits by user_id."""
        response = await client.get(
            "/admin/deposits",
            params={"user_id": user.id},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(d["user_id"] == user.id for d in data["deposits"])


class TestAdminDepositActionRoute:
    """Tests for admin deposit action endpoint."""

    @pytest.mark.asyncio
    async def test_approve_deposit(self, client, admin_headers, pending_deposit, user, db_session):
        """Test approving a deposit."""
        old_balance = user.balance_xpet

        response = await client.post(
            f"/admin/deposits/{pending_deposit.id}/action",
            headers=admin_headers,
            json={"action": "approve"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["new_status"] == "approved"

        # Verify deposit status updated
        await db_session.refresh(pending_deposit)
        assert pending_deposit.status == RequestStatus.APPROVED

        # Verify user balance updated
        await db_session.refresh(user)
        assert user.balance_xpet == old_balance + pending_deposit.amount

    @pytest.mark.asyncio
    async def test_approve_deposit_creates_transaction(self, client, admin_headers, pending_deposit, user, db_session):
        """Test approving deposit creates transaction."""
        response = await client.post(
            f"/admin/deposits/{pending_deposit.id}/action",
            headers=admin_headers,
            json={"action": "approve"}
        )

        assert response.status_code == 200

        # Verify transaction exists
        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.type == TxType.DEPOSIT
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet == pending_deposit.amount

    @pytest.mark.asyncio
    async def test_reject_deposit(self, client, admin_headers, pending_deposit, user, db_session):
        """Test rejecting a deposit."""
        old_balance = user.balance_xpet

        response = await client.post(
            f"/admin/deposits/{pending_deposit.id}/action",
            headers=admin_headers,
            json={"action": "reject", "note": "Invalid payment"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["new_status"] == "rejected"

        # Verify user balance unchanged
        await db_session.refresh(user)
        assert user.balance_xpet == old_balance

    @pytest.mark.asyncio
    async def test_cannot_approve_already_approved(self, client, admin_headers, pending_deposit, db_session):
        """Test cannot approve already approved deposit."""
        # First approve
        await client.post(
            f"/admin/deposits/{pending_deposit.id}/action",
            headers=admin_headers,
            json={"action": "approve"}
        )

        # Try to approve again
        response = await client.post(
            f"/admin/deposits/{pending_deposit.id}/action",
            headers=admin_headers,
            json={"action": "approve"}
        )

        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_moderator_cannot_approve_deposits(self, client, moderator_headers, pending_deposit, db_session):
        """Test moderator cannot approve deposits."""
        response = await client.post(
            f"/admin/deposits/{pending_deposit.id}/action",
            headers=moderator_headers,
            json={"action": "approve"}
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_deposit_not_found(self, client, admin_headers, db_session):
        """Test action on non-existent deposit."""
        response = await client.post(
            "/admin/deposits/99999/action",
            headers=admin_headers,
            json={"action": "approve"}
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
