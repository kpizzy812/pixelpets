"""
Tests for pets service and routes.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User, UserPet, PetType, Transaction, PetStatus, PetLevel, TxType
from app.services.pets import (
    get_next_level,
    calculate_max_profit,
    calculate_daily_profit,
    calculate_upgrade_cost,
    calculate_sell_fee,
    calculate_sell_refund,
    get_pet_catalog,
    get_user_pets,
    get_free_slot,
    buy_pet,
    upgrade_pet,
    sell_pet,
    start_training,
    check_training_status,
    claim_profit,
    get_hall_of_fame,
    MAX_SLOTS,
    SELL_BASE_FEE,
    SELL_MAX_FEE,
    TRAINING_DURATION_HOURS,
)


class TestPetServiceCalculations:
    """Tests for pet calculation functions."""

    def test_get_next_level_from_baby(self):
        """Test getting next level from BABY."""
        assert get_next_level(PetLevel.BABY) == PetLevel.ADULT

    def test_get_next_level_from_adult(self):
        """Test getting next level from ADULT."""
        assert get_next_level(PetLevel.ADULT) == PetLevel.MYTHIC

    def test_get_next_level_from_mythic(self):
        """Test getting next level from MYTHIC returns None."""
        assert get_next_level(PetLevel.MYTHIC) is None

    def test_calculate_max_profit(self):
        """Test max profit calculation."""
        invested = Decimal("100")
        roi_cap = Decimal("1.5")  # 150%
        expected = Decimal("150")  # 100 * 1.5
        assert calculate_max_profit(invested, roi_cap) == expected

    def test_calculate_daily_profit(self):
        """Test daily profit calculation."""
        invested = Decimal("100")
        daily_rate = Decimal("0.01")  # 1%
        expected = Decimal("1")  # 100 * 0.01
        assert calculate_daily_profit(invested, daily_rate) == expected

    def test_calculate_upgrade_cost_baby_to_adult(self):
        """Test upgrade cost from BABY to ADULT."""
        level_prices = {"BABY": 5, "ADULT": 20, "MYTHIC": 50}
        invested = Decimal("5")  # Current invested at BABY level
        cost = calculate_upgrade_cost(level_prices, PetLevel.ADULT, invested)
        assert cost == Decimal("15")  # 20 - 5

    def test_calculate_upgrade_cost_adult_to_mythic(self):
        """Test upgrade cost from ADULT to MYTHIC."""
        level_prices = {"BABY": 5, "ADULT": 20, "MYTHIC": 50}
        invested = Decimal("20")  # Current invested at ADULT level
        cost = calculate_upgrade_cost(level_prices, PetLevel.MYTHIC, invested)
        assert cost == Decimal("30")  # 50 - 20

    def test_calculate_upgrade_cost_already_at_level(self):
        """Test upgrade cost when already invested more."""
        level_prices = {"BABY": 5, "ADULT": 20, "MYTHIC": 50}
        invested = Decimal("25")  # More than ADULT price
        cost = calculate_upgrade_cost(level_prices, PetLevel.ADULT, invested)
        assert cost == Decimal("0")  # max(0, 20 - 25)


class TestPetServiceDatabase:
    """Tests for pet service database operations."""

    @pytest.mark.asyncio
    async def test_get_pet_catalog(self, db_session, pet_types):
        """Test getting active pet types."""
        catalog = await get_pet_catalog(db_session)
        # Should only include active pets (3 out of 4)
        assert len(catalog) == 3
        assert all(pt.is_active for pt in catalog)

    @pytest.mark.asyncio
    async def test_get_pet_catalog_ordered_by_price(self, db_session, pet_types):
        """Test catalog is ordered by base price."""
        catalog = await get_pet_catalog(db_session)
        prices = [pt.base_price for pt in catalog]
        assert prices == sorted(prices)

    @pytest.mark.asyncio
    async def test_get_user_pets_empty(self, db_session, user):
        """Test getting pets for user with no pets."""
        pets = await get_user_pets(db_session, user.id)
        assert pets == []

    @pytest.mark.asyncio
    async def test_get_user_pets_with_pets(self, db_session, user, user_pet):
        """Test getting pets for user with pets."""
        pets = await get_user_pets(db_session, user.id)
        assert len(pets) == 1
        assert pets[0].id == user_pet.id

    @pytest.mark.asyncio
    async def test_get_user_pets_excludes_sold(self, db_session, user, pet_types):
        """Test sold pets are excluded."""
        # Create a sold pet
        sold_pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.SOLD,
            slot_index=0,
        )
        db_session.add(sold_pet)
        await db_session.commit()

        pets = await get_user_pets(db_session, user.id)
        assert len(pets) == 0

    @pytest.mark.asyncio
    async def test_get_free_slot_empty(self, db_session, user):
        """Test free slot when no pets."""
        slot = await get_free_slot(db_session, user.id)
        assert slot == 0

    @pytest.mark.asyncio
    async def test_get_free_slot_one_pet(self, db_session, user, user_pet):
        """Test free slot with one pet."""
        slot = await get_free_slot(db_session, user.id)
        assert slot == 1  # Slot 0 is taken

    @pytest.mark.asyncio
    async def test_get_free_slot_all_occupied(self, db_session, user, pet_types):
        """Test no free slot when all occupied."""
        for i in range(MAX_SLOTS):
            pet = UserPet(
                user_id=user.id,
                pet_type_id=pet_types[0].id,
                invested_total=Decimal("5"),
                level=PetLevel.BABY,
                status=PetStatus.OWNED_IDLE,
                slot_index=i,
            )
            db_session.add(pet)
        await db_session.commit()

        slot = await get_free_slot(db_session, user.id)
        assert slot is None


class TestBuyPet:
    """Tests for buying pets."""

    @pytest.mark.asyncio
    async def test_buy_pet_success(self, db_session, rich_user, pet_types):
        """Test successful pet purchase."""
        initial_balance = rich_user.balance_xpet
        pet_type = pet_types[0]  # Bubble Slime, price 5

        pet, new_balance = await buy_pet(db_session, rich_user, pet_type.id)

        assert pet is not None
        assert pet.user_id == rich_user.id
        assert pet.pet_type_id == pet_type.id
        assert pet.invested_total == pet_type.base_price
        assert pet.level == PetLevel.BABY
        assert pet.status == PetStatus.OWNED_IDLE
        assert new_balance == initial_balance - pet_type.base_price

    @pytest.mark.asyncio
    async def test_buy_pet_creates_transaction(self, db_session, rich_user, pet_types):
        """Test pet purchase creates transaction."""
        pet_type = pet_types[0]
        await buy_pet(db_session, rich_user, pet_type.id)

        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == rich_user.id,
                Transaction.type == TxType.PET_BUY
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet == -pet_type.base_price

    @pytest.mark.asyncio
    async def test_buy_pet_insufficient_balance(self, db_session, user, pet_types):
        """Test buying pet with insufficient balance."""
        user.balance_xpet = Decimal("1")  # Less than cheapest pet
        await db_session.commit()

        with pytest.raises(ValueError, match="Insufficient balance"):
            await buy_pet(db_session, user, pet_types[0].id)

    @pytest.mark.asyncio
    async def test_buy_pet_type_not_found(self, db_session, rich_user):
        """Test buying non-existent pet type."""
        with pytest.raises(ValueError, match="Pet type not found"):
            await buy_pet(db_session, rich_user, 99999)

    @pytest.mark.asyncio
    async def test_buy_pet_inactive_type(self, db_session, rich_user, pet_types):
        """Test buying inactive pet type."""
        inactive_type = pet_types[3]  # The inactive one
        with pytest.raises(ValueError, match="not available"):
            await buy_pet(db_session, rich_user, inactive_type.id)

    @pytest.mark.asyncio
    async def test_buy_pet_no_slots(self, db_session, rich_user, pet_types):
        """Test buying pet when all slots full."""
        # Fill all slots
        for i in range(MAX_SLOTS):
            pet = UserPet(
                user_id=rich_user.id,
                pet_type_id=pet_types[0].id,
                invested_total=Decimal("5"),
                level=PetLevel.BABY,
                status=PetStatus.OWNED_IDLE,
                slot_index=i,
            )
            db_session.add(pet)
        await db_session.commit()

        with pytest.raises(ValueError, match="No free slots"):
            await buy_pet(db_session, rich_user, pet_types[0].id)


class TestUpgradePet:
    """Tests for upgrading pets."""

    @pytest.mark.asyncio
    async def test_upgrade_pet_success(self, db_session, rich_user, pet_types):
        """Test successful pet upgrade."""
        # Create a pet for rich user
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        initial_balance = rich_user.balance_xpet
        upgraded_pet, new_balance = await upgrade_pet(db_session, rich_user, pet.id)

        assert upgraded_pet.level == PetLevel.ADULT
        assert upgraded_pet.invested_total == Decimal("20")  # ADULT price
        assert new_balance == initial_balance - Decimal("15")  # 20 - 5

    @pytest.mark.asyncio
    async def test_upgrade_pet_creates_transaction(self, db_session, rich_user, pet_types):
        """Test upgrade creates transaction."""
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        await upgrade_pet(db_session, rich_user, pet.id)

        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == rich_user.id,
                Transaction.type == TxType.PET_UPGRADE
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet == Decimal("-15")

    @pytest.mark.asyncio
    async def test_upgrade_pet_not_found(self, db_session, rich_user):
        """Test upgrading non-existent pet."""
        with pytest.raises(ValueError, match="Pet not found"):
            await upgrade_pet(db_session, rich_user, 99999)

    @pytest.mark.asyncio
    async def test_upgrade_pet_sold(self, db_session, user, pet_types):
        """Test cannot upgrade sold pet."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.SOLD,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="sold"):
            await upgrade_pet(db_session, user, pet.id)

    @pytest.mark.asyncio
    async def test_upgrade_pet_evolved(self, db_session, user, pet_types):
        """Test cannot upgrade evolved pet."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.EVOLVED,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="evolved"):
            await upgrade_pet(db_session, user, pet.id)

    @pytest.mark.asyncio
    async def test_upgrade_pet_max_level(self, db_session, user, pet_types):
        """Test cannot upgrade MYTHIC pet."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("50"),
            level=PetLevel.MYTHIC,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="max level"):
            await upgrade_pet(db_session, user, pet.id)


