"""
Tests for referrals service and routes.
"""
import pytest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User, UserPet, Transaction, ReferralStats, ReferralReward, PetLevel, PetStatus, TxType
from app.services.referrals import (
    get_active_referrals_count,
    update_user_ref_levels,
    get_referrer_chain,
    process_referral_rewards,
    update_referral_stats,
    get_referral_stats,
    get_level_referrals_count,
    generate_ref_link,
    get_share_text,
    get_bot_username,
)


class TestReferralHelpers:
    """Tests for referral helper functions."""

    @pytest.mark.asyncio
    async def test_generate_ref_link(self, db_session):
        """Test referral link generation."""
        ref_code = "ABC12345"
        bot_username = await get_bot_username(db_session)
        link = await generate_ref_link(db_session, ref_code)
        assert link == f"https://t.me/{bot_username}?start={ref_code}"

    def test_get_share_text(self):
        """Test share text."""
        text = get_share_text()
        assert isinstance(text, str)
        assert len(text) > 0


class TestActiveReferrals:
    """Tests for active referral counting."""

    @pytest.mark.asyncio
    async def test_get_active_referrals_count_no_referrals(self, db_session, user):
        """Test counting active referrals when none exist."""
        count = await get_active_referrals_count(db_session, user.id)
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_active_referrals_count_with_referrals(self, db_session, user, pet_types):
        """Test counting active referrals with pets."""
        # Create referrals with pets
        for i in range(3):
            referral = User(
                telegram_id=200000000 + i,
                username=f"referral{i}",
                first_name=f"Referral{i}",
                language_code="en",
                ref_code=f"REF{i:05d}",
                referrer_id=user.id,
            )
            db_session.add(referral)
            await db_session.commit()
            await db_session.refresh(referral)

            # Give them a pet
            pet = UserPet(
                user_id=referral.id,
                pet_type_id=pet_types[0].id,
                invested_total=Decimal("5"),
                level=PetLevel.BABY,
                status=PetStatus.OWNED_IDLE,
                slot_index=0,
            )
            db_session.add(pet)

        await db_session.commit()

        count = await get_active_referrals_count(db_session, user.id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_get_active_referrals_excludes_no_pets(self, db_session, user):
        """Test that referrals without pets are not counted."""
        # Create referral without pet
        referral = User(
            telegram_id=300000000,
            username="nopet",
            first_name="NoPet",
            language_code="en",
            ref_code="NOPET123",
            referrer_id=user.id,
        )
        db_session.add(referral)
        await db_session.commit()

        count = await get_active_referrals_count(db_session, user.id)
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_active_referrals_excludes_sold_pets(self, db_session, user, pet_types):
        """Test that referrals with only sold pets are not counted."""
        # Create referral with sold pet
        referral = User(
            telegram_id=400000000,
            username="soldpet",
            first_name="SoldPet",
            language_code="en",
            ref_code="SOLD1234",
            referrer_id=user.id,
        )
        db_session.add(referral)
        await db_session.commit()
        await db_session.refresh(referral)

        pet = UserPet(
            user_id=referral.id,
            pet_type_id=pet_types[0].id,
            invested_total=Decimal("5"),
            level=PetLevel.BABY,
            status=PetStatus.SOLD,  # Pet is sold
            slot_index=0,
        )
        db_session.add(pet)
        await db_session.commit()

        count = await get_active_referrals_count(db_session, user.id)
        assert count == 0


class TestRefLevels:
    """Tests for referral level unlocking."""

    @pytest.mark.asyncio
    async def test_update_ref_levels_default(self, db_session, user):
        """Test default ref level is 1."""
        levels = await update_user_ref_levels(db_session, user)
        assert levels == 1

    @pytest.mark.asyncio
    async def test_update_ref_levels_unlock_level_2(self, db_session, user, pet_types):
        """Test unlocking level 2 with 3 active referrals."""
        # Need 3 active referrals for level 2
        for i in range(3):
            referral = User(
                telegram_id=600000000 + i,
                username=f"ref2_{i}",
                first_name=f"Ref{i}",
                language_code="en",
                ref_code=f"LV2{i:05d}",
                referrer_id=user.id,
            )
            db_session.add(referral)
            await db_session.commit()
            await db_session.refresh(referral)

            pet = UserPet(
                user_id=referral.id,
                pet_type_id=pet_types[0].id,
                invested_total=Decimal("5"),
                level=PetLevel.BABY,
                status=PetStatus.OWNED_IDLE,
                slot_index=0,
            )
            db_session.add(pet)
        await db_session.commit()

        levels = await update_user_ref_levels(db_session, user)
        assert levels == 2

    @pytest.mark.asyncio
    async def test_update_ref_levels_unlock_level_3(self, db_session, user, pet_types):
        """Test unlocking level 3 with 5 active referrals."""
        for i in range(5):
            referral = User(
                telegram_id=700000000 + i,
                username=f"ref3_{i}",
                first_name=f"Ref{i}",
                language_code="en",
                ref_code=f"LV3{i:05d}",
                referrer_id=user.id,
            )
            db_session.add(referral)
            await db_session.commit()
            await db_session.refresh(referral)

            pet = UserPet(
                user_id=referral.id,
                pet_type_id=pet_types[0].id,
                invested_total=Decimal("5"),
                level=PetLevel.BABY,
                status=PetStatus.OWNED_IDLE,
                slot_index=0,
            )
            db_session.add(pet)
        await db_session.commit()

        levels = await update_user_ref_levels(db_session, user)
        assert levels == 3


class TestReferrerChain:
    """Tests for getting referrer chain."""

    @pytest.mark.asyncio
    async def test_get_referrer_chain_no_referrer(self, db_session, user):
        """Test chain when user has no referrer."""
        chain = await get_referrer_chain(db_session, user.id)
        assert chain == []

    @pytest.mark.asyncio
    async def test_get_referrer_chain_one_level(self, db_session, user, user_with_referrer):
        """Test chain with one referrer."""
        chain = await get_referrer_chain(db_session, user_with_referrer.id)
        assert len(chain) == 1
        assert chain[0].id == user.id

    @pytest.mark.asyncio
    async def test_get_referrer_chain_five_levels(self, db_session, referral_chain):
        """Test chain with 5 levels."""
        # referral_chain: [user5, user4, user3, user2, user1, claiming_user]
        claiming_user = referral_chain[-1]
        chain = await get_referrer_chain(db_session, claiming_user.id)

        # Chain should be: user1, user2, user3, user4, user5
        assert len(chain) == 5
        assert chain[0].id == referral_chain[4].id  # user1
        assert chain[1].id == referral_chain[3].id  # user2
        assert chain[2].id == referral_chain[2].id  # user3
        assert chain[3].id == referral_chain[1].id  # user4
        assert chain[4].id == referral_chain[0].id  # user5


class TestProcessReferralRewards:
    """Tests for referral reward processing."""

    @pytest.mark.asyncio
    async def test_process_referral_rewards_single_level(self, db_session, user, user_with_referrer):
        """Test rewards for single level."""
        claim_amount = Decimal("10")

        rewards = await process_referral_rewards(db_session, user_with_referrer, claim_amount)

        # Level 1 reward: 20% of 10 = 2
        assert len(rewards) == 1
        assert rewards[0]["level"] == 1
        assert rewards[0]["reward_amount"] == Decimal("2")

        # Check referrer balance increased
        await db_session.refresh(user)
        assert user.balance_xpet == Decimal("102")  # 100 + 2

    @pytest.mark.asyncio
    async def test_process_referral_rewards_creates_records(self, db_session, user, user_with_referrer):
        """Test that reward records are created."""
        claim_amount = Decimal("10")

        await process_referral_rewards(db_session, user_with_referrer, claim_amount)

        # Check ReferralReward record
        result = await db_session.execute(
            select(ReferralReward).where(ReferralReward.to_user_id == user.id)
        )
        reward = result.scalar_one()
        assert reward.from_user_id == user_with_referrer.id
        assert reward.level == 1
        assert reward.reward_amount == Decimal("2")

        # Check Transaction record
        result = await db_session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.type == TxType.REF_REWARD
            )
        )
        tx = result.scalar_one()
        assert tx.amount_xpet == Decimal("2")

    @pytest.mark.asyncio
    async def test_process_referral_rewards_five_levels(self, db_session, referral_chain):
        """Test rewards distributed to 5 levels."""
        claiming_user = referral_chain[-1]
        claim_amount = Decimal("100")

        rewards = await process_referral_rewards(db_session, claiming_user, claim_amount)

        # Expected rewards:
        # Level 1: 20% = 20 (user1 has level 1 unlocked)
        # Level 2: 15% = 15 (user2 has level 2 unlocked)
        # Level 3: 10% = 10 (user3 has level 3 unlocked)
        # Level 4: 5% = 5 (user4 has level 4 unlocked)
        # Level 5: 2% = 2 (user5 has level 5 unlocked)
        assert len(rewards) == 5

        expected = [
            (1, Decimal("20")),
            (2, Decimal("15")),
            (3, Decimal("10")),
            (4, Decimal("5")),
            (5, Decimal("2")),
        ]

        for i, (level, amount) in enumerate(expected):
            assert rewards[i]["level"] == level
            assert rewards[i]["reward_amount"] == amount

    @pytest.mark.asyncio
    async def test_process_referral_rewards_respects_level_lock(self, db_session, pet_types):
        """Test rewards skip users without unlocked level."""
        # Create chain where level 2 referrer only has level 1 unlocked
        user2 = User(
            telegram_id=800000002,
            username="locktest2",
            first_name="Lock",
            language_code="en",
            ref_code="LOCK0002",
            ref_levels_unlocked=1,  # Only level 1 unlocked
            balance_xpet=Decimal("100"),
        )
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user2)

        user1 = User(
            telegram_id=800000001,
            username="locktest1",
            first_name="Lock",
            language_code="en",
            ref_code="LOCK0001",
            referrer_id=user2.id,
            ref_levels_unlocked=1,
            balance_xpet=Decimal("100"),
        )
        db_session.add(user1)
        await db_session.commit()
        await db_session.refresh(user1)

        claimer = User(
            telegram_id=800000000,
            username="lockclaimer",
            first_name="Claimer",
            language_code="en",
            ref_code="LOCK0000",
            referrer_id=user1.id,
            balance_xpet=Decimal("100"),
        )
        db_session.add(claimer)
        await db_session.commit()
        await db_session.refresh(claimer)

        rewards = await process_referral_rewards(db_session, claimer, Decimal("10"))

        # Only level 1 reward should be given (user1 gets it)
        # user2 is at level 2 in chain but only has level 1 unlocked
        assert len(rewards) == 1
        assert rewards[0]["level"] == 1


