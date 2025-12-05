"""
Tests for wallet service and routes.
"""
import pytest
from decimal import Decimal

from sqlalchemy import select

from app.models import User, Transaction, DepositRequest, WithdrawRequest, TxType, NetworkType, RequestStatus
from app.services.wallet import (
    calculate_withdraw_fee,
    get_wallet_info,
    create_deposit_request,
    create_withdraw_request,
    get_transactions,
    WITHDRAW_MIN,
    WITHDRAW_FEE_FIXED,
    WITHDRAW_FEE_PERCENT,
    DEPOSIT_ADDRESSES,
)


class TestWalletServiceCalculations:
    """Tests for wallet calculation functions."""

    def test_calculate_withdraw_fee_minimum(self):
        """Test withdraw fee for minimum amount."""
        amount = WITHDRAW_MIN  # $5
        fee = calculate_withdraw_fee(amount)
        # $1 fixed + 2% of $5 = $1 + $0.10 = $1.10
        expected = WITHDRAW_FEE_FIXED + (amount * WITHDRAW_FEE_PERCENT)
        assert fee == expected

    def test_calculate_withdraw_fee_larger_amount(self):
        """Test withdraw fee for larger amount."""
        amount = Decimal("100")
        fee = calculate_withdraw_fee(amount)
        # $1 fixed + 2% of $100 = $1 + $2 = $3
        expected = Decimal("1") + Decimal("2")
        assert fee == expected

    def test_calculate_withdraw_fee_formula(self):
        """Test withdraw fee formula is correct."""
        amounts = [Decimal("10"), Decimal("50"), Decimal("1000")]
        for amount in amounts:
            fee = calculate_withdraw_fee(amount)
            expected = WITHDRAW_FEE_FIXED + (amount * WITHDRAW_FEE_PERCENT)
            assert fee == expected


class TestWalletServiceDatabase:
    """Tests for wallet service database operations."""

    @pytest.mark.asyncio
    async def test_get_wallet_info_no_pending(self, db_session, user):
        """Test wallet info with no pending requests."""
        info = await get_wallet_info(db_session, user.id, user.balance_xpet)

        assert info["balance_xpet"] == user.balance_xpet
        assert info["balance_usd"] == user.balance_xpet  # 1:1 ratio
        assert info["pending_deposits"] == 0
        assert info["pending_withdrawals"] == 0

    @pytest.mark.asyncio
    async def test_get_wallet_info_with_pending_deposits(self, db_session, user):
        """Test wallet info counts pending deposits."""
        # Create pending deposits
        for i in range(3):
            deposit = DepositRequest(
                user_id=user.id,
                amount=Decimal("10"),
                network=NetworkType.BEP20,
                status=RequestStatus.PENDING,
            )
            db_session.add(deposit)
        await db_session.commit()

        info = await get_wallet_info(db_session, user.id, user.balance_xpet)
        assert info["pending_deposits"] == 3

    @pytest.mark.asyncio
    async def test_get_wallet_info_with_pending_withdrawals(self, db_session, user):
        """Test wallet info counts pending withdrawals."""
        # Create pending withdrawals
        for i in range(2):
            withdrawal = WithdrawRequest(
                user_id=user.id,
                amount=Decimal("10"),
                fee=Decimal("1.2"),
                network=NetworkType.SOLANA,
                wallet_address="test_address",
                status=RequestStatus.PENDING,
            )
            db_session.add(withdrawal)
        await db_session.commit()

        info = await get_wallet_info(db_session, user.id, user.balance_xpet)
        assert info["pending_withdrawals"] == 2

    @pytest.mark.asyncio
    async def test_get_wallet_info_excludes_non_pending(self, db_session, user):
        """Test wallet info excludes non-pending requests."""
        # Create completed deposit
        deposit = DepositRequest(
            user_id=user.id,
            amount=Decimal("10"),
            network=NetworkType.BEP20,
            status=RequestStatus.COMPLETED,
        )
        db_session.add(deposit)

        # Create rejected withdrawal
        withdrawal = WithdrawRequest(
            user_id=user.id,
            amount=Decimal("10"),
            fee=Decimal("1.2"),
            network=NetworkType.SOLANA,
            wallet_address="test_address",
            status=RequestStatus.REJECTED,
        )
        db_session.add(withdrawal)
        await db_session.commit()

        info = await get_wallet_info(db_session, user.id, user.balance_xpet)
        assert info["pending_deposits"] == 0
        assert info["pending_withdrawals"] == 0


