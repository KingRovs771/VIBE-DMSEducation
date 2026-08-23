"""
Admin Siswa Endpoints — CRUD & Excel Bulk Import
===============================================
Menyediakan REST API pengelolaan profil siswa untuk admin sekolah.
"""
import secrets
import structlog
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.admin import Admin
from app.models.siswa import Siswa
from app.schemas.sekolah_schemas import SiswaResponse, SiswaCreate, SiswaUpdate, SiswaList

logger = structlog.get_logger(__name__)
router = APIRouter()


# ─── ENDPOINTS SISWA ADMIN ────────────────────────────────────────────────────

@router.get("", response_model=SiswaList, tags=["Admin Siswa"])
async def get_students(
    sekolah_id: Optional[int] = None,
    kelas: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=2000, description="Jumlah data per halaman"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar seluruh siswa sekolah dengan filter opsional dan paginasi.
    """
    logger.info("👨‍🎓 Admin fetching students list", admin_id=current_admin.id, page=page, limit=limit)
    
    from sqlalchemy import or_
    query = select(Siswa)
    count_query = select(func.count()).select_from(Siswa)
    
    if sekolah_id:
        query = query.where(Siswa.sekolah_id == sekolah_id)
        count_query = count_query.where(Siswa.sekolah_id == sekolah_id)
    if kelas:
        query = query.where(Siswa.kelas == kelas)
        count_query = count_query.where(Siswa.kelas == kelas)
    if search:
        search_term = f"%{search}%"
        search_filter = or_(
            Siswa.nama_lengkap.ilike(search_term),
            Siswa.nis.ilike(search_term),
            Siswa.nisn.ilike(search_term)
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    # Get total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    students = result.scalars().all()
    
    return {
        "items": students,
        "total": total,
        "page": page,
        "size": limit
    }


@router.get("/kelas", response_model=list[str], tags=["Admin Siswa"])
async def get_classes(
    sekolah_id: Optional[int] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar kelas unik yang ada pada data siswa.
    """
    query = select(Siswa.kelas).distinct().where(Siswa.kelas.is_not(None))
    if sekolah_id:
        query = query.where(Siswa.sekolah_id == sekolah_id)
        
    result = await db.execute(query)
    classes = result.scalars().all()
    # Hapus string kosong dan urutkan
    return sorted([c for c in classes if c.strip()])


@router.post("", response_model=SiswaResponse, status_code=201, tags=["Admin Siswa"])
async def create_student(
    payload: SiswaCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Menambahkan siswa baru ke sistem.
    Secara otomatis menghasilkan `entropy_seed` acak kriptografis sepanjang 32-karakter hex (16 bytes)
    untuk kebutuhan modul NeuralKeyGen.
    """
    logger.info("👨‍🎓 Admin creating student", admin_id=current_admin.id, nis=payload.nis)
    
    # 1. Cek duplikasi NIS
    query_nis = select(Siswa).where(Siswa.nis == payload.nis)
    res_nis = await db.execute(query_nis)
    if res_nis.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Siswa dengan NIS {payload.nis} sudah terdaftar di sistem"
        )
        
    # 2. Hasilkan entropy_seed acak (16 bytes = 32 hex chars)
    entropy_seed = secrets.token_hex(16)
    
    # 3. Simpan ke database
    new_student = Siswa(
        nis=payload.nis,
        nisn=payload.nisn,
        nama_lengkap=payload.nama_lengkap,
        tgl_lahir=payload.tgl_lahir,
        tempat_lahir=payload.tempat_lahir,
        jenis_kelamin=payload.jenis_kelamin,
        agama=payload.agama,
        alamat=payload.alamat,
        kelas=payload.kelas,
        jurusan=payload.jurusan,
        angkatan=payload.angkatan,
        tahun_lulus=payload.tahun_lulus,
        email=payload.email,
        telepon=payload.telepon,
        telepon_ortu=payload.telepon_ortu,
        nama_ortu=payload.nama_ortu,
        sekolah_id=payload.sekolah_id,
        entropy_seed=entropy_seed,
        is_active=True
    )
    
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    
    logger.info("✅ Student created successfully", siswa_id=new_student.id, nis=new_student.nis)
    return new_student


@router.get("/{id}", response_model=SiswaResponse, tags=["Admin Siswa"])
async def get_student_detail(
    id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil informasi profil lengkap siswa berdasarkan ID.
    """
    logger.info("👨‍🎓 Admin fetching student detail", admin_id=current_admin.id, siswa_id=id)
    
    query = select(Siswa).where(Siswa.id == id)
    result = await db.execute(query)
    siswa = result.scalar_one_or_none()
    
    if not siswa:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        
    return siswa


@router.put("/{id}", response_model=SiswaResponse, tags=["Admin Siswa"])
async def update_student(
    id: int,
    payload: SiswaUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Memperbarui profil informasi siswa.
    """
    logger.info("👨‍🎓 Admin updating student", admin_id=current_admin.id, siswa_id=id)
    
    query = select(Siswa).where(Siswa.id == id)
    result = await db.execute(query)
    siswa = result.scalar_one_or_none()
    
    if not siswa:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        
    # Update fields
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(siswa, key, value)
        
    await db.commit()
    await db.refresh(siswa)
    
    logger.info("✅ Student updated successfully", siswa_id=id)
    return siswa


@router.delete("/{id}", tags=["Admin Siswa"])
async def delete_student(
    id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Menghapus siswa dari sistem (soft-delete / non-aktifkan akun siswa).
    """
    logger.info("👨‍🎓 Admin deleting student", admin_id=current_admin.id, siswa_id=id)
    
    query = select(Siswa).where(Siswa.id == id)
    result = await db.execute(query)
    siswa = result.scalar_one_or_none()
    
    if not siswa:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        
    siswa.is_active = False
    await db.commit()
    
    logger.info("✅ Student deactivated successfully", siswa_id=id)
    return {"status": "success", "message": f"Akun Siswa ID {id} berhasil dinonaktifkan"}


@router.post("/import", tags=["Admin Siswa"])
async def import_students_via_excel(
    file: UploadFile = File(..., description="File Excel (.xlsx/.xls) daftar siswa baru"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Melakukan import massal (bulk import) data siswa baru via Excel.
    Secara otomatis menghasilkan `entropy_seed` unik untuk setiap baris siswa baru.
    """
    logger.info("📥 Admin importing students via Excel", admin_id=current_admin.id, filename=file.filename)
    
    # Validasi extension file
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Hanya mendukung berkas Excel (.xlsx atau .xls)")
        
    import openpyxl
    import io
    from datetime import datetime

    contents = await file.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file Excel: {str(e)}")
        
    ws = wb.active
    headers = [str(cell.value).strip().lower() if cell.value else "" for cell in ws[1]]
    
    if not headers or "nis" not in headers or "nama_lengkap" not in headers:
        raise HTTPException(status_code=400, detail="Format Excel tidak valid. Pastikan menggunakan template yang disediakan.")
        
    imported_count = 0
    total_processed = 0
    
    def parse_date(val):
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except ValueError:
                pass
        return None
        
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row): continue
        total_processed += 1
        
        row_dict = dict(zip(headers, row))
        nis = str(row_dict.get("nis", "")).strip()
        if not nis or nis == "None":
            continue
            
        nama = str(row_dict.get("nama_lengkap", "")).strip()
        kelas = str(row_dict.get("kelas", "")).strip()
        
        if not nama or nama == "None":
            nama = "Tanpa Nama"
            
        query_nis = select(Siswa).where(Siswa.nis == nis)
        res_nis = await db.execute(query_nis)
        if res_nis.scalar_one_or_none():
            continue
            
        entropy_seed = secrets.token_hex(16)
        
        angkatan_val = row_dict.get("angkatan")
        try:
            angkatan = int(angkatan_val) if angkatan_val and str(angkatan_val) != "None" else None
        except ValueError:
            angkatan = None
            
        def clean_val(val):
            s = str(val).strip()
            return None if not s or s == "None" else s
            
        new_student = Siswa(
            nis=nis,
            nisn=clean_val(row_dict.get("nisn")),
            nama_lengkap=nama,
            kelas=clean_val(row_dict.get("kelas")),
            angkatan=angkatan,
            jurusan=clean_val(row_dict.get("jurusan")),
            tgl_lahir=parse_date(row_dict.get("tgl_lahir")),
            tempat_lahir=clean_val(row_dict.get("tempat_lahir")),
            jenis_kelamin=clean_val(row_dict.get("jenis_kelamin")),
            agama=clean_val(row_dict.get("agama")),
            email=clean_val(row_dict.get("email")),
            telepon=clean_val(row_dict.get("telepon")),
            nama_ortu=clean_val(row_dict.get("nama_ortu")),
            telepon_ortu=clean_val(row_dict.get("telepon_ortu")),
            alamat=clean_val(row_dict.get("alamat")),
            sekolah_id=current_admin.sekolah_id or 1,
            entropy_seed=entropy_seed,
            is_active=True
        )
        db.add(new_student)
        imported_count += 1
        
    await db.commit()
    logger.info("✅ Bulk import completed successfully", total_imported=imported_count)
    return {
        "status": "success",
        "message": f"Berhasil mengimpor {imported_count} data siswa baru dari Excel.",
        "details": {"total_processed": total_processed, "total_imported": imported_count}
    }