class TestReferralStats:
    """Tests for referral statistics."""

    @pytest.mark.asyncio
    async def test_update_referral_stats_creates_new(self, db_session, user):
        """Test updating stats creates new record if none exists."""
        await update_referral_stats(db_session, user.id, 1, Decimal("5"))
        await db_session.commit()

        result = await db_session.execute(
            select(ReferralStats).where(ReferralStats.user_id == user.id)
        )
        stats = result.scalar_one()
        assert stats.level_1_earned == Decimal("5")
        assert stats.total_earned == Decimal("5")

    @pytest.mark.asyncio
    async def test_update_referral_stats_accumulates(self, db_session, user):
        """Test stats accumulate over multiple updates."""
        await update_referral_stats(db_session, user.id, 1, Decimal("5"))
        await db_session.commit()
        await update_referral_stats(db_session, user.id, 1, Decimal("3"))
        await db_session.commit()

        result = await db_session.execute(
            select(ReferralStats).where(ReferralStats.user_id == user.id)
        )
        stats = result.scalar_one()
        assert stats.level_1_earned == Decimal("8")
        assert stats.total_earned == Decimal("8")

    @pytest.mark.asyncio
    async def test_get_referral_stats(self, db_session, user):
        """Test getting referral stats."""
        stats = await get_referral_stats(db_session, user)

        assert stats["ref_code"] == user.ref_code
        assert stats["total_earned_xpet"] == Decimal("0")
        assert stats["levels_unlocked"] == 1
        assert len(stats["levels"]) == 5

    @pytest.mark.asyncio
    async def test_get_level_referrals_count_level_1(self, db_session, user):
        """Test counting level 1 referrals."""
        # Create direct referrals
        for i in range(3):
            referral = User(
                telegram_id=900000000 + i,
                username=f"count1_{i}",
                first_name=f"Count{i}",
                language_code="en",
                ref_code=f"CNT1{i:04d}",
                referrer_id=user.id,
            )
            db_session.add(referral)
        await db_session.commit()

        count = await get_level_referrals_count(db_session, user.id, 1)
        assert count == 3

    @pytest.mark.asyncio
    async def test_get_level_referrals_count_level_2(self, db_session, user):
        """Test counting level 2 referrals."""
        # Create level 1 referral
        level1 = User(
            telegram_id=950000000,
            username="level1",
            first_name="Level1",
            language_code="en",
            ref_code="L1TEST",
            referrer_id=user.id,
        )
        db_session.add(level1)
        await db_session.commit()
        await db_session.refresh(level1)

        # Create level 2 referrals (referred by level1)
        for i in range(2):
            level2 = User(
                telegram_id=960000000 + i,
                username=f"level2_{i}",
                first_name=f"Level2_{i}",
                language_code="en",
                ref_code=f"L2T{i:04d}",
                referrer_id=level1.id,
            )
            db_session.add(level2)
        await db_session.commit()

        count = await get_level_referrals_count(db_session, user.id, 2)
        assert count == 2