class TestDepositRequest:
    """Tests for deposit request creation."""

    @pytest.mark.asyncio
    async def test_create_deposit_request_bep20(self, db_session, user):
        """Test creating BEP20 deposit request."""
        deposit = await create_deposit_request(
            db_session, user, Decimal("50"), NetworkType.BEP20
        )

        assert deposit.user_id == user.id
        assert deposit.amount == Decimal("50")
        assert deposit.network == NetworkType.BEP20
        assert deposit.deposit_address == DEPOSIT_ADDRESSES[NetworkType.BEP20]
        assert deposit.status == RequestStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_deposit_request_solana(self, db_session, user):
        """Test creating Solana deposit request."""
        deposit = await create_deposit_request(
            db_session, user, Decimal("100"), NetworkType.SOLANA
        )

        assert deposit.network == NetworkType.SOLANA
        assert deposit.deposit_address == DEPOSIT_ADDRESSES[NetworkType.SOLANA]

    @pytest.mark.asyncio
    async def test_create_deposit_request_ton(self, db_session, user):
        """Test creating TON deposit request."""
        deposit = await create_deposit_request(
            db_session, user, Decimal("25"), NetworkType.TON
        )

        assert deposit.network == NetworkType.TON
        assert deposit.deposit_address == DEPOSIT_ADDRESSES[NetworkType.TON]


class TestWithdrawRequest:
    """Tests for withdrawal request creation."""

    @pytest.mark.asyncio
    async def test_create_withdraw_request_success(self, db_session, rich_user):
        """Test successful withdrawal request."""
        amount = Decimal("50")
        wallet_address = "0xtest123456789"
        initial_balance = rich_user.balance_xpet

        request, new_balance = await create_withdraw_request(
            db_session, rich_user, amount, NetworkType.BEP20, wallet_address
        )

        fee = calculate_withdraw_fee(amount)
        total_deducted = amount + fee

        assert request.user_id == rich_user.id
        assert request.amount == amount
        assert request.fee == fee
        assert request.network == NetworkType.BEP20
        assert request.wallet_address == wallet_address
        assert request.status == RequestStatus.PENDING
        assert new_balance == initial_balance - total_deducted

    @pytest.mark.asyncio
    async def test_create_withdraw_request_creates_transaction(self, db_session, rich_user):
        """Test withdrawal creates transaction."""
        amount = Decimal("50")

        await create_withdraw_request(
            db_session, rich_user, amount, NetworkType.BEP20, "0xtest"
        )

        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == rich_user.id,
                Transaction.type == TxType.WITHDRAW
            )
        )
        tx = result.scalar_one()
        fee = calculate_withdraw_fee(amount)
        assert tx.amount_xpet == -(amount + fee)
        assert tx.fee == fee

    @pytest.mark.asyncio
    async def test_create_withdraw_request_below_minimum(self, db_session, rich_user):
        """Test withdrawal below minimum fails."""
        amount = Decimal("1")  # Below $5 minimum

        with pytest.raises(ValueError, match="Minimum withdrawal"):
            await create_withdraw_request(
                db_session, rich_user, amount, NetworkType.BEP20, "0xtest"
            )

    @pytest.mark.asyncio
    async def test_create_withdraw_request_insufficient_balance(self, db_session, user):
        """Test withdrawal with insufficient balance fails."""
        # User has 100, try to withdraw more
        amount = Decimal("100")  # Plus fee will exceed balance

        with pytest.raises(ValueError, match="Insufficient balance"):
            await create_withdraw_request(
                db_session, user, amount, NetworkType.BEP20, "0xtest"
            )


