"""
Tests for boost system: Snacks, ROI Boosts, Auto-Claim.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    User, UserPet, PetType, Transaction, PetSnack, PetRoiBoost,
    AutoClaimSubscription, BoostTransaction,
    PetStatus, PetLevel, TxType, SnackType, BoostType
)
from app.services.boosts import (
    calculate_snack_price,
    buy_snack,
    get_active_snack,
    calculate_roi_boost_price,
    buy_roi_boost,
    get_pet_total_roi_boost,
    buy_auto_claim,
    get_active_auto_claim,
    get_auto_claim_status,
    get_user_boost_stats,
    SNACK_CONFIG,
    ROI_BOOST_COST_COEFFICIENT,
    AUTO_CLAIM_MONTHLY_COST,
    AUTO_CLAIM_COMMISSION_PERCENT,
)
from app.services.pets import claim_profit


class TestSnackCalculations:
    """Tests for snack price calculations."""

    @pytest.mark.asyncio
    async def test_calculate_snack_price_cookie(self, db_session, user, pet_types):
        """Test cookie snack price calculation."""
        # Create pet
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[2].id,  # Glitch Cat: 100$, 1.5% daily
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()

        # Load pet type
        result = await db_session.execute(
            select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == pet.id)
        )
        pet = result.scalar_one()

        cost, bonus_percent = calculate_snack_price(pet, SnackType.COOKIE)

        # Daily profit = 100 * 0.015 = 1.5
        # Bonus = 1.5 * 0.10 = 0.15
        # Cost = 0.15 * 0.60 = 0.09
        assert bonus_percent == Decimal("0.10")
        assert cost == Decimal("0.09")

    @pytest.mark.asyncio
    async def test_calculate_snack_price_cake(self, db_session, user, pet_types):
        """Test cake snack price calculation."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()

        result = await db_session.execute(
            select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == pet.id)
        )
        pet = result.scalar_one()

        cost, bonus_percent = calculate_snack_price(pet, SnackType.CAKE)

        # Bonus = 1.5 * 0.50 = 0.75
        # Cost = 0.75 * 0.50 = 0.375
        assert bonus_percent == Decimal("0.50")
        assert cost == Decimal("0.375")

    @pytest.mark.asyncio
    async def test_snack_minimum_cost(self, db_session, user, pet_types):
        """Test minimum snack cost of 0.01 XPET."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,  # Bubble Slime: 5$, 1% daily
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()

        result = await db_session.execute(
            select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == pet.id)
        )
        pet = result.scalar_one()

        cost, bonus_percent = calculate_snack_price(pet, SnackType.COOKIE)

        # Daily profit = 5 * 0.01 = 0.05
        # Bonus = 0.05 * 0.10 = 0.005
        # Cost = 0.005 * 0.60 = 0.003, but min is 0.01
        assert cost == Decimal("0.01")


class TestBuySnack:
    """Tests for buying snacks."""

    @pytest.mark.asyncio
    async def test_buy_snack_success(self, db_session, rich_user, pet_types):
        """Test successful snack purchase."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        initial_balance = rich_user.balance_xpet
        snack, new_balance = await buy_snack(db_session, rich_user, pet.id, SnackType.COOKIE)

        assert snack.pet_id == pet.id
        assert snack.user_id == rich_user.id
        assert snack.snack_type == SnackType.COOKIE
        assert snack.bonus_percent == Decimal("0.10")
        assert snack.is_used is False
        assert new_balance < initial_balance

    @pytest.mark.asyncio
    async def test_buy_snack_creates_transactions(self, db_session, rich_user, pet_types):
        """Test snack purchase creates transactions."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        await buy_snack(db_session, rich_user, pet.id, SnackType.STEAK)

        # Check main transaction
        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == rich_user.id,
                Transaction.type == TxType.BOOST_PURCHASE
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet < 0

        # Check boost transaction
        result = await db_session.execute(
            select(BoostTransaction).where(
                BoostTransaction.user_id == rich_user.id,
                BoostTransaction.boost_type == BoostType.SNACK
            )
        )
        boost_tx = result.scalar_one()
        assert boost_tx.pet_id == pet.id

    @pytest.mark.asyncio
    async def test_buy_snack_insufficient_balance(self, db_session, user, pet_types):
        """Test buying snack with insufficient balance."""
        user.balance_xpet = Decimal("0.001")
        await db_session.commit()

        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="Insufficient balance"):
            await buy_snack(db_session, user, pet.id, SnackType.COOKIE)

    @pytest.mark.asyncio
    async def test_buy_snack_already_active(self, db_session, rich_user, pet_types):
        """Test cannot buy snack when one is already active."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Buy first snack
        await buy_snack(db_session, rich_user, pet.id, SnackType.COOKIE)

        # Try to buy another
        with pytest.raises(ValueError, match="already has an active snack"):
            await buy_snack(db_session, rich_user, pet.id, SnackType.STEAK)

    @pytest.mark.asyncio
    async def test_buy_snack_sold_pet(self, db_session, rich_user, pet_types):
        """Test cannot buy snack for sold pet."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.SOLD,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="Cannot boost"):
            await buy_snack(db_session, rich_user, pet.id, SnackType.COOKIE)


class TestSnackWithClaim:
    """Tests for snack integration with claim."""

    @pytest.mark.asyncio
    async def test_claim_with_snack_bonus(self, db_session, rich_user, pet_types):
        """Test claim applies snack bonus."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,  # 100$, 1.5%
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("0"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Buy snack first
        await buy_snack(db_session, rich_user, pet.id, SnackType.CAKE)  # +50%

        initial_balance = rich_user.balance_xpet
        result = await claim_profit(db_session, rich_user, pet.id)

        # Base profit = 1.5, Cake bonus = 0.75, Total = 2.25
        assert result["base_profit"] == Decimal("1.5")
        assert result["snack_bonus"] == Decimal("0.75")
        assert result["profit_claimed"] == Decimal("2.25")
        assert result["snack_used"] == "cake"

        # Snack should be marked as used
        snack = await get_active_snack(db_session, pet.id)
        assert snack is None  # No active snack anymore

    @pytest.mark.asyncio
    async def test_claim_without_snack(self, db_session, rich_user, pet_types):
        """Test claim without snack has no bonus."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("0"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        result = await claim_profit(db_session, rich_user, pet.id)

        assert result["base_profit"] == Decimal("1.5")
        assert result["snack_bonus"] == Decimal("0")
        assert result["profit_claimed"] == Decimal("1.5")
        assert result["snack_used"] is None


class TestRoiBoostCalculations:
    """Tests for ROI boost calculations."""

    @pytest.mark.asyncio
    async def test_calculate_roi_boost_price(self, db_session, user, pet_types):
        """Test ROI boost price calculation."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[2].id,  # 100$
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()

        result = await db_session.execute(
            select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == pet.id)
        )
        pet = result.scalar_one()

        cost, extra_profit = calculate_roi_boost_price(pet, Decimal("0.10"))

        # Extra profit = 100 * 0.10 = 10
        # Cost = 10 * 0.25 = 2.5
        assert extra_profit == Decimal("10")
        assert cost == Decimal("2.5")


