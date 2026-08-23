"""
Model: AuditLog
===============
Audit trail lengkap untuk setiap aksi yang terjadi di sistem DMS.
Tidak ada record yang boleh dihapus — ini adalah immutable log.

Prinsip:
    - INSERT only, tidak ada UPDATE/DELETE pada tabel ini
    - user_type membedakan apakah aktor adalah admin atau siswa
    - status mencatat apakah aksi berhasil atau gagal
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime, Enum, ForeignKey, Index, Integer,
    String, Text, JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserType(str, enum.Enum):
    """Tipe aktor yang melakukan aksi."""
    ADMIN   = "admin"
    SISWA   = "siswa"
    SYSTEM  = "system"   # Proses otomatis (cron, background job)
    GUEST   = "guest"    # Akses tanpa autentikasi


class AuditAction(str, enum.Enum):
    """Jenis aksi yang dicatat."""
    # Auth
    LOGIN               = "login"
    LOGOUT              = "logout"
    LOGIN_FAILED        = "login_failed"
    TOKEN_REFRESH       = "token_refresh"
    PASSWORD_CHANGE     = "password_change"
    # Dokumen
    DOKUMEN_UPLOAD      = "dokumen_upload"
    DOKUMEN_VIEW        = "dokumen_view"
    DOKUMEN_DOWNLOAD    = "dokumen_download"
    DOKUMEN_UPDATE      = "dokumen_update"
    DOKUMEN_DELETE      = "dokumen_delete"
    DOKUMEN_APPROVE     = "dokumen_approve"
    DOKUMEN_REJECT      = "dokumen_reject"
    DOKUMEN_SHARE       = "dokumen_share"
    # Siswa
    SISWA_CREATE        = "siswa_create"
    SISWA_UPDATE        = "siswa_update"
    SISWA_DELETE        = "siswa_delete"
    SISWA_VIEW          = "siswa_view"
    # Admin
    ADMIN_CREATE        = "admin_create"
    ADMIN_UPDATE        = "admin_update"
    ADMIN_DEACTIVATE    = "admin_deactivate"
    # System
    KEY_ROTATION        = "key_rotation"
    BACKUP_CREATED      = "backup_created"
    SYSTEM_ERROR        = "system_error"


class AuditStatus(str, enum.Enum):
    """Hasil dari aksi yang dicatat."""
    SUCCESS = "success"
    FAILED  = "failed"
    ERROR   = "error"
    BLOCKED = "blocked"   # Ditolak oleh firewall/rate-limiter


class AuditLog(Base):
    """
    Tabel: audit_log
    Immutable audit trail — hanya INSERT, tidak ada UPDATE/DELETE.

    Indexes:
        - ix_audit_user_id       (user_id)     — riwayat per user
        - ix_audit_created_at    (created_at)  — timeline query
        - ix_audit_dokumen_id    (dokumen_id)  — history per dokumen
        - ix_audit_action        (action)      — filter by jenis aksi
        - ix_audit_status        (status)      — filter sukses/gagal
        - ix_audit_ip            (ip_address)  — investigasi by IP
        - ix_audit_user_action   (user_id, action)  — compound
    """
    __tablename__ = "audit_log"

    __table_args__ = (
        Index("ix_audit_user_id", "user_id"),
        Index("ix_audit_created_at", "created_at"),
        Index("ix_audit_dokumen_id", "dokumen_id"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_status", "status"),
        Index("ix_audit_ip_address", "ip_address"),
        Index("ix_audit_user_action", "user_id", "action"),
        Index("ix_audit_user_type", "user_type"),
        {"comment": "Immutable audit trail — INSERT ONLY"},
    )

    # ── Primary Key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key",
    )

    # ── Aktor ─────────────────────────────────────────────────────────────────
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("admin.id", ondelete="SET NULL"),
        nullable=True,
        comment=(
            "FK ke tabel admin (jika user_type = admin). "
            "NULL untuk aksi sistem atau guest."
        ),
    )
    siswa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("siswa.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK ke tabel siswa (jika user_type = siswa)",
    )
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType, name="user_type_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        comment="Tipe aktor: admin | siswa | system | guest",
    )

    # ── Aksi ──────────────────────────────────────────────────────────────────
    action: Mapped[AuditAction | str] = mapped_column(
        String(100),
        nullable=False,
        comment="Jenis aksi yang dilakukan (menggunakan AuditAction enum)",
    )
    dokumen_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dokumen.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK ke dokumen yang terlibat (jika ada)",
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipe resource yang diakses: dokumen | siswa | admin | sekolah",
    )
    resource_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="ID resource yang diakses",
    )

    # ── Konteks Request ───────────────────────────────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address aktor (IPv4/IPv6)",
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User-Agent string dari HTTP request",
    )
    request_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="UUID request (untuk korelasi log)",
    )
    endpoint: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Endpoint HTTP yang diakses (e.g. /api/v1/dokumen/upload)",
    )
    http_method: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="HTTP method: GET | POST | PUT | PATCH | DELETE",
    )

    # ── Hasil ─────────────────────────────────────────────────────────────────
    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus, name="audit_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=AuditStatus.SUCCESS,
        comment="Hasil aksi: success | failed | error | blocked",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Pesan error jika status = failed/error",
    )
    detail: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
        comment=(
            "Detail tambahan dalam JSONB. Contoh: "
            '{"old_status": "draft", "new_status": "approved", "file_size": 1024}'
        ),
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Durasi request dalam milidetik (untuk performance monitoring)",
    )

    # ── Timestamp ─────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Waktu aksi terjadi (UTC, immutable)",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    admin: Mapped["Admin | None"] = relationship(  # noqa: F821
        "Admin",
        foreign_keys=[user_id],
        back_populates="audit_logs",
    )
    siswa: Mapped["Siswa | None"] = relationship(  # noqa: F821
        "Siswa",
        foreign_keys=[siswa_id],
    )
    dokumen: Mapped["Dokumen | None"] = relationship(  # noqa: F821
        "Dokumen",
        back_populates="audit_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} action={self.action} "
            f"user_id={self.user_id} status={self.status}>"
        )
