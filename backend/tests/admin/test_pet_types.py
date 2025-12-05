"""Tests for admin pet types management."""
import pytest
from decimal import Decimal

from sqlalchemy import select
from app.models import PetType


class TestAdminPetTypesListRoute:
    """Tests for admin pet types list endpoint."""

    @pytest.mark.asyncio
    async def test_list_pet_types(self, client, super_admin_headers, pet_types, db_session):
        """Test listing pet types."""
        response = await client.get("/admin/pet-types", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # We have 4 pet types in fixture (1 inactive)

    @pytest.mark.asyncio
    async def test_list_pet_types_includes_inactive(self, client, super_admin_headers, pet_types, db_session):
        """Test listing includes inactive pet types."""
        response = await client.get(
            "/admin/pet-types",
            params={"include_inactive": True},
            headers=super_admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert any(pt["is_active"] is False for pt in data)

    @pytest.mark.asyncio
    async def test_moderator_can_view_pet_types(self, client, moderator_headers, pet_types, db_session):
        """Test moderator can view pet types."""
        response = await client.get("/admin/pet-types", headers=moderator_headers)

        assert response.status_code == 200


class TestAdminPetTypesCreateRoute:
    """Tests for admin pet types create endpoint."""

    @pytest.mark.asyncio
    async def test_create_pet_type(self, client, admin_headers, db_session):
        """Test creating a new pet type."""
        response = await client.post(
            "/admin/pet-types",
            headers=admin_headers,
            json={
                "name": "New Pet",
                "emoji": "🆕",
                "base_price": "75.00",
                "daily_rate": "0.018",
                "roi_cap_multiplier": "1.65",
                "level_prices": {"BABY": 75, "ADULT": 300, "MYTHIC": 750},
                "is_active": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Pet"
        assert data["emoji"] == "🆕"
        assert Decimal(data["base_price"]) == Decimal("75")

    @pytest.mark.asyncio
    async def test_create_pet_type_validates_rate(self, client, admin_headers, db_session):
        """Test validation of daily rate (must be <= 1)."""
        response = await client.post(
            "/admin/pet-types",
            headers=admin_headers,
            json={
                "name": "Invalid Pet",
                "base_price": "50.00",
                "daily_rate": "1.5",  # Invalid: > 1
                "roi_cap_multiplier": "1.5",
                "level_prices": {"BABY": 50}
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_moderator_cannot_create_pet_type(self, client, moderator_headers, db_session):
        """Test moderator cannot create pet types."""
        response = await client.post(
            "/admin/pet-types",
            headers=moderator_headers,
            json={
                "name": "Test",
                "base_price": "50.00",
                "daily_rate": "0.01",
                "roi_cap_multiplier": "1.5",
                "level_prices": {"BABY": 50}
            }
        )

        assert response.status_code == 403


class TestAdminPetTypesUpdateRoute:
    """Tests for admin pet types update endpoint."""

    @pytest.mark.asyncio
    async def test_update_pet_type(self, client, admin_headers, pet_types, db_session):
        """Test updating a pet type."""
        pet_type = pet_types[0]

        response = await client.patch(
            f"/admin/pet-types/{pet_type.id}",
            headers=admin_headers,
            json={"name": "Updated Slime", "daily_rate": "0.015"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Slime"
        assert Decimal(data["daily_rate"]) == Decimal("0.015")

    @pytest.mark.asyncio
    async def test_deactivate_pet_type(self, client, admin_headers, pet_types, db_session):
        """Test deactivating a pet type."""
        pet_type = pet_types[0]

        response = await client.patch(
            f"/admin/pet-types/{pet_type.id}",
            headers=admin_headers,
            json={"is_active": False}
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_nonexistent_pet_type(self, client, admin_headers, db_session):
        """Test updating non-existent pet type."""
        response = await client.patch(
            "/admin/pet-types/99999",
            headers=admin_headers,
            json={"name": "Test"}
        )

        assert response.status_code == 404


class TestAdminPetTypesDeleteRoute:
    """Tests for admin pet types delete endpoint."""

    @pytest.mark.asyncio
    async def test_soft_delete_pet_type(self, client, admin_headers, pet_types, db_session):
        """Test soft deleting a pet type."""
        pet_type = pet_types[0]

        response = await client.delete(
            f"/admin/pet-types/{pet_type.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        assert response.json()["deleted"] == pet_type.id

        # Verify soft deleted
        await db_session.refresh(pet_type)
        assert pet_type.is_active is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_pet_type(self, client, admin_headers, db_session):
        """Test deleting non-existent pet type."""
        response = await client.delete(
            "/admin/pet-types/99999",
            headers=admin_headers
        )

        assert response.status_code == 404