class TestBuyRoiBoost:
    """Tests for buying ROI boosts."""

    @pytest.mark.asyncio
    async def test_buy_roi_boost_success(self, db_session, rich_user, pet_types):
        """Test successful ROI boost purchase."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        initial_balance = rich_user.balance_xpet
        boost, new_balance = await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.10"))

        assert boost.pet_id == pet.id
        assert boost.boost_percent == Decimal("0.10")
        assert boost.extra_profit == Decimal("10")
        assert new_balance == initial_balance - Decimal("2.5")

    @pytest.mark.asyncio
    async def test_buy_multiple_roi_boosts(self, db_session, rich_user, pet_types):
        """Test buying multiple ROI boosts on same pet."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Buy two boosts
        await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.10"))
        await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.15"))

        total_boost = await get_pet_total_roi_boost(db_session, pet.id)
        assert total_boost == Decimal("0.25")

    @pytest.mark.asyncio
    async def test_roi_boost_max_exceeded(self, db_session, rich_user, pet_types):
        """Test cannot exceed 50% total ROI boost."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Buy 40%
        await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.20"))
        await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.20"))

        # Try to buy another 20% (would exceed 50%)
        with pytest.raises(ValueError, match="Maximum ROI boost"):
            await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.20"))

    @pytest.mark.asyncio
    async def test_invalid_boost_percent(self, db_session, rich_user, pet_types):
        """Test invalid boost percentage."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="Invalid boost percentage"):
            await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.07"))  # Not 5/10/15/20


