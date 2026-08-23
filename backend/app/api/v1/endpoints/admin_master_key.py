from datetime import datetime, timezone
import os
import shutil
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, AsyncSessionLocal
from app.core.dependencies import get_super_admin
from app.core.crypto import generate_master_key, unwrap_student_key, wrap_student_key
from app.models.admin import Admin
from app.models.sekolah import Sekolah
from app.models.dokumen import Dokumen
from app.models.siswa import Siswa
from app.models.audit_log import AuditLog

router = APIRouter()

SECRETS_DIR = "/app/.secrets"

class RotateKeyRequest(BaseModel):
    confirm: str

class MasterKeyStatusResponse(BaseModel):
    mk_version: int
    active_public_key: str | None
    status: str
    total_dokumen: int


@router.get("/status", response_model=MasterKeyStatusResponse)
async def get_master_key_status(
    current_admin: Admin = Depends(get_super_admin),
    db: AsyncSession = Depends(get_db)
):
    sekolah = await db.scalar(select(Sekolah).where(Sekolah.id == current_admin.sekolah_id))
    if not sekolah:
        raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")

    # Hitung total dokumen
    stmt = select(func.count(Dokumen.id)).join(Siswa).where(Siswa.sekolah_id == current_admin.sekolah_id)
    total_dokumen = await db.scalar(stmt)

    status_str = "active" if sekolah.mk_version > 0 else "not_setup"

    return MasterKeyStatusResponse(
        mk_version=sekolah.mk_version,
        active_public_key=sekolah.public_key_pem,
        status=status_str,
        total_dokumen=total_dokumen or 0,
    )


async def process_key_rotation(
    sekolah_id: int, 
    old_version: int, 
    new_version: int, 
    old_private_key_pem: str | None, 
    new_public_key_pem: str, 
    admin_id: int
):
    """
    Tugas background untuk melakukan re-wrapping kunci dokumen.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(Dokumen).join(Siswa).where(Siswa.sekolah_id == sekolah_id)
            result = await db.execute(stmt)
            dokumen_list = result.scalars().all()
            
            success_count = 0
            error_count = 0

            for doc in dokumen_list:
                try:
                    student_key = None
                    if old_private_key_pem and doc.key_wrapped:
                        student_key = unwrap_student_key(doc.key_wrapped, old_private_key_pem)
                    
                    if student_key:
                        new_wrapped_key = wrap_student_key(student_key, new_public_key_pem)
                        doc.key_wrapped = new_wrapped_key
                        doc.mk_version = new_version
                        success_count += 1
                except Exception as e:
                    print(f"[Rotasi] Gagal re-wrap dokumen ID {doc.id}: {e}")
                    error_count += 1
                    
            # Catat di Audit Log
            audit = AuditLog(
                admin_id=admin_id,
                action="ROTASI_KUNCI",
                resource="MASTER_KEY",
                resource_id=str(sekolah_id),
                details={
                    "old_version": old_version,
                    "new_version": new_version,
                    "dokumen_berhasil": success_count,
                    "dokumen_gagal": error_count,
                },
                ip_address="127.0.0.1"
            )
            db.add(audit)
            await db.commit()
    except Exception as ex:
        print(f"[Rotasi] Fatal error: {ex}")


@router.post("/rotate")
async def rotate_master_key(
    req: RotateKeyRequest,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_super_admin),
    db: AsyncSession = Depends(get_db)
):
    if req.confirm != "ROTASI KUNCI MASTER":
        raise HTTPException(status_code=400, detail="Konfirmasi rotasi tidak valid")
        
    sekolah = await db.scalar(select(Sekolah).where(Sekolah.id == current_admin.sekolah_id))
    if not sekolah:
        raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")

    os.makedirs(SECRETS_DIR, exist_ok=True)
    
    old_version = sekolah.mk_version
    new_version = old_version + 1
    
    old_private_key_pem = None
    if old_version > 0:
        old_key_path = os.path.join(SECRETS_DIR, f"master_key_v{old_version}.pem")
        if os.path.exists(old_key_path):
            with open(old_key_path, "r") as f:
                old_private_key_pem = f.read()
        else:
            raise HTTPException(status_code=500, detail="Private key lama tidak ditemukan. Tidak dapat melakukan rotasi.")
            
    # Generate kunci baru
    new_public_pem, new_private_pem = generate_master_key()
    
    # Simpan kunci baru
    new_key_path = os.path.join(SECRETS_DIR, f"master_key_v{new_version}.pem")
    with open(new_key_path, "w") as f:
        f.write(new_private_pem)
        
    # Update DB (Public Key)
    sekolah.public_key_pem = new_public_pem
    sekolah.mk_version = new_version
    
    # Audit log (awal rotasi)
    audit = AuditLog(
        admin_id=current_admin.id,
        action="INIT_ROTASI_KUNCI",
        resource="MASTER_KEY",
        resource_id=str(sekolah.id),
        details={"new_version": new_version},
        ip_address="127.0.0.1"
    )
    db.add(audit)
    
    await db.commit()
    
    # Cek jumlah dokumen untuk re-wrapping
    stmt = select(func.count(Dokumen.id)).join(Siswa).where(Siswa.sekolah_id == current_admin.sekolah_id)
    total_dokumen = await db.scalar(stmt)
    
    if total_dokumen and total_dokumen > 0:
        background_tasks.add_task(
            process_key_rotation,
            sekolah.id, 
            old_version, 
            new_version, 
            old_private_key_pem, 
            new_public_pem, 
            current_admin.id
        )

    return {"message": "Master Key berhasil dibuat/dirotasi", "version": new_version}
