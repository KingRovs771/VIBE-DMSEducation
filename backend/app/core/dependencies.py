"""
Dependencies — FastAPI Dependency Injection untuk Otentikasi & Otorisasi
======================================================================
Menyediakan helper otentikasi yang kuat untuk validasi JWT Admin dan Siswa.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.admin import Admin
from app.models.siswa import Siswa
from app.models.user import User

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    """Dependency: Memvalidasi token JWT dan mengembalikan objek Admin yang login."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        subject: str = payload.get("sub", "")
        if not subject or not subject.startswith("admin:"):
            raise credentials_exception
        admin_id = int(subject.split(":")[1])
    except Exception:
        raise credentials_exception

    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun admin tidak aktif atau tidak ditemukan"
        )
    return admin


async def get_current_siswa(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Siswa:
    """Dependency: Memvalidasi token JWT dan mengembalikan objek Siswa yang login."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        subject: str = payload.get("sub", "")
        if not subject or not subject.startswith("siswa:"):
            raise credentials_exception
        siswa_id = int(subject.split(":")[1])
    except Exception:
        raise credentials_exception

    result = await db.execute(select(Siswa).where(Siswa.id == siswa_id))
    siswa = result.scalar_one_or_none()
    if siswa is None or not siswa.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun siswa tidak aktif atau tidak ditemukan"
        )
    return siswa


async def get_super_admin(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    """Dependency: Memastikan admin yang login memiliki hak akses super_admin."""
    if current_admin.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Super Admin yang diijinkan mengakses modul ini"
        )
    return current_admin


async def get_tu_sekolah(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    """Dependency: Memastikan admin yang login memiliki hak akses tu_sekolah, admin, atau super_admin."""
    if current_admin.role not in ("tu_sekolah", "admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Tata Usaha (TU), Admin, atau Super Admin yang diijinkan"
        )
    return current_admin


async def get_dinas_pendidikan(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    """Dependency: Memastikan admin yang login memiliki hak akses dinas_pendidikan."""
    if current_admin.role != "dinas_pendidikan":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Dinas Pendidikan yang diijinkan mengakses modul ini"
        )
    return current_admin


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Legacy dependency: Mengembalikan User lama."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        subject: str = payload.get("sub", "")
        if subject.startswith("admin:"):
            user_id = int(subject.split(":")[1])
        elif subject.startswith("siswa:"):
            user_id = int(subject.split(":")[1])
        else:
            user_id = int(subject)
    except Exception:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Legacy dependency: Memastikan user lama adalah admin."""
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak"
        )
    return current_user


async def get_current_any_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Dependency: Memvalidasi token JWT dan mengembalikan Admin atau Siswa yang aktif."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        subject: str = payload.get("sub", "")
        if not subject:
            raise credentials_exception
        
        if subject.startswith("admin:"):
            admin_id = int(subject.split(":")[1])
            result = await db.execute(select(Admin).where(Admin.id == admin_id))
            admin = result.scalar_one_or_none()
            if admin and admin.is_active:
                return admin
        elif subject.startswith("siswa:"):
            siswa_id = int(subject.split(":")[1])
            result = await db.execute(select(Siswa).where(Siswa.id == siswa_id))
            siswa = result.scalar_one_or_none()
            if siswa and siswa.is_active:
                return siswa
    except Exception:
        raise credentials_exception
    raise credentials_exception
