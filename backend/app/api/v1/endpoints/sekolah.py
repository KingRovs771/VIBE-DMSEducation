import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.admin import Admin, AdminRole
from app.models.sekolah import Sekolah
from app.schemas.sekolah_schemas import SekolahResponse, SekolahUpdate

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/biodata", response_model=SekolahResponse)
async def get_sekolah_biodata(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil data profil lengkap sekolah untuk admin/staf sekolah & dinas.
    """
    logger.info("🏫 Admin/Dinas fetching school biodata", admin_id=current_admin.id)
    
    # Dinas Pendidikan bisa melihat semua sekolah (yang dibina, tetapi untuk biodata single, dinas mengambil sekolah miliknya/yang dicari)
    # Jika admin biasa/TU/operator/viewer, hanya bisa melihat sekolahnya sendiri
    sekolah_id = current_admin.sekolah_id
    if not sekolah_id:
        if current_admin.role == AdminRole.SUPER_ADMIN:
            # Super admin default ke sekolah ID 1 jika tidak dispesifikasikan, atau ambil sekolah pertama
            stmt = select(Sekolah).limit(1)
            res = await db.execute(stmt)
            sekolah = res.scalar_one_or_none()
            if not sekolah:
                raise HTTPException(status_code=404, detail="Sekolah belum dikonfigurasi")
            return sekolah
        else:
            raise HTTPException(status_code=403, detail="Akses ditolak. Akun Anda tidak terkait dengan sekolah manapun.")
            
    stmt = select(Sekolah).where(Sekolah.id == sekolah_id)
    res = await db.execute(stmt)
    sekolah = res.scalar_one_or_none()
    if not sekolah:
        raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")
        
    return sekolah


@router.put("/biodata", response_model=SekolahResponse)
async def update_sekolah_biodata(
    payload: SekolahUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Memperbarui profil biodata sekolah (Akses: Admin Sekolah / Super Admin).
    """
    logger.info("🏫 Admin updating school biodata", admin_id=current_admin.id)
    
    if current_admin.role not in (AdminRole.ADMIN, AdminRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin Sekolah atau Super Admin yang diijinkan memperbarui profil sekolah"
        )
        
    sekolah_id = current_admin.sekolah_id
    if not sekolah_id and current_admin.role == AdminRole.SUPER_ADMIN:
        # Super admin default ke sekolah pertama
        stmt = select(Sekolah).limit(1)
        res = await db.execute(stmt)
        sekolah = res.scalar_one_or_none()
    else:
        stmt = select(Sekolah).where(Sekolah.id == sekolah_id)
        res = await db.execute(stmt)
        sekolah = res.scalar_one_or_none()
        
    if not sekolah:
        raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(sekolah, key, val)
        
    await db.commit()
    await db.refresh(sekolah)
    
    logger.info("✅ School biodata updated successfully", sekolah_id=sekolah.id)
    return sekolah
