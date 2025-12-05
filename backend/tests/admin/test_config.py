"""Tests for admin config management."""
import pytest


class TestAdminConfigListRoute:
    """Tests for admin config list endpoint."""

    @pytest.mark.asyncio
    async def test_list_configs(self, client, super_admin_headers, system_configs, db_session):
        """Test listing system configs."""
        response = await client.get("/admin/config", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert any(c["key"] == "referral_percentages" for c in data)

    @pytest.mark.asyncio
    async def test_moderator_can_view_configs(self, client, moderator_headers, system_configs, db_session):
        """Test moderator can view configs."""
        response = await client.get("/admin/config", headers=moderator_headers)

        assert response.status_code == 200


class TestAdminConfigUpdateRoute:
    """Tests for admin config update endpoint."""

    @pytest.mark.asyncio
    async def test_update_config(self, client, super_admin_headers, system_configs, db_session):
        """Test updating a config value."""
        response = await client.put(
            "/admin/config/withdraw_min",
            headers=super_admin_headers,
            json={"value": 10, "description": "Updated minimum"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["value"] == 10
        assert data["description"] == "Updated minimum"

    @pytest.mark.asyncio
    async def test_create_new_config(self, client, super_admin_headers, db_session):
        """Test creating new config key."""
        response = await client.put(
            "/admin/config/new_setting",
            headers=super_admin_headers,
            json={"value": {"enabled": True}, "description": "New setting"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "new_setting"
        assert data["value"] == {"enabled": True}

    @pytest.mark.asyncio
    async def test_admin_cannot_update_config(self, client, admin_headers, system_configs, db_session):
        """Test regular admin cannot update configs."""
        response = await client.put(
            "/admin/config/withdraw_min",
            headers=admin_headers,
            json={"value": 10}
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_moderator_cannot_update_config(self, client, moderator_headers, system_configs, db_session):
        """Test moderator cannot update configs."""
        response = await client.put(
            "/admin/config/withdraw_min",
            headers=moderator_headers,
            json={"value": 10}
        )

        assert response.status_code == 403


class TestAdminReferralConfigRoute:
    """Tests for admin referral config endpoints."""

    @pytest.mark.asyncio
    async def test_get_referral_config(self, client, super_admin_headers, system_configs, db_session):
        """Test getting referral config."""
        response = await client.get("/admin/config/referrals", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "percentages" in data
        assert "unlock_thresholds" in data
        assert data["percentages"]["1"] == 20

    @pytest.mark.asyncio
    async def test_update_referral_percentages(self, client, super_admin_headers, system_configs, db_session):
        """Test updating referral percentages."""
        response = await client.put(
            "/admin/config/referrals",
            headers=super_admin_headers,
            json={"percentages": {"1": 25, "2": 20, "3": 15, "4": 10, "5": 5}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["percentages"]["1"] == 25

    @pytest.mark.asyncio
    async def test_update_referral_thresholds(self, client, super_admin_headers, system_configs, db_session):
        """Test updating referral unlock thresholds."""
        response = await client.put(
            "/admin/config/referrals",
            headers=super_admin_headers,
            json={"unlock_thresholds": {"1": 0, "2": 5, "3": 10, "4": 20, "5": 50}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["unlock_thresholds"]["2"] == 5

    @pytest.mark.asyncio
    async def test_admin_cannot_update_referral_config(self, client, admin_headers, system_configs, db_session):
        """Test regular admin cannot update referral config."""
        response = await client.put(
            "/admin/config/referrals",
            headers=admin_headers,
            json={"percentages": {"1": 30}}
        )

        assert response.status_code == 403
