"""
Test untuk Auth endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

from app.main import app
from app.models.sekolah import Sekolah
from app.models.admin import Admin, AdminRole
from app.core.security import hash_password
from app.core.database import get_db

@pytest.mark.asyncio
async def test_login_admin_success(db_session):
    # Override db dependency to use SQLite test database
    app.dependency_overrides[get_db] = lambda: db_session
    
    try:
        # 1. Create Sekolah prereq
        sekolah = Sekolah(
            nama="Sekolah Test Auth",
            kode="NPSNAUTH01",
            master_key_hash="mock_school_hash",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(sekolah)
        await db_session.flush()

        # 2. Create Admin (using unique credentials to avoid test database pollution)
        admin = Admin(
            username="auth_admin_1",
            email="auth_admin1@test.id",
            nama_lengkap="Admin Test 1",
            password_hash=hash_password("AdminPassword123!"),
            role=AdminRole.ADMIN,
            sekolah_id=sekolah.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(admin)
        await db_session.commit()

        # 3. Test Login Success
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login/admin",
                json={"username": "auth_admin_1", "password": "AdminPassword123!"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["admin"]["username"] == "auth_admin_1"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_admin_wrong_password(db_session):
    # Override db dependency to use SQLite test database
    app.dependency_overrides[get_db] = lambda: db_session
    
    try:
        # 1. Create Sekolah prereq
        sekolah = Sekolah(
            nama="Sekolah Test Auth 2",
            kode="NPSNAUTH02",
            master_key_hash="mock_school_hash_2",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(sekolah)
        await db_session.flush()

        # 2. Create Admin (using unique credentials to avoid test database pollution)
        admin = Admin(
            username="auth_admin_2",
            email="auth_admin2@test.id",
            nama_lengkap="Admin Test 2",
            password_hash=hash_password("AdminPassword123!"),
            role=AdminRole.ADMIN,
            sekolah_id=sekolah.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(admin)
        await db_session.commit()

        # 3. Test Login Fail
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login/admin",
                json={"username": "auth_admin_2", "password": "WrongPassword!"},
            )
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
