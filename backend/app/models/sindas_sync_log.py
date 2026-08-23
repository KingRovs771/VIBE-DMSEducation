"""
Model: SindasSyncLog
====================
Tabel audit trail untuk setiap event sinkronisasi yang diterima dari SINDAS.
Digunakan untuk debugging, monitoring, dan pemulihan data jika terjadi kegagalan.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime, Enum, ForeignKey, Index,
    Integer, String, Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SindasEventType(str, enum.Enum):
    """Tipe event yang dikirim oleh SINDAS via webhook."""
    CREATED = "created"    # Siswa baru ditambahkan di SINDAS
    UPDATED = "updated"    # Data siswa diubah di SINDAS
    DELETED = "deleted"    # Siswa dihapus / dinonaktifkan di SINDAS
    PULL    = "pull"       # Sinkronisasi aktif (DMS pull dari SINDAS)


class SindasSyncStatus(str, enum.Enum):
    """Status hasil pemrosesan event SINDAS."""
    SUCCESS = "success"    # Event berhasil diproses dan data tersinkronisasi
    FAILED  = "failed"     # Terjadi error saat memproses event
    SKIPPED = "skipped"    # Event diabaikan (duplikat / tidak relevan)


class SindasSyncLog(Base):
    """
    Tabel: sindas_sync_log
    Merekam setiap event webhook yang diterima dari SINDAS.

    Indexes:
        - ix_sindas_log_nis          (nis_sindas)     — cari by NIS
        - ix_sindas_log_status       (status)         — filter by status
        - ix_sindas_log_processed_at (processed_at)   — sort / filter by waktu
        - ix_sindas_log_siswa_id     (siswa_id)       — link ke record siswa
    """
    __tablename__ = "sindas_sync_log"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key",
    )

    # ── Identifikasi Event ────────────────────────────────────────────────────
    event_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="ID unik event dari SINDAS (untuk deteksi duplikat / idempotency)",
    )
    event_type: Mapped[SindasEventType] = mapped_column(
        Enum(
            SindasEventType,
            name="sindas_event_type_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        comment="Tipe event: created / updated / deleted / pull",
    )

    # ── Data Siswa yang Disinkronisasi ────────────────────────────────────────
    nis_sindas: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="NIS siswa dari payload SINDAS",
    )
    siswa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("siswa.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK ke tabel siswa (NULL jika insert gagal)",
    )
    sekolah_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sekolah.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK ke tabel sekolah terkait event ini",
    )

    # ── Payload & Hasil ───────────────────────────────────────────────────────
    payload_raw: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Payload JSON mentah dari SINDAS (untuk debugging)",
    )
    status: Mapped[SindasSyncStatus] = mapped_column(
        Enum(
            SindasSyncStatus,
            name="sindas_sync_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        comment="Hasil pemrosesan: success / failed / skipped",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Pesan error jika status = failed",
    )
    changes_summary: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Ringkasan field yang berubah (hanya untuk event updated)",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Waktu event diproses oleh DMS (UTC)",
    )
    sindas_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Waktu event terjadi di SINDAS (dari payload, UTC)",
    )

    # ── Index ─────────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_sindas_log_nis", "nis_sindas"),
        Index("ix_sindas_log_status", "status"),
        Index("ix_sindas_log_processed_at", "processed_at"),
        Index("ix_sindas_log_siswa_id", "siswa_id"),
        Index("ix_sindas_log_sekolah_id", "sekolah_id"),
        {"comment": "Audit trail sinkronisasi data siswa dari SINDAS"},
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    siswa: Mapped["Siswa | None"] = relationship("Siswa")  # noqa: F821
    sekolah: Mapped["Sekolah | None"] = relationship("Sekolah")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<SindasSyncLog id={self.id} event={self.event_type} "
            f"nis={self.nis_sindas!r} status={self.status}>"
        )