class TestSellPet:
    """Tests for selling pets."""

    @pytest.mark.asyncio
    async def test_sell_pet_success_no_profit(self, db_session, user, user_pet):
        """Test successful pet sale with no profit claimed (15% fee)."""
        initial_balance = user.balance_xpet
        invested = user_pet.invested_total

        refund, fee_percent, new_balance = await sell_pet(db_session, user, user_pet.id)

        # With no profit claimed, fee should be base 15%
        expected_refund = invested * (Decimal("1") - SELL_BASE_FEE)
        assert fee_percent == SELL_BASE_FEE
        assert refund == expected_refund
        assert new_balance == initial_balance + expected_refund

        # Verify pet is now SOLD
        await db_session.refresh(user_pet)
        assert user_pet.status == PetStatus.SOLD

    @pytest.mark.asyncio
    async def test_sell_pet_progressive_fee(self, db_session, user, pet_types):
        """Test progressive sell fee based on profit claimed."""
        # Create pet with 50% profit claimed
        pet_type = pet_types[0]
        invested = Decimal("100")
        max_profit = invested * pet_type.roi_cap_multiplier  # 150
        profit_claimed = max_profit * Decimal("0.5")  # 75 (50% of max)

        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_type.id,
            invested_total=invested,
            profit_claimed=profit_claimed,
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        refund, fee_percent, _ = await sell_pet(db_session, user, pet.id)

        # At 50% profit: fee = 15% + (50% × 85%) = 57.5%
        expected_fee = Decimal("0.15") + (Decimal("0.5") * Decimal("0.85"))
        assert fee_percent == expected_fee
        expected_refund = invested * (Decimal("1") - expected_fee)
        assert refund == expected_refund

    @pytest.mark.asyncio
    async def test_sell_pet_at_roi_cap_zero_refund(self, db_session, user, pet_types):
        """Test selling pet at ROI cap returns zero (100% fee)."""
        # Create pet at 100% ROI cap
        pet_type = pet_types[0]
        invested = Decimal("100")
        max_profit = invested * pet_type.roi_cap_multiplier  # 150

        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_type.id,
            invested_total=invested,
            profit_claimed=max_profit,  # 100% of max profit
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        refund, fee_percent, _ = await sell_pet(db_session, user, pet.id)

        # At 100% profit: fee = 100%, refund = 0
        assert fee_percent == SELL_MAX_FEE
        assert refund == Decimal("0")

    @pytest.mark.asyncio
    async def test_sell_pet_creates_transaction(self, db_session, user, user_pet):
        """Test sell creates transaction with fee metadata."""
        await sell_pet(db_session, user, user_pet.id)

        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.type == TxType.SELL_REFUND
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet > 0

    @pytest.mark.asyncio
    async def test_sell_pet_not_found(self, db_session, user):
        """Test selling non-existent pet."""
        with pytest.raises(ValueError, match="Pet not found"):
            await sell_pet(db_session, user, 99999)

    @pytest.mark.asyncio
    async def test_sell_pet_already_sold(self, db_session, user, pet_types):
        """Test cannot sell already sold pet."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.SOLD,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="Cannot sell"):
            await sell_pet(db_session, user, pet.id)

    @pytest.mark.asyncio
    async def test_sell_pet_evolved(self, db_session, user, pet_types):
        """Test cannot sell evolved pet."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.EVOLVED,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="Cannot sell"):
            await sell_pet(db_session, user, pet.id)


