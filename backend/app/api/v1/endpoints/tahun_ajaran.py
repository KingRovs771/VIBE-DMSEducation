"""
TahunAjaran endpoints
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_any_user
from app.models.tahun_ajaran import TahunAjaran
from app.schemas.sekolah_schemas import TahunAjaranCreate, TahunAjaranResponse

router = APIRouter()


@router.get("/", response_model=list[TahunAjaranResponse])
async def list_tahun_ajaran(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(get_current_any_user),
):
    """Mengambil semua daftar tahun ajaran."""
    result = await db.execute(select(TahunAjaran).order_by(TahunAjaran.tahun.desc()))
    return result.scalars().all()


@router.get("/default", response_model=TahunAjaranResponse)
async def get_default_tahun_ajaran(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(get_current_any_user),
):
    """Mengambil tahun ajaran default."""
    result = await db.execute(select(TahunAjaran).where(TahunAjaran.is_default == True))
    default_year = result.scalar_one_or_none()
    if not default_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tahun ajaran default tidak diset"
        )
    return default_year


@router.post("/", response_model=TahunAjaranResponse, status_code=201)
async def create_tahun_ajaran(
    payload: TahunAjaranCreate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(get_current_admin),
):
    """Membuat tahun ajaran baru (Hanya Admin)."""
    # Cek apakah tahun ajaran sudah terdaftar
    existing = await db.execute(select(TahunAjaran).where(TahunAjaran.tahun == payload.tahun))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tahun ajaran '{payload.tahun}' sudah terdaftar"
        )

    # Jika diset sebagai default, hilangkan status default pada yang lain
    if payload.is_default:
        await db.execute(update(TahunAjaran).values(is_default=False))

    new_year = TahunAjaran(**payload.model_dump())
    db.add(new_year)
    await db.commit()
    await db.refresh(new_year)
    return new_year


@router.put("/{id}/set-default", response_model=TahunAjaranResponse)
async def set_default_tahun_ajaran(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(get_current_admin),
):
    """Mengubah tahun ajaran tertentu menjadi default (Hanya Admin)."""
    # Cek apakah ID ada
    result = await db.execute(select(TahunAjaran).where(TahunAjaran.id == id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tahun ajaran tidak ditemukan"
        )

    # Set semua yang lain ke False
    await db.execute(update(TahunAjaran).values(is_default=False))
    
    # Set target ke True
    target.is_default = True
    await db.commit()
    await db.refresh(target)
    return target


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tahun_ajaran(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(get_current_admin),
):
    """Menghapus tahun ajaran (Hanya Admin)."""
    result = await db.execute(select(TahunAjaran).where(TahunAjaran.id == id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tahun ajaran tidak ditemukan"
        )

    await db.delete(target)
    await db.commit()