class TestReferralRoutes:
    """Tests for referral API routes."""

    @pytest.mark.asyncio
    async def test_get_referral_link(self, client, user, auth_headers):
        """Test getting referral link."""
        response = await client.get("/referrals/link", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ref_code"] == user.ref_code
        assert user.ref_code in data["ref_link"]
        assert "share_text" in data

    @pytest.mark.asyncio
    async def test_get_referrals(self, client, user, auth_headers, db_session):
        """Test getting referral stats."""
        response = await client.get("/referrals", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ref_code"] == user.ref_code
        assert "total_earned_xpet" in data
        assert "levels_unlocked" in data
        assert "levels" in data
        assert len(data["levels"]) == 5
        assert "active_referrals_count" in data

    @pytest.mark.asyncio
    async def test_get_referrals_levels_structure(self, client, user, auth_headers, db_session):
        """Test referral levels have correct structure."""
        response = await client.get("/referrals", headers=auth_headers)
        data = response.json()

        for level_info in data["levels"]:
            assert "level" in level_info
            assert "percent" in level_info
            assert "unlocked" in level_info
            assert "referrals_count" in level_info
            assert "earned_xpet" in level_info

    @pytest.mark.asyncio
    async def test_referrals_unauthorized(self, client):
        """Test referral routes require auth."""
        response = await client.get("/referrals/link")
        assert response.status_code == 401

        response = await client.get("/referrals")
        assert response.status_code == 401
