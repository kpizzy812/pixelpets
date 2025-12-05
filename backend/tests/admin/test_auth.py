"""Tests for admin authentication."""
import pytest

from app.models import AdminRole
from app.services.admin.auth import hash_password, verify_password


class TestAdminAuthService:
    """Tests for admin auth service functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_hash_uniqueness(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestAdminLoginRoute:
    """Tests for admin login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client, super_admin, db_session):
        """Test successful admin login."""
        response = await client.post(
            "/admin/login",
            json={"username": "superadmin", "password": "superpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["admin"]["username"] == "superadmin"
        assert data["admin"]["role"] == AdminRole.SUPER_ADMIN.value

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, super_admin, db_session):
        """Test login with wrong password."""
        response = await client.post(
            "/admin/login",
            json={"username": "superadmin", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_wrong_username(self, client, db_session):
        """Test login with non-existent username."""
        response = await client.post(
            "/admin/login",
            json={"username": "nonexistent", "password": "somepassword"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_admin(self, client, inactive_admin, db_session):
        """Test login with inactive admin account."""
        response = await client.post(
            "/admin/login",
            json={"username": "inactiveadmin", "password": "inactivepass"}
        )

        assert response.status_code == 401


class TestAdminMeRoute:
    """Tests for admin profile endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_success(self, client, super_admin, super_admin_headers, db_session):
        """Test getting current admin profile."""
        response = await client.get("/admin/me", headers=super_admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "superadmin"
        assert data["role"] == AdminRole.SUPER_ADMIN.value
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client, db_session):
        """Test getting profile without token."""
        response = await client.get("/admin/me")

        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client, db_session):
        """Test getting profile with invalid token."""
        response = await client.get(
            "/admin/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


class TestAdminCreateRoute:
    """Tests for admin creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_admin_by_super_admin(self, client, super_admin, super_admin_headers, db_session):
        """Test super admin can create new admins."""
        response = await client.post(
            "/admin/admins",
            headers=super_admin_headers,
            json={
                "username": "newadmin",
                "password": "newpass123",
                "email": "new@pixelpets.io",
                "role": AdminRole.ADMIN.value,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newadmin"
        assert data["role"] == AdminRole.ADMIN.value

    @pytest.mark.asyncio
    async def test_create_admin_by_regular_admin_forbidden(self, client, admin_user, admin_headers, db_session):
        """Test regular admin cannot create new admins."""
        response = await client.post(
            "/admin/admins",
            headers=admin_headers,
            json={
                "username": "newadmin",
                "password": "newpass123",
                "role": AdminRole.MODERATOR.value,
            }
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_admin_duplicate_username(self, client, super_admin, super_admin_headers, db_session):
        """Test cannot create admin with existing username."""
        response = await client.post(
            "/admin/admins",
            headers=super_admin_headers,
            json={
                "username": "superadmin",  # Already exists
                "password": "newpass123",
                "role": AdminRole.ADMIN.value,
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestAdminUpdateRoute:
    """Tests for admin update endpoint."""

    @pytest.mark.asyncio
    async def test_update_admin_role(self, client, super_admin, admin_user, super_admin_headers, db_session):
        """Test super admin can update admin role."""
        response = await client.patch(
            f"/admin/admins/{admin_user.id}",
            headers=super_admin_headers,
            json={"role": AdminRole.MODERATOR.value}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == AdminRole.MODERATOR.value

    @pytest.mark.asyncio
    async def test_cannot_change_own_role(self, client, super_admin, super_admin_headers, db_session):
        """Test admin cannot change their own role."""
        response = await client.patch(
            f"/admin/admins/{super_admin.id}",
            headers=super_admin_headers,
            json={"role": AdminRole.MODERATOR.value}
        )

        assert response.status_code == 400
        assert "Cannot change your own role" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_deactivate_admin(self, client, super_admin, admin_user, super_admin_headers, db_session):
        """Test deactivating an admin."""
        response = await client.patch(
            f"/admin/admins/{admin_user.id}",
            headers=super_admin_headers,
            json={"is_active": False}
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False
