import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthRoutes:

    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "name": "name",
                "password": "supersecret",
                "role": "user",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "user@example.com"
        assert "id" in data

    async def test_register_conflict(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "conflict@example.com",
                "name": "name",
                "password": "supersecret",
                "role": "user",
            },
        )
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "conflict@example.com",
                "name": "name",
                "password": "supersecret",
                "role": "user",
            },
        )
        assert response.status_code == 409

    async def test_login_success(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "auth@example.com",
                "name": "name",
                "password": "supersecret",
                "role": "user",
            },
        )

        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "auth@example.com", "password": "supersecret"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_failure(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "wrong@example.com", "password": "wrongpass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    async def test_profile_access(self, client: AsyncClient, token_headers):
        response = await client.get("/api/v1/auth/me", headers=token_headers)
        assert response.status_code == 200
        assert "email" in response.json()

    async def test_profile_by_id_success(self, client: AsyncClient):
        register = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "byid@example.com",
                "name": "name",
                "password": "supersecret",
                "role": "user",
            },
        )
        user_id = register.json()["id"]

        response = await client.get(f"/api/v1/auth/profile/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    async def test_profile_by_id_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/profile/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "ID=9999 не найден"