class TestTraining:
    """Tests for pet training."""

    @pytest.mark.asyncio
    async def test_start_training_success(self, db_session, user, user_pet):
        """Test starting training."""
        pet = await start_training(db_session, user, user_pet.id)

        assert pet.status == PetStatus.TRAINING
        assert pet.training_started_at is not None
        assert pet.training_ends_at is not None
        assert (pet.training_ends_at - pet.training_started_at).total_seconds() == TRAINING_DURATION_HOURS * 3600

    @pytest.mark.asyncio
    async def test_start_training_not_idle(self, db_session, user, pet_types):
        """Test cannot start training if not idle."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.TRAINING,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        with pytest.raises(ValueError, match="idle"):
            await start_training(db_session, user, pet.id)

    @pytest.mark.asyncio
    async def test_check_training_status_complete(self, db_session, training_pet):
        """Test check_training_status marks complete training."""
        pet = check_training_status(training_pet)
        assert pet.status == PetStatus.READY_TO_CLAIM

    @pytest.mark.asyncio
    async def test_check_training_status_not_complete(self, db_session, user, pet_types):
        """Test check_training_status keeps training if not done."""
        now = datetime.now(timezone.utc)
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.TRAINING,
            slot_index=0,
            training_started_at=now,
            training_ends_at=now + timedelta(hours=24),
        )
        db_session.add(pet)
        await db_session.commit()

        pet = check_training_status(pet)
        assert pet.status == PetStatus.TRAINING


class TestClaimProfit:
    """Tests for claiming profit."""

    @pytest.mark.asyncio
    async def test_claim_profit_success(self, db_session, user, pet_types):
        """Test successful profit claim."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("0"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        # Load pet_type relation
        result = await db_session.execute(
            select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == pet.id)
        )
        pet = result.scalar_one()

        initial_balance = user.balance_xpet
        claim_result = await claim_profit(db_session, user, pet.id)

        # Daily profit = 5 * 0.01 = 0.05
        expected_profit = Decimal("0.05")
        assert claim_result["profit_claimed"] == expected_profit
        assert claim_result["evolved"] is False
        assert claim_result["pet_status"] == PetStatus.OWNED_IDLE

        await db_session.refresh(user)
        assert user.balance_xpet == initial_balance + expected_profit

    @pytest.mark.asyncio
    async def test_claim_profit_not_ready(self, db_session, user, user_pet):
        """Test cannot claim from non-ready pet."""
        with pytest.raises(ValueError, match="not ready"):
            await claim_profit(db_session, user, user_pet.id)

    @pytest.mark.asyncio
    async def test_claim_profit_evolution(self, db_session, user, pet_types):
        """Test pet evolves when ROI cap reached."""
        # Create pet near ROI cap
        # Max profit = 5 * 1.5 = 7.5
        # Already claimed 7.45, so next claim will push past cap
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.READY_TO_CLAIM,
            slot_index=0,
            profit_claimed=Decimal("7.45"),
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        result = await db_session.execute(
            select(UserPet).options(selectinload(UserPet.pet_type)).where(UserPet.id == pet.id)
        )
        pet = result.scalar_one()

        claim_result = await claim_profit(db_session, user, pet.id)

        assert claim_result["evolved"] is True
        assert claim_result["pet_status"] == PetStatus.EVOLVED
        assert "hall_of_fame_entry" in claim_result


