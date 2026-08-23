"""
Schemas: SINDAS Integration
============================
Pydantic schemas untuk payload webhook SINDAS dan response monitoring.

Catatan: Struktur payload diasumsikan berdasarkan standar umum API SINDAS.
Sesuaikan field di SindasSiswaData jika format SINDAS berbeda.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ══════════════════════════════════════════════════════════════
#  INBOUND — Payload dari SINDAS ke DMS (Webhook)
# ══════════════════════════════════════════════════════════════

class SindasSiswaData(BaseModel):
    """
    Data siswa yang dikirim SINDAS dalam payload webhook.
    Field disesuaikan dengan struktur umum API SINDAS / DAPODIK.
    """
    nis: str = Field(..., description="Nomor Induk Siswa (unik per sekolah)")
    nisn: Optional[str] = Field(None, description="Nomor Induk Siswa Nasional (10 digit)")
    nama: str = Field(..., description="Nama lengkap siswa")
    kelas: Optional[str] = Field(None, description="Kelas aktif (X, XI, XII, dst.)")
    jurusan: Optional[str] = Field(None, description="Jurusan / program studi")
    angkatan: Optional[int] = Field(None, description="Tahun angkatan masuk")
    tahun_lulus: Optional[int] = Field(None, description="Tahun kelulusan")
    jenis_kelamin: Optional[str] = Field(None, description="L = Laki-laki, P = Perempuan")
    tgl_lahir: Optional[date] = Field(None, description="Tanggal lahir")
    tempat_lahir: Optional[str] = Field(None, description="Tempat lahir")
    agama: Optional[str] = Field(None, description="Agama siswa")
    alamat: Optional[str] = Field(None, description="Alamat lengkap")
    email: Optional[str] = Field(None, description="Email siswa")
    telepon: Optional[str] = Field(None, description="No. telepon siswa")
    telepon_ortu: Optional[str] = Field(None, description="No. telepon orang tua")
    nama_ortu: Optional[str] = Field(None, description="Nama orang tua / wali")
    sekolah_id: Optional[int] = Field(None, description="ID sekolah di DMS (opsional)")
    npsn: Optional[str] = Field(None, description="NPSN sekolah (alternatif mapping sekolah_id)")

    @field_validator("nis")
    @classmethod
    def nis_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("NIS tidak boleh kosong")
        return v.strip()

    @field_validator("jenis_kelamin")
    @classmethod
    def validate_jenis_kelamin(cls, v: Optional[str]) -> Optional[str]:
        if v and v.upper() not in ("L", "P"):
            return None  # Abaikan nilai yang tidak valid
        return v.upper() if v else None


class SindasWebhookPayload(BaseModel):
    """
    Payload lengkap yang dikirim SINDAS ke endpoint `/sindas/webhook`.

    Format payload yang diharapkan:
    {
        "event_id": "evt_abc123",
        "event_type": "created",
        "timestamp": "2026-08-19T07:00:00Z",
        "source": "SINDAS",
        "data": { ...SindasSiswaData... }
    }
    """
    event_id: Optional[str] = Field(
        None,
        description="ID unik event dari SINDAS untuk idempotency check"
    )
    event_type: str = Field(
        ...,
        description="Tipe event: created | updated | deleted"
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="Waktu event terjadi di SINDAS (ISO 8601)"
    )
    source: Optional[str] = Field(
        "SINDAS",
        description="Sumber event (identifikasi pengirim)"
    )
    data: SindasSiswaData = Field(
        ...,
        description="Data siswa dalam event ini"
    )

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        allowed = {"created", "updated", "deleted"}
        if v.lower() not in allowed:
            raise ValueError(f"event_type harus salah satu dari: {allowed}")
        return v.lower()


# ══════════════════════════════════════════════════════════════
#  OUTBOUND — Response dari DMS ke klien
# ══════════════════════════════════════════════════════════════

class SindasWebhookResponse(BaseModel):
    """Response standar setelah DMS memproses webhook dari SINDAS."""
    status: str = Field(..., description="'accepted' atau 'error'")
    message: str
    log_id: Optional[int] = Field(None, description="ID di tabel sindas_sync_log")
    siswa_id: Optional[int] = Field(None, description="ID siswa yang dibuat/diupdate")


class SindasSyncLogResponse(BaseModel):
    """Schema response untuk setiap baris di tabel sindas_sync_log."""
    id: int
    event_id: Optional[str]
    event_type: str
    nis_sindas: Optional[str]
    siswa_id: Optional[int]
    sekolah_id: Optional[int]
    status: str
    error_message: Optional[str]
    changes_summary: Optional[dict[str, Any]]
    processed_at: datetime
    sindas_timestamp: Optional[datetime]

    model_config = {"from_attributes": True}


class SindasSyncStatusResponse(BaseModel):
    """Statistik sinkronisasi SINDAS untuk dashboard monitoring."""
    sindas_enabled: bool
    sindas_api_configured: bool
    today_total: int = Field(..., description="Total event diproses hari ini")
    today_success: int = Field(..., description="Total event berhasil hari ini")
    today_failed: int = Field(..., description="Total event gagal hari ini")
    today_skipped: int = Field(..., description="Total event dilewati hari ini")
    last_sync_at: Optional[datetime] = Field(None, description="Waktu sync terakhir berhasil")
    last_sync_nis: Optional[str] = Field(None, description="NIS terakhir yang disinkronisasi")
    total_all_time: int = Field(..., description="Total event sepanjang waktu")


class SindasPullRequest(BaseModel):
    """Body request untuk trigger pull manual dari SINDAS."""
    sekolah_id: Optional[int] = Field(
        None,
        description="ID sekolah yang ingin di-pull. Jika null, pull semua sekolah."
    )
    kelas: Optional[str] = Field(
        None,
        description="Filter kelas tertentu (opsional)"
    )
    limit: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Jumlah maksimum record yang di-pull dalam satu request"
    )


class SindasPullResponse(BaseModel):
    """Response setelah proses pull data manual dari SINDAS."""
    status: str
    message: str
    total_fetched: int = Field(..., description="Jumlah data yang diambil dari SINDAS")
    total_created: int = Field(..., description="Jumlah siswa baru yang dibuat di DMS")
    total_updated: int = Field(..., description="Jumlah siswa yang diperbarui")
    total_skipped: int = Field(..., description="Jumlah data yang dilewati")
    total_failed: int = Field(..., description="Jumlah data yang gagal diproses")
    duration_ms: Optional[float] = Field(None, description="Durasi proses dalam milidetik")
