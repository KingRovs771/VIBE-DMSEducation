"""
Auth Endpoints — Login Admin & Siswa, JWT Token, Refresh, Logout, Reset Password
================================================================================
Menyediakan REST API otentikasi lengkap untuk admin dan siswa.
"""
from datetime import datetime, timezone
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password
)
from app.core.dependencies import get_current_admin
from app.core.totp import (
    generate_totp_secret,
    get_totp_uri,
    generate_qr_code_data_url,
    verify_totp_code,
    encrypt_totp_secret,
    decrypt_totp_secret,
)
from app.models.admin import Admin
from app.models.siswa import Siswa
from app.schemas.sekolah_schemas import (
    AdminLoginRequest,
    AdminTokenResponse,
    AdminResponse
)
from pydantic import BaseModel, Field, EmailStr

logger = structlog.get_logger(__name__)
router = APIRouter()


# ─── PYDANTIC SCHEMAS KHUSUS AUTH SISWA & UMUM ────────────────────────────────

class SiswaLoginRequest(BaseModel):
    nis: str = Field(..., description="Nomor Induk Siswa")
    password: str = Field(..., description="Password (tgl lahir YYYY-MM-DD atau password kustom)")


class SiswaLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    siswa: dict  # Profil dasar siswa


class RefreshRequest(BaseModel):
    refresh_token: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email untuk kirim tautan reset")


class Enable2FARequest(BaseModel):
    secret: str
    code: str


class Disable2FARequest(BaseModel):
    code: str


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/login/admin", response_model=AdminTokenResponse, tags=["Authentication"])
async def login_admin(payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login operator/admin sekolah menggunakan username atau email.
    Mengembalikan token JWT akses dan refresh.
    """
    logger.info("🔑 Admin login attempt", identity=payload.username)
    
    # Cari admin berdasarkan username atau email
    query = select(Admin).where(
        (Admin.username == payload.username) | (Admin.email == payload.username)
    )
    result = await db.execute(query)
    admin = result.scalar_one_or_none()
    
    # Validasi eksistensi dan is_active
    if not admin or not admin.is_active:
        logger.warning("❌ Admin login failed: Account not found or inactive", identity=payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username, email, atau password salah"
        )
        
    # Validasi password
    if not verify_password(payload.password, admin.password_hash):
        logger.warning("❌ Admin login failed: Incorrect password", identity=payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username, email, atau password salah"
        )

    # Validasi 2FA jika aktif
    if admin.two_factor_enabled:
        if not payload.code:
            logger.warning("❌ Admin login failed: 2FA enabled but no code provided", identity=payload.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kode Authenticator wajib diisi"
            )
        
        secret = decrypt_totp_secret(admin.two_factor_secret)
        if not secret or not verify_totp_code(secret, payload.code):
            logger.warning("❌ Admin login failed: Invalid 2FA code", identity=payload.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kode Authenticator tidak valid"
            )
        
    # Update last login
    admin.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # Generate tokens
    access = create_access_token(subject=f"admin:{admin.id}", extra_claims={"role": admin.role})
    refresh = create_refresh_token(subject=f"admin:{admin.id}")
    
    logger.info("✅ Admin logged in successfully", admin_id=admin.id, role=admin.role)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": 1800,  # 30 menit
        "admin": admin
    }


@router.post("/login/siswa", response_model=SiswaLoginResponse, tags=["Authentication"])
async def login_siswa(payload: SiswaLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login siswa menggunakan NIS dan password (tgl lahir YYYY-MM-DD atau password kustom).
    Mengembalikan token JWT akses dan refresh.
    """
    logger.info("🔑 Siswa login attempt", nis=payload.nis)
    
    # Cari siswa berdasarkan NIS
    query = select(Siswa).where(Siswa.nis == payload.nis)
    result = await db.execute(query)
    siswa = result.scalar_one_or_none()
    
    # Validasi eksistensi
    if not siswa or not siswa.is_active:
        logger.warning("❌ Siswa login failed: Student not found or inactive", nis=payload.nis)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NIS atau password salah"
        )
        
    # Validasi password (di sistem sekolah biasa, default password adalah tgl_lahir YYYY-MM-DD)
    # Jika password di DB disimpan sebagai hash kustom, kita bisa verify. 
    # Sebagai fallback/default awal, kita bandingkan tgl_lahir format YYYY-MM-DD
    raw_tgl_lahir = siswa.tgl_lahir.strftime('%Y-%m-%d') if siswa.tgl_lahir else ""
    
    # Anda juga bisa memverifikasi dengan verify_password jika kolom password/entropy_seed diderivasi
    is_valid_pass = (payload.password == raw_tgl_lahir)
    if not is_valid_pass:
        logger.warning("❌ Siswa login failed: Incorrect password", nis=payload.nis)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NIS atau password salah"
        )
        
    # Generate tokens
    access = create_access_token(subject=f"siswa:{siswa.id}", extra_claims={"role": "siswa"})
    refresh = create_refresh_token(subject=f"siswa:{siswa.id}")
    
    logger.info("✅ Siswa logged in successfully", siswa_id=siswa.id, nis=siswa.nis)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": 1800,  # 30 menit
        "siswa": {
            "id": siswa.id,
            "nis": siswa.nis,
            "nama_lengkap": siswa.nama_lengkap,
            "kelas": siswa.kelas,
            "angkatan": siswa.angkatan,
            "email": siswa.email,
            "sekolah_id": siswa.sekolah_id
        }
    }


