"""Tests for admin withdrawal management."""
import pytest
from decimal import Decimal

from sqlalchemy import select
from app.models import WithdrawRequest, User, Transaction, RequestStatus, TxType


class TestAdminWithdrawalsListRoute:
    """Tests for admin withdrawals list endpoint."""

    @pytest.mark.asyncio
    async def test_list_withdrawals(self, client, super_admin_headers, pending_withdrawal, db_session):
        """Test listing withdrawals."""
        response = await client.get("/admin/withdrawals", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["withdrawals"]) >= 1

    @pytest.mark.asyncio
    async def test_list_withdrawals_filter_by_status(self, client, super_admin_headers, pending_withdrawal, db_session):
        """Test filtering withdrawals by status."""
        response = await client.get(
            "/admin/withdrawals",
            params={"status": "pending"},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(w["status"] == "pending" for w in data["withdrawals"])

    @pytest.mark.asyncio
    async def test_withdrawal_includes_net_amount(self, client, super_admin_headers, pending_withdrawal, db_session):
        """Test withdrawal response includes net amount."""
        response = await client.get("/admin/withdrawals", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        wd = data["withdrawals"][0]
        assert "net_amount" in wd
        assert Decimal(wd["net_amount"]) == Decimal(wd["amount"]) - Decimal(wd["fee"])


class TestAdminWithdrawalActionRoute:
    """Tests for admin withdrawal action endpoint."""

    @pytest.mark.asyncio
    async def test_complete_withdrawal(self, client, admin_headers, pending_withdrawal, db_session):
        """Test completing a withdrawal."""
        response = await client.post(
            f"/admin/withdrawals/{pending_withdrawal.id}/action",
            headers=admin_headers,
            json={"action": "complete", "tx_hash": "0xabc123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["new_status"] == "completed"

        # Verify status updated
        await db_session.refresh(pending_withdrawal)
        assert pending_withdrawal.status == RequestStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_reject_withdrawal_refunds_user(self, client, admin_headers, pending_withdrawal, user, db_session):
        """Test rejecting withdrawal refunds user."""
        old_balance = user.balance_xpet

        response = await client.post(
            f"/admin/withdrawals/{pending_withdrawal.id}/action",
            headers=admin_headers,
            json={"action": "reject", "note": "Suspicious activity"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["new_status"] == "rejected"

        # Verify user balance refunded (full amount including fee)
        await db_session.refresh(user)
        assert user.balance_xpet == old_balance + pending_withdrawal.amount

    @pytest.mark.asyncio
    async def test_reject_creates_refund_transaction(self, client, admin_headers, pending_withdrawal, user, db_session):
        """Test rejecting withdrawal creates refund transaction."""
        response = await client.post(
            f"/admin/withdrawals/{pending_withdrawal.id}/action",
            headers=admin_headers,
            json={"action": "reject", "note": "Test refund"}
        )

        assert response.status_code == 200

        # Verify refund transaction exists
        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.type == TxType.ADMIN_ADJUST
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet == pending_withdrawal.amount
        assert "rejected" in tx.meta.get("reason", "").lower()

    @pytest.mark.asyncio
    async def test_cannot_complete_already_completed(self, client, admin_headers, pending_withdrawal, db_session):
        """Test cannot complete already completed withdrawal."""
        # First complete
        await client.post(
            f"/admin/withdrawals/{pending_withdrawal.id}/action",
            headers=admin_headers,
            json={"action": "complete"}
        )

        # Try again
        response = await client.post(
            f"/admin/withdrawals/{pending_withdrawal.id}/action",
            headers=admin_headers,
            json={"action": "complete"}
        )

        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_moderator_cannot_process_withdrawals(self, client, moderator_headers, pending_withdrawal, db_session):
        """Test moderator cannot process withdrawals."""
        response = await client.post(
            f"/admin/withdrawals/{pending_withdrawal.id}/action",
            headers=moderator_headers,
            json={"action": "complete"}
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_withdrawal_not_found(self, client, admin_headers, db_session):
        """Test action on non-existent withdrawal."""
        response = await client.post(
            "/admin/withdrawals/99999/action",
            headers=admin_headers,
            json={"action": "complete"}
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
