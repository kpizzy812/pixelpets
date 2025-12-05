"""
Test fixtures and configuration for Pixel Pets backend tests.
"""
import asyncio
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import AsyncGenerator
from urllib.parse import urlencode

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["TELEGRAM_BOT_TOKEN"] = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models import (
    User, PetType, UserPet, Transaction, Task, UserTask,
    DepositRequest, WithdrawRequest, ReferralStats, ReferralReward,
    Admin, SystemConfig, AdminActionLog,
    PetStatus, PetLevel, TxType, TaskType, TaskStatus, NetworkType, RequestStatus, AdminRole
)
from app.services.auth import create_access_token
from app.services.admin.auth import hash_password
from app.core.admin_security import create_admin_access_token


# Test database engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database dependency override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ============== User Fixtures ==============

@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    """Create a basic test user."""
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="TESTCODE",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_with_referrer(db_session: AsyncSession, user: User) -> User:
    """Create a user with a referrer."""
    referred_user = User(
        telegram_id=987654321,
        username="referreduser",
        first_name="Referred",
        last_name="User",
        language_code="en",
        balance_xpet=Decimal("50"),
        ref_code="REFCODE2",
        referrer_id=user.id,
    )
    db_session.add(referred_user)
    await db_session.commit()
    await db_session.refresh(referred_user)
    return referred_user