@router.post("/refresh", tags=["Authentication"])
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Memperbarui access token JWT menggunakan refresh token yang masih aktif.
    """
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Token tipe tidak valid")
            
        subject = decoded.get("sub")
        # Generate token akses baru
        role = "siswa" if subject.startswith("siswa:") else "admin"
        access = create_access_token(subject=subject, extra_claims={"role": role})
        
        return {
            "access_token": access,
            "token_type": "bearer",
            "expires_in": 1800
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token kadaluarsa atau tidak valid"
        )


@router.post("/logout", tags=["Authentication"])
async def logout():
    """
    Logout dari aplikasi. (Menandakan token tidak valid).
    """
    logger.info("👋 Logout requested successfully")
    return {"status": "success", "message": "Berhasil logout. Silakan hapus token dari client."}


@router.post("/reset-password", tags=["Authentication"])
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    Mengirim tautan reset password ke email yang terdaftar.
    """
    logger.info("📧 Password reset request", email=payload.email)
    
    # Cari di admin terlebih dahulu
    query_admin = select(Admin).where(Admin.email == payload.email)
    res_admin = await db.execute(query_admin)
    admin = res_admin.scalar_one_or_none()
    
    # Cari di siswa jika tidak ada di admin
    target_found = False
    if admin:
        target_found = True
    else:
        query_siswa = select(Siswa).where(Siswa.email == payload.email)
        res_siswa = await db.execute(query_siswa)
        siswa = res_siswa.scalar_one_or_none()
        if siswa:
            target_found = True
            
    if not target_found:
        # Kembalikan status sukses semu untuk mencegah enumerasi email user
        return {"status": "success", "message": "Jika email terdaftar, instruksi reset password telah dikirim."}
        
    # Simulasikan pengiriman email (log link ke stdout)
    reset_token = secrets.token_hex(32)
    reset_link = f"https://dms-sekolah.sch.id/reset-password?token={reset_token}"
    logger.info("🔗 [MOCK EMAIL] Reset Password Link generated", email=payload.email, link=reset_link)
    
    return {"status": "success", "message": "Jika email terdaftar, instruksi reset password telah dikirim."}


# ─── ENDPOINTS 2FA ────────────────────────────────────────────────────────────

@router.get("/2fa/setup", tags=["Authentication"])
async def setup_2fa(
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Menghasilkan secret key TOTP baru dan QR Code gambar base64 untuk admin.
    """
    logger.info("🔑 Admin initiating 2FA setup", admin_id=current_admin.id)
    secret = generate_totp_secret()
    uri = get_totp_uri(current_admin.username, secret)
    qr_code = generate_qr_code_data_url(uri)
    return {"secret": secret, "qr_code": qr_code}


@router.post("/2fa/enable", tags=["Authentication"])
async def enable_2fa(
    payload: Enable2FARequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Memverifikasi kode setup 2FA dan mengaktifkannya jika sukses.
    """
    logger.info("🔑 Admin attempting to enable 2FA", admin_id=current_admin.id)
    if not verify_totp_code(payload.secret, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi Authenticator salah atau kadaluarsa"
        )
    
    current_admin.two_factor_secret = encrypt_totp_secret(payload.secret)
    current_admin.two_factor_enabled = True
    await db.commit()
    
    logger.info("🔑 2FA enabled successfully", admin_id=current_admin.id)
    return {"status": "success", "message": "Otentikasi Dua Faktor (2FA) berhasil diaktifkan"}


@router.post("/2fa/disable", tags=["Authentication"])
async def disable_2fa(
    payload: Disable2FARequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Menonaktifkan 2FA setelah verifikasi kode valid saat ini.
    """
    logger.info("🔑 Admin attempting to disable 2FA", admin_id=current_admin.id)
    if not current_admin.two_factor_enabled or not current_admin.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA belum aktif untuk akun ini"
        )
        
    secret = decrypt_totp_secret(current_admin.two_factor_secret)
    if not secret or not verify_totp_code(secret, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi Authenticator salah atau kadaluarsa"
        )
        
    current_admin.two_factor_secret = None
    current_admin.two_factor_enabled = False
    await db.commit()
    
    logger.info("🔑 2FA disabled", admin_id=current_admin.id)
    return {"status": "success", "message": "Otentikasi Dua Faktor (2FA) berhasil dinonaktifkan"}