class TestRoiBoostWithClaim:
    """Tests for ROI boost integration with claim."""

    @pytest.mark.asyncio
    async def test_claim_with_roi_boost(self, db_session, rich_user, pet_types):
        """Test claim respects boosted ROI cap."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,  # 100$, 170% ROI cap
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("0"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Buy +10% ROI boost
        await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.10"))

        result = await claim_profit(db_session, rich_user, pet.id)

        # Original max_profit = 100 * 1.7 = 170
        # With boost: 100 * 1.8 = 180
        assert result["max_profit"] == Decimal("180")
        assert result["roi_boost_percent"] == Decimal("10")


class TestAutoClaimSubscription:
    """Tests for auto-claim subscription."""

    @pytest.mark.asyncio
    async def test_buy_auto_claim_success(self, db_session, rich_user):
        """Test successful auto-claim purchase."""
        initial_balance = rich_user.balance_xpet
        subscription, new_balance = await buy_auto_claim(db_session, rich_user, months=1)

        assert subscription.user_id == rich_user.id
        assert subscription.cost_xpet == AUTO_CLAIM_MONTHLY_COST
        assert subscription.commission_percent == AUTO_CLAIM_COMMISSION_PERCENT
        assert subscription.is_active is True
        assert new_balance == initial_balance - AUTO_CLAIM_MONTHLY_COST

        # Check expiry is ~30 days
        days_until_expiry = (subscription.expires_at - datetime.utcnow()).days
        assert 29 <= days_until_expiry <= 30

    @pytest.mark.asyncio
    async def test_buy_auto_claim_3_months(self, db_session, rich_user):
        """Test 3-month auto-claim purchase."""
        subscription, _ = await buy_auto_claim(db_session, rich_user, months=3)

        assert subscription.cost_xpet == AUTO_CLAIM_MONTHLY_COST * 3
        days_until_expiry = (subscription.expires_at - datetime.utcnow()).days
        assert 88 <= days_until_expiry <= 90

    @pytest.mark.asyncio
    async def test_buy_auto_claim_already_active(self, db_session, rich_user):
        """Test cannot buy when subscription already active."""
        await buy_auto_claim(db_session, rich_user, months=1)

        with pytest.raises(ValueError, match="already active"):
            await buy_auto_claim(db_session, rich_user, months=1)

    @pytest.mark.asyncio
    async def test_buy_auto_claim_invalid_period(self, db_session, rich_user):
        """Test invalid subscription period."""
        with pytest.raises(ValueError, match="Invalid subscription period"):
            await buy_auto_claim(db_session, rich_user, months=2)

    @pytest.mark.asyncio
    async def test_get_auto_claim_status_inactive(self, db_session, user):
        """Test status when no subscription."""
        status = await get_auto_claim_status(db_session, user.id)

        assert status["is_active"] is False
        assert status["monthly_cost"] == AUTO_CLAIM_MONTHLY_COST

    @pytest.mark.asyncio
    async def test_get_auto_claim_status_active(self, db_session, rich_user):
        """Test status when subscription active."""
        await buy_auto_claim(db_session, rich_user, months=1)

        status = await get_auto_claim_status(db_session, rich_user.id)

        assert status["is_active"] is True
        assert status["days_remaining"] >= 29
        assert status["total_claims"] == 0


class TestAutoClaimWithClaim:
    """Tests for auto-claim commission during claim."""

    @pytest.mark.asyncio
    async def test_auto_claim_commission(self, db_session, rich_user, pet_types):
        """Test auto-claim takes 3% commission."""
        # Buy auto-claim subscription
        await buy_auto_claim(db_session, rich_user, months=1)

        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,  # 100$, 1.5% daily
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("0"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        result = await claim_profit(db_session, rich_user, pet.id, is_auto_claim=True)

        # Base profit = 1.5
        # Commission = 1.5 * 0.03 = 0.045
        # Received = 1.5 - 0.045 = 1.455
        assert result["auto_claim_commission"] == Decimal("0.045")
        assert result["profit_claimed"] == Decimal("1.455")

    @pytest.mark.asyncio
    async def test_manual_claim_no_commission(self, db_session, rich_user, pet_types):
        """Test manual claim has no commission even with subscription."""
        await buy_auto_claim(db_session, rich_user, months=1)

        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("0"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        result = await claim_profit(db_session, rich_user, pet.id, is_auto_claim=False)

        assert result["auto_claim_commission"] == Decimal("0")
        assert result["profit_claimed"] == Decimal("1.5")


class TestBoostStats:
    """Tests for boost statistics."""

    @pytest.mark.asyncio
    async def test_get_user_boost_stats(self, db_session, rich_user, pet_types):
        """Test getting user boost stats."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Buy various boosts
        await buy_snack(db_session, rich_user, pet.id, SnackType.COOKIE)
        await buy_roi_boost(db_session, rich_user, pet.id, Decimal("0.10"))
        await buy_auto_claim(db_session, rich_user, months=1)

        stats = await get_user_boost_stats(db_session, rich_user.id)

        assert stats["snacks_purchased"] == 1
        assert stats["roi_boosts_purchased"] == 1
        assert stats["auto_claim_subscriptions"] == 1
        assert stats["total_spent"] > 0