@pytest_asyncio.fixture
async def rich_user(db_session: AsyncSession) -> User:
    """Create a user with high balance."""
    user = User(
        telegram_id=111222333,
        username="richuser",
        first_name="Rich",
        last_name="User",
        language_code="en",
        balance_xpet=Decimal("10000"),
        ref_code="RICHCODE",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============== Auth Fixtures ==============

@pytest.fixture
def auth_headers(user: User) -> dict:
    """Generate auth headers for a user."""
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def rich_auth_headers(rich_user: User) -> dict:
    """Generate auth headers for rich user."""
    token = create_access_token(rich_user.id)
    return {"Authorization": f"Bearer {token}"}


def generate_telegram_init_data(
    user_id: int = 123456789,
    username: str = "testuser",
    first_name: str = "Test",
    last_name: str = "User",
    language_code: str = "en",
) -> str:
    """Generate valid Telegram initData for testing."""
    user_data = {
        "id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "language_code": language_code,
    }

    params = {
        "user": json.dumps(user_data),
        "auth_date": str(int(datetime.now(timezone.utc).timestamp())),
        "query_id": "test_query_id",
    }

    # Build data check string (sorted, without hash)
    data_pairs = [f"{k}={v}" for k, v in sorted(params.items())]
    data_check_string = "\n".join(data_pairs)

    # Calculate secret key
    secret_key = hmac.new(
        b"WebAppData",
        settings.TELEGRAM_BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    # Calculate hash
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    params["hash"] = hash_value

    return urlencode(params)


# ============== Pet Fixtures ==============

@pytest_asyncio.fixture
async def pet_types(db_session: AsyncSession) -> list[PetType]:
    """Create standard pet types for testing."""
    types = [
        PetType(
            name="Bubble Slime",
            emoji="🫧",
            image_key="bubble",
            base_price=Decimal("5"),
            daily_rate=Decimal("0.01"),
            roi_cap_multiplier=Decimal("1.5"),
            level_prices={"BABY": 5, "ADULT": 20, "MYTHIC": 50},
            is_active=True,
        ),
        PetType(
            name="Pixel Fox",
            emoji="🦊",
            image_key="fox",
            base_price=Decimal("50"),
            daily_rate=Decimal("0.012"),
            roi_cap_multiplier=Decimal("1.6"),
            level_prices={"BABY": 50, "ADULT": 200, "MYTHIC": 500},
            is_active=True,
        ),
        PetType(
            name="Glitch Cat",
            emoji="🐱",
            image_key="cat",
            base_price=Decimal("100"),
            daily_rate=Decimal("0.015"),
            roi_cap_multiplier=Decimal("1.7"),
            level_prices={"BABY": 100, "ADULT": 400, "MYTHIC": 1000},
            is_active=True,
        ),
        PetType(
            name="Inactive Pet",
            emoji="❌",
            image_key="inactive",
            base_price=Decimal("10"),
            daily_rate=Decimal("0.01"),
            roi_cap_multiplier=Decimal("1.5"),
            level_prices={"BABY": 10, "ADULT": 40, "MYTHIC": 100},
            is_active=False,
        ),
    ]
    for pt in types:
        db_session.add(pt)
    await db_session.commit()
    for pt in types:
        await db_session.refresh(pt)
    return types


@pytest_asyncio.fixture
async def user_pet(db_session: AsyncSession, user: User, pet_types: list[PetType]) -> UserPet:
    """Create a pet owned by user."""
    pet = UserPet(
        user_id=user.id,
        pet_type_id=pet_types[0].id,
        invested_total=Decimal("5"),
        level=PetLevel.BABY,
        status=PetStatus.OWNED_IDLE,
        slot_index=0,
    )
    db_session.add(pet)
    await db_session.commit()
    await db_session.refresh(pet)
    return pet


@pytest_asyncio.fixture
async def training_pet(db_session: AsyncSession, user: User, pet_types: list[PetType]) -> UserPet:
    """Create a pet in training state."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    pet = UserPet(
        user_id=user.id,
        pet_type_id=pet_types[0].id,
        invested_total=Decimal("5"),
        level=PetLevel.BABY,
        status=PetStatus.TRAINING,
        slot_index=1,
        training_started_at=now - timedelta(hours=25),  # Started 25 hours ago
        training_ends_at=now - timedelta(hours=1),  # Ended 1 hour ago
    )
    db_session.add(pet)
    await db_session.commit()
    await db_session.refresh(pet)
    return pet


@pytest_asyncio.fixture
async def ready_to_claim_pet(db_session: AsyncSession, user: User, pet_types: list[PetType]) -> UserPet:
    """Create a pet ready to claim."""
    pet = UserPet(
        user_id=user.id,
        pet_type_id=pet_types[0].id,
        invested_total=Decimal("5"),
        level=PetLevel.BABY,
        status=PetStatus.READY_TO_CLAIM,
        slot_index=0,
    )
    db_session.add(pet)
    await db_session.commit()
    await db_session.refresh(pet)
    return pet


# ============== Task Fixtures ==============

@pytest_asyncio.fixture
async def tasks(db_session: AsyncSession) -> list[Task]:
    """Create test tasks."""
    task_list = [
        Task(
            title="Join Telegram Channel",
            description="Join our official channel",
            reward_xpet=Decimal("0.30"),
            link="https://t.me/pixelpets_official",
            task_type=TaskType.TELEGRAM_CHANNEL,
            is_active=True,
            order=1,
        ),
        Task(
            title="Follow Twitter",
            description="Follow us on Twitter",
            reward_xpet=Decimal("0.20"),
            link="https://twitter.com/pixelpets",
            task_type=TaskType.TWITTER,
            is_active=True,
            order=2,
        ),
        Task(
            title="Inactive Task",
            description="This task is inactive",
            reward_xpet=Decimal("1.00"),
            link="https://example.com",
            task_type=TaskType.OTHER,
            is_active=False,
            order=3,
        ),
    ]
    for task in task_list:
        db_session.add(task)
    await db_session.commit()
    for task in task_list:
        await db_session.refresh(task)
    return task_list


# ============== Referral Fixtures ==============

@pytest_asyncio.fixture
async def referral_chain(db_session: AsyncSession, pet_types: list[PetType]) -> list[User]:
    """Create a 5-level referral chain for testing."""
    users = []

    # Level 5 (top of chain - no referrer)
    user5 = User(
        telegram_id=500000005,
        username="user5",
        first_name="User",
        last_name="Five",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="LEVEL5",
        ref_levels_unlocked=5,  # All levels unlocked
    )
    db_session.add(user5)
    await db_session.commit()
    await db_session.refresh(user5)
    users.append(user5)

    # Level 4
    user4 = User(
        telegram_id=500000004,
        username="user4",
        first_name="User",
        last_name="Four",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="LEVEL4",
        referrer_id=user5.id,
        ref_levels_unlocked=4,
    )
    db_session.add(user4)
    await db_session.commit()
    await db_session.refresh(user4)
    users.append(user4)

    # Level 3
    user3 = User(
        telegram_id=500000003,
        username="user3",
        first_name="User",
        last_name="Three",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="LEVEL3",
        referrer_id=user4.id,
        ref_levels_unlocked=3,
    )
    db_session.add(user3)
    await db_session.commit()
    await db_session.refresh(user3)
    users.append(user3)

    # Level 2
    user2 = User(
        telegram_id=500000002,
        username="user2",
        first_name="User",
        last_name="Two",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="LEVEL2",
        referrer_id=user3.id,
        ref_levels_unlocked=2,
    )
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)
    users.append(user2)

    # Level 1 (direct referrer)
    user1 = User(
        telegram_id=500000001,
        username="user1",
        first_name="User",
        last_name="One",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="LEVEL1",
        referrer_id=user2.id,
        ref_levels_unlocked=1,
    )
    db_session.add(user1)
    await db_session.commit()
    await db_session.refresh(user1)
    users.append(user1)

    # Claiming user (at the bottom)
    claiming_user = User(
        telegram_id=500000000,
        username="claimer",
        first_name="Claiming",
        last_name="User",
        language_code="en",
        balance_xpet=Decimal("100"),
        ref_code="CLAIMER",
        referrer_id=user1.id,
    )
    db_session.add(claiming_user)
    await db_session.commit()
    await db_session.refresh(claiming_user)
    users.append(claiming_user)

    # Give claimer a pet so they can claim
    pet = UserPet(
        user_id=claiming_user.id,
        pet_type_id=pet_types[0].id,
        invested_total=Decimal("5"),
        level=PetLevel.BABY,
        status=PetStatus.READY_TO_CLAIM,
        slot_index=0,
    )
    db_session.add(pet)
    await db_session.commit()

    # users: [user5, user4, user3, user2, user1, claiming_user]
    # referral chain: claiming_user -> user1 -> user2 -> user3 -> user4 -> user5
    return users


# ============== Transaction Fixtures ==============

@pytest_asyncio.fixture
async def transactions(db_session: AsyncSession, user: User) -> list[Transaction]:
    """Create test transactions."""
    tx_list = [
        Transaction(
            user_id=user.id,
            type=TxType.DEPOSIT,
            amount_xpet=Decimal("100"),
        ),
        Transaction(
            user_id=user.id,
            type=TxType.PET_BUY,
            amount_xpet=Decimal("-5"),
            meta={"pet_type_id": 1, "pet_name": "Bubble Slime"},
        ),
        Transaction(
            user_id=user.id,
            type=TxType.CLAIM,
            amount_xpet=Decimal("0.05"),
            meta={"pet_id": 1},
        ),
    ]
    for tx in tx_list:
        db_session.add(tx)
    await db_session.commit()
    for tx in tx_list:
        await db_session.refresh(tx)
    return tx_list


# ============== Admin Fixtures ==============

@pytest_asyncio.fixture
async def super_admin(db_session: AsyncSession) -> Admin:
    """Create a super admin for testing."""
    admin = Admin(
        username="superadmin",
        password_hash=hash_password("superpass123"),
        email="super@pixelpets.io",
        role=AdminRole.SUPER_ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> Admin:
    """Create a regular admin for testing."""
    admin = Admin(
        username="adminuser",
        password_hash=hash_password("adminpass123"),
        email="admin@pixelpets.io",
        role=AdminRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def moderator(db_session: AsyncSession) -> Admin:
    """Create a moderator for testing."""
    admin = Admin(
        username="moderator",
        password_hash=hash_password("modpass123"),
        email="mod@pixelpets.io",
        role=AdminRole.MODERATOR,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def inactive_admin(db_session: AsyncSession) -> Admin:
    """Create an inactive admin for testing."""
    admin = Admin(
        username="inactiveadmin",
        password_hash=hash_password("inactivepass"),
        email="inactive@pixelpets.io",
        role=AdminRole.ADMIN,
        is_active=False,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
def super_admin_headers(super_admin: Admin) -> dict:
    """Generate auth headers for super admin."""
    token = create_admin_access_token(super_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user: Admin) -> dict:
    """Generate auth headers for regular admin."""
    token = create_admin_access_token(admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def moderator_headers(moderator: Admin) -> dict:
    """Generate auth headers for moderator."""
    token = create_admin_access_token(moderator.id)
    return {"Authorization": f"Bearer {token}"}


# ============== Deposit/Withdrawal Request Fixtures ==============

@pytest_asyncio.fixture
async def pending_deposit(db_session: AsyncSession, user: User) -> DepositRequest:
    """Create a pending deposit request."""
    deposit = DepositRequest(
        user_id=user.id,
        amount=Decimal("100"),
        network=NetworkType.BEP20,
        deposit_address="0x1234567890abcdef",
        status=RequestStatus.PENDING,
    )
    db_session.add(deposit)
    await db_session.commit()
    await db_session.refresh(deposit)
    return deposit


@pytest_asyncio.fixture
async def pending_withdrawal(db_session: AsyncSession, user: User) -> WithdrawRequest:
    """Create a pending withdrawal request."""
    withdrawal = WithdrawRequest(
        user_id=user.id,
        amount=Decimal("50"),
        fee=Decimal("2"),
        network=NetworkType.BEP20,
        wallet_address="0xabcdef1234567890",
        status=RequestStatus.PENDING,
    )
    db_session.add(withdrawal)
    await db_session.commit()
    await db_session.refresh(withdrawal)
    return withdrawal


# ============== System Config Fixtures ==============

@pytest_asyncio.fixture
async def system_configs(db_session: AsyncSession) -> list[SystemConfig]:
    """Create system config entries for testing."""
    configs = [
        SystemConfig(
            key="referral_percentages",
            value={"1": 20, "2": 15, "3": 10, "4": 5, "5": 2},
            description="Referral commission percentages",
        ),
        SystemConfig(
            key="referral_unlock_thresholds",
            value={"1": 0, "2": 3, "3": 5, "4": 10, "5": 20},
            description="Referral level unlock thresholds",
        ),
        SystemConfig(
            key="withdraw_min",
            value=5,
            description="Minimum withdrawal amount",
        ),
    ]
    for cfg in configs:
        db_session.add(cfg)
    await db_session.commit()
    for cfg in configs:
        await db_session.refresh(cfg)
    return configs