class TestGetTransactions:
    """Tests for transaction retrieval."""

    @pytest.mark.asyncio
    async def test_get_transactions_empty(self, db_session, user):
        """Test getting transactions when none exist."""
        txs, total = await get_transactions(db_session, user.id)
        assert txs == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_transactions_with_data(self, db_session, user, transactions):
        """Test getting transactions with data."""
        txs, total = await get_transactions(db_session, user.id)
        assert len(txs) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_get_transactions_pagination(self, db_session, user, transactions):
        """Test transaction pagination."""
        # Get first page with limit 2
        txs, total = await get_transactions(db_session, user.id, page=1, limit=2)
        assert len(txs) == 2
        assert total == 3

        # Get second page
        txs, total = await get_transactions(db_session, user.id, page=2, limit=2)
        assert len(txs) == 1

    @pytest.mark.asyncio
    async def test_get_transactions_filter_by_type(self, db_session, user, transactions):
        """Test filtering transactions by type."""
        txs, total = await get_transactions(db_session, user.id, tx_type=TxType.DEPOSIT)
        assert len(txs) == 1
        assert all(tx.type == TxType.DEPOSIT for tx in txs)

    @pytest.mark.asyncio
    async def test_get_transactions_ordered_by_date(self, db_session, user, transactions):
        """Test transactions are ordered by date descending."""
        txs, total = await get_transactions(db_session, user.id)
        dates = [tx.created_at for tx in txs]
        assert dates == sorted(dates, reverse=True)


class TestWalletRoutes:
    """Tests for wallet API routes."""

    @pytest.mark.asyncio
    async def test_get_wallet(self, client, user, auth_headers):
        """Test getting wallet info."""
        response = await client.get("/wallet", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "balance_xpet" in data
        assert "balance_usd" in data
        assert "pending_deposits" in data
        assert "pending_withdrawals" in data

    @pytest.mark.asyncio
    async def test_create_deposit_route(self, client, user, auth_headers):
        """Test creating deposit request via API."""
        response = await client.post(
            "/wallet/deposit-request",
            headers=auth_headers,
            json={"amount": "50", "network": "BEP-20"}
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["amount"]) == Decimal("50")
        assert data["network"] == "BEP-20"
        assert "deposit_address" in data
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_deposit_solana(self, client, user, auth_headers):
        """Test creating Solana deposit via API."""
        response = await client.post(
            "/wallet/deposit-request",
            headers=auth_headers,
            json={"amount": "100", "network": "Solana"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["network"] == "Solana"

    @pytest.mark.asyncio
    async def test_create_withdraw_route(self, client, rich_user, rich_auth_headers):
        """Test creating withdrawal request via API."""
        response = await client.post(
            "/wallet/withdraw-request",
            headers=rich_auth_headers,
            json={
                "amount": "50",
                "network": "BEP-20",
                "wallet_address": "0x1234567890abcdef"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "fee" in data
        assert "total_deducted" in data
        assert "new_balance" in data

    @pytest.mark.asyncio
    async def test_create_withdraw_below_minimum(self, client, rich_user, rich_auth_headers):
        """Test withdrawal below minimum via API."""
        response = await client.post(
            "/wallet/withdraw-request",
            headers=rich_auth_headers,
            json={
                "amount": "1",
                "network": "BEP-20",
                "wallet_address": "0x1234567890abcdef"
            }
        )
        assert response.status_code == 400
        assert "Minimum" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_transactions_route(self, client, user, auth_headers, transactions):
        """Test getting transactions via API."""
        response = await client.get("/wallet/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data

    @pytest.mark.asyncio
    async def test_get_transactions_pagination(self, client, user, auth_headers, transactions):
        """Test transaction pagination via API."""
        response = await client.get(
            "/wallet/transactions?page=1&limit=2",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 2
        assert data["total"] == 3
        assert data["pages"] == 2

    @pytest.mark.asyncio
    async def test_get_transactions_filter(self, client, user, auth_headers, transactions):
        """Test transaction filter via API."""
        response = await client.get(
            "/wallet/transactions?type=deposit",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(tx["type"] == "deposit" for tx in data["transactions"])

    @pytest.mark.asyncio
    async def test_wallet_unauthorized(self, client):
        """Test wallet routes require auth."""
        response = await client.get("/wallet")
        assert response.status_code == 401
