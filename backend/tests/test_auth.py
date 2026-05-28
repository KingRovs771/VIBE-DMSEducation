"""
Test untuk Auth endpoints
"""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@sekolah.id",
                "username": "testuser",
                "full_name": "Test User",
                "password": "Password123",
                "role": "guru",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@sekolah.id"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@sekolah.id",
                "username": "loginuser",
                "full_name": "Login User",
                "password": "Password123",
                "role": "staf",
            },
        )
        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@sekolah.id", "password": "Password123"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexist@sekolah.id", "password": "wrongpass"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