class TestBoostRoutes:
    """Tests for boost API routes."""

    @pytest.mark.asyncio
    async def test_get_snack_prices(self, client, user, auth_headers, pet_types, db_session):
        """Test getting snack prices via API."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        response = await client.get(f"/boosts/snacks/prices/{pet.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "cookie" in data["prices"]
        assert "steak" in data["prices"]
        assert "cake" in data["prices"]
        assert float(data["daily_profit"]) == 1.5

    @pytest.mark.asyncio
    async def test_buy_snack_route(self, client, rich_user, rich_auth_headers, pet_types, db_session):
        """Test buying snack via API."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        response = await client.post(
            "/boosts/snacks/buy",
            headers=rich_auth_headers,
            json={"pet_id": pet.id, "snack_type": "cookie"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["snack_type"] == "cookie"
        assert "bonus_percent" in data

    @pytest.mark.asyncio
    async def test_get_roi_boost_prices(self, client, user, auth_headers, pet_types, db_session):
        """Test getting ROI boost prices via API."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        response = await client.get(f"/boosts/roi/prices/{pet.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["current_boost"] == "0"
        assert data["max_boost"] == "50"
        assert "+5%" in data["options"]

    @pytest.mark.asyncio
    async def test_buy_roi_boost_route(self, client, rich_user, rich_auth_headers, pet_types, db_session):
        """Test buying ROI boost via API."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[2].id,
            invested_total=Decimal("100"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        response = await client.post(
            "/boosts/roi/buy",
            headers=rich_auth_headers,
            json={"pet_id": pet.id, "boost_percent": "0.10"}
        )
        assert response.status_code == 200
        data = response.json()

        assert float(data["boost_percent"]) == 10
        assert float(data["total_boost"]) == 10

    @pytest.mark.asyncio
    async def test_get_auto_claim_status_route(self, client, user, auth_headers):
        """Test getting auto-claim status via API."""
        response = await client.get("/boosts/auto-claim/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_buy_auto_claim_route(self, client, rich_user, rich_auth_headers):
        """Test buying auto-claim via API."""
        response = await client.post(
            "/boosts/auto-claim/buy",
            headers=rich_auth_headers,
            json={"months": 1}
        )
        assert response.status_code == 200
        data = response.json()

        assert "subscription_id" in data
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_get_boost_stats_route(self, client, user, auth_headers):
        """Test getting boost stats via API."""
        response = await client.get("/boosts/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "total_spent" in data
        assert "snacks_purchased" in data