class TestHallOfFame:
    """Tests for Hall of Fame."""

    @pytest.mark.asyncio
    async def test_get_hall_of_fame_empty(self, db_session, user):
        """Test empty hall of fame."""
        result = await get_hall_of_fame(db_session, user.id)
        assert result["pets"] == []
        assert result["total_pets_evolved"] == 0
        assert result["total_farmed_all_time"] == 0

    @pytest.mark.asyncio
    async def test_get_hall_of_fame_with_pets(self, db_session, user, pet_types):
        """Test hall of fame with evolved pets."""
        pet = UserPet(
            user_id=user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.MYTHIC,
            status=PetStatus.EVOLVED,
            slot_index=0,
            profit_claimed=Decimal("7.5"),
            evolved_at=datetime.now(timezone.utc),
        )
        db_session.add(pet)
        await db_session.commit()

        result = await get_hall_of_fame(db_session, user.id)
        assert result["total_pets_evolved"] == 1
        assert result["total_farmed_all_time"] == Decimal("7.5")


class TestPetRoutes:
    """Tests for pet API routes."""

    @pytest.mark.asyncio
    async def test_get_catalog(self, client, pet_types):
        """Test getting pet catalog."""
        response = await client.get("/pets/catalog")
        assert response.status_code == 200
        data = response.json()
        assert len(data["pets"]) == 3  # Only active pets

    @pytest.mark.asyncio
    async def test_get_my_pets_empty(self, client, user, auth_headers):
        """Test getting pets when user has none."""
        response = await client.get("/pets/my", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["pets"] == []
        assert data["free_slots"] == MAX_SLOTS

    @pytest.mark.asyncio
    async def test_get_my_pets_with_pets(self, client, user, auth_headers, user_pet, pet_types):
        """Test getting pets when user has some."""
        response = await client.get("/pets/my", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["pets"]) == 1
        assert data["free_slots"] == MAX_SLOTS - 1

    @pytest.mark.asyncio
    async def test_buy_pet_route(self, client, rich_user, rich_auth_headers, pet_types):
        """Test buying pet via API."""
        response = await client.post(
            "/pets/buy",
            headers=rich_auth_headers,
            json={"pet_type_id": pet_types[0].id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "pet" in data
        assert "new_balance" in data

    @pytest.mark.asyncio
    async def test_buy_pet_insufficient_balance(self, client, user, auth_headers, pet_types):
        """Test buying pet with insufficient balance."""
        # User has 100, try to buy pet costing more
        user.balance_xpet = Decimal("1")

        response = await client.post(
            "/pets/buy",
            headers=auth_headers,
            json={"pet_type_id": pet_types[1].id}  # 50 XPET
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upgrade_pet_route(self, client, rich_user, rich_auth_headers, pet_types, db_session):
        """Test upgrading pet via API."""
        # Create pet for rich user
        pet = UserPet(
            user_id=rich_user.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.OWNED_IDLE,
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()
        await db_session.refresh(pet)

        response = await client.post(
            "/pets/upgrade",
            headers=rich_auth_headers,
            json={"pet_id": pet.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pet"]["level"] == "ADULT"

    @pytest.mark.asyncio
    async def test_sell_pet_route(self, client, user, auth_headers, user_pet):
        """Test selling pet via API."""
        response = await client.post(
            "/pets/sell",
            headers=auth_headers,
            json={"pet_id": user_pet.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "refund_amount" in data
        assert "fee_percent" in data
        assert "new_balance" in data
        # New pet with no profit = 15% fee
        assert Decimal(data["fee_percent"]) == Decimal("15")

    @pytest.mark.asyncio
    async def test_start_training_route(self, client, user, auth_headers, user_pet):
        """Test starting training via API."""
        response = await client.post(
            "/pets/start-training",
            headers=auth_headers,
            json={"pet_id": user_pet.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "TRAINING"
        assert "training_started_at" in data
        assert "training_ends_at" in data

    @pytest.mark.asyncio
    async def test_claim_route(self, client, user, auth_headers, ready_to_claim_pet, pet_types, db_session):
        """Test claiming profit via API."""
        response = await client.post(
            "/pets/claim",
            headers=auth_headers,
            json={"pet_id": ready_to_claim_pet.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "profit_claimed" in data
        assert "new_balance" in data

    @pytest.mark.asyncio
    async def test_hall_of_fame_route(self, client, user, auth_headers):
        """Test hall of fame via API."""
        response = await client.get("/pets/hall-of-fame", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "pets" in data
        assert "total_pets_evolved" in data
        assert "total_farmed_all_time" in data
