"""
Tests for auth service and routes.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy import select

from app.models import User
from app.services.auth import (
    generate_ref_code,
    validate_telegram_init_data,
    create_access_token,
    decode_access_token,
    get_or_create_user,
)
from tests.conftest import generate_telegram_init_data


class TestAuthService:
    """Tests for auth service functions."""

    def test_generate_ref_code_length(self):
        """Test that ref code has correct length."""
        code = generate_ref_code()
        assert len(code) == 8

    def test_generate_ref_code_custom_length(self):
        """Test that ref code respects custom length."""
        code = generate_ref_code(length=12)
        assert len(code) == 12

    def test_generate_ref_code_characters(self):
        """Test that ref code contains only valid characters."""
        code = generate_ref_code()
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        assert all(c in valid_chars for c in code)

    def test_generate_ref_code_uniqueness(self):
        """Test that generated codes are unique."""
        codes = [generate_ref_code() for _ in range(100)]
        assert len(codes) == len(set(codes))  # All should be unique

    def test_validate_telegram_init_data_valid(self):
        """Test validation of valid Telegram initData."""
        init_data = generate_telegram_init_data(
            user_id=123456789,
            username="testuser",
            first_name="Test",
        )
        result = validate_telegram_init_data(init_data)
        assert result is not None
        assert result["id"] == 123456789
        assert result["username"] == "testuser"

    def test_validate_telegram_init_data_invalid_hash(self):
        """Test validation fails with invalid hash."""
        init_data = "user=%7B%22id%22%3A123%7D&hash=invalidhash"
        result = validate_telegram_init_data(init_data)
        assert result is None

    def test_validate_telegram_init_data_no_hash(self):
        """Test validation fails without hash."""
        init_data = "user=%7B%22id%22%3A123%7D"
        result = validate_telegram_init_data(init_data)
        assert result is None

    def test_validate_telegram_init_data_malformed(self):
        """Test validation fails with malformed data."""
        result = validate_telegram_init_data("not_valid_data")
        assert result is None

    def test_create_access_token(self):
        """Test JWT token creation."""
        token = create_access_token(user_id=123)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid(self):
        """Test decoding valid JWT token."""
        user_id = 456
        token = create_access_token(user_id=user_id)
        decoded_id = decode_access_token(token)
        assert decoded_id == user_id

    def test_decode_access_token_invalid(self):
        """Test decoding invalid JWT token returns None."""
        result = decode_access_token("invalid.token.here")
        assert result is None

    def test_decode_access_token_tampered(self):
        """Test decoding tampered JWT token returns None."""
        token = create_access_token(user_id=123)
        # Tamper with token
        tampered = token[:-5] + "XXXXX"
        result = decode_access_token(tampered)
        assert result is None


class TestGetOrCreateUser:
    """Tests for get_or_create_user function."""

    @pytest.mark.asyncio
    async def test_create_new_user(self, db_session):
        """Test creating a new user."""
        user, is_new = await get_or_create_user(
            db=db_session,
            telegram_id=999888777,
            username="newuser",
            first_name="New",
            last_name="User",
            language_code="ru",
        )

        assert user is not None
        assert is_new is True
        assert user.telegram_id == 999888777
        assert user.username == "newuser"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.language_code == "ru"
        assert user.balance_xpet == Decimal("0")
        assert len(user.ref_code) == 8
        assert user.referrer_id is None

    @pytest.mark.asyncio
    async def test_get_existing_user(self, db_session, user):
        """Test getting existing user updates their info."""
        original_ref_code = user.ref_code

        updated_user, is_new = await get_or_create_user(
            db=db_session,
            telegram_id=user.telegram_id,
            username="updated_username",
            first_name="Updated",
            last_name="Name",
            language_code="de",
        )

        assert is_new is False
        assert updated_user.id == user.id
        assert updated_user.username == "updated_username"
        assert updated_user.first_name == "Updated"
        assert updated_user.ref_code == original_ref_code  # Should not change

    @pytest.mark.asyncio
    async def test_create_user_with_referrer(self, db_session, user):
        """Test creating user with valid referral code."""
        new_user, is_new = await get_or_create_user(
            db=db_session,
            telegram_id=888777666,
            username="referred",
            first_name="Referred",
            last_name="User",
            language_code="en",
            ref_code_from_link=user.ref_code,
        )

        assert is_new is True
        assert new_user.referrer_id == user.id

    @pytest.mark.asyncio
    async def test_create_user_with_invalid_referrer(self, db_session):
        """Test creating user with invalid referral code."""
        new_user, is_new = await get_or_create_user(
            db=db_session,
            telegram_id=777666555,
            username="noreferrer",
            first_name="No",
            last_name="Referrer",
            language_code="en",
            ref_code_from_link="INVALID123",
        )

        assert is_new is True
        assert new_user.referrer_id is None


class TestAuthRoutes:
    """Tests for auth API routes."""

    @pytest.mark.asyncio
    async def test_telegram_auth_success(self, client, db_session):
        """Test successful Telegram authentication."""
        init_data = generate_telegram_init_data(
            user_id=555444333,
            username="authtest",
            first_name="Auth",
            last_name="Test",
        )

        response = await client.post(
            "/auth/telegram",
            json={"init_data": init_data}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["telegram_id"] == 555444333
        assert data["user"]["username"] == "authtest"

    @pytest.mark.asyncio
    async def test_telegram_auth_with_ref_code(self, client, db_session, user):
        """Test Telegram auth with referral code."""
        init_data = generate_telegram_init_data(
            user_id=444333222,
            username="referred",
        )

        response = await client.post(
            "/auth/telegram",
            json={"init_data": init_data, "ref_code": user.ref_code}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["referrer_id"] == user.id

    @pytest.mark.asyncio
    async def test_telegram_auth_invalid_data(self, client):
        """Test Telegram auth with invalid initData."""
        response = await client.post(
            "/auth/telegram",
            json={"init_data": "invalid_init_data"}
        )

        assert response.status_code == 401
        assert "Invalid Telegram initData" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_me_success(self, client, user, auth_headers, db_session):
        """Test getting current user profile."""
        response = await client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == user.telegram_id
        assert data["username"] == user.username
        assert "stats" in data
        assert data["stats"]["total_pets_owned"] == 0
        assert data["stats"]["total_claimed"] == "0"
        assert data["stats"]["total_ref_earned"] == "0"

    @pytest.mark.asyncio
    async def test_get_me_with_pets(self, client, user, auth_headers, user_pet, db_session):
        """Test getting profile includes pet count."""
        response = await client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["total_pets_owned"] == 1

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client):
        """Test getting profile without auth fails."""
        response = await client.get("/auth/me")

        assert response.status_code == 401  # Unauthorized when no token

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        """Test getting profile with invalid token fails."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
