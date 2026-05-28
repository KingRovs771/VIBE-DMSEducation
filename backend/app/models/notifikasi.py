"""
Model: Notifikasi
=================
Notifikasi in-app untuk siswa (dan admin).
Mendukung berbagai tipe notifikasi dengan data payload JSONB.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Index,
    Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipeNotifikasi(str, enum.Enum):
    """Kategori notifikasi."""
    DOKUMEN_APPROVED    = "dokumen_approved"
    DOKUMEN_REJECTED    = "dokumen_rejected"
    DOKUMEN_UPLOADED    = "dokumen_uploaded"
    DOKUMEN_EXPIRING    = "dokumen_expiring"    # Dokumen akan expire
    DOKUMEN_EXPIRED     = "dokumen_expired"
    PASSWORD_CHANGED    = "password_changed"
    LOGIN_NEW_DEVICE    = "login_new_device"
    PENGUMUMAN          = "pengumuman"          # Broadcast dari admin
    SISTEM              = "sistem"              # Notifikasi sistem


class Notifikasi(Base):
    """
    Tabel: notifikasi
    Notifikasi in-app untuk siswa.

    Indexes:
        - ix_notif_siswa_id       (siswa_id)              — notif per siswa
        - ix_notif_created_at     (created_at)             — timeline
        - ix_notif_is_read        (is_read)                — filter unread
        - ix_notif_siswa_unread   (siswa_id, is_read)     — compound: unread per siswa
        - ix_notif_tipe           (tipe)                   — filter by type
    """
    __tablename__ = "notifikasi"

    __table_args__ = (
        Index("ix_notif_siswa_id", "siswa_id"),
        Index("ix_notif_created_at", "created_at"),
        Index("ix_notif_is_read", "is_read"),
        Index("ix_notif_siswa_unread", "siswa_id", "is_read"),
        Index("ix_notif_tipe", "tipe"),
        {"comment": "Notifikasi in-app untuk siswa"},
    )

    # ── Primary Key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────────────
    siswa_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("siswa.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK ke tabel siswa — penerima notifikasi",
    )
    dokumen_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dokumen.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK ke dokumen yang terkait (opsional)",
    )

    # ── Konten ────────────────────────────────────────────────────────────────
    tipe: Mapped[TipeNotifikasi] = mapped_column(
        Enum(TipeNotifikasi, name="tipe_notifikasi_enum"),
        nullable=False,
        default=TipeNotifikasi.SISTEM,
        comment="Kategori notifikasi",
    )
    judul: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Judul notifikasi (maks 255 karakter)",
    )
    pesan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Isi pesan notifikasi",
    )
    payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Data tambahan dalam JSONB. Contoh: "
            '{"dokumen_id": 42, "jenis": "ijazah", "action_url": "/dokumen/42"}'
        ),
    )

    # ── Status ────────────────────────────────────────────────────────────────
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
        comment="Apakah notifikasi sudah dibaca",
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Waktu notifikasi dibaca (UTC)",
    )
    is_sent_email: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
        comment="Apakah sudah dikirim via email",
    )
    sent_email_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Waktu email dikirim (UTC)",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Waktu notifikasi dibuat (UTC)",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Waktu notifikasi kedaluwarsa (dihapus otomatis oleh cron)",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    siswa: Mapped["Siswa"] = relationship(  # noqa: F821
        "Siswa",
        back_populates="notifikasi",
    )
    dokumen: Mapped["Dokumen | None"] = relationship(  # noqa: F821
        "Dokumen",
        foreign_keys=[dokumen_id],
    )

    def __repr__(self) -> str:
        return (
            f"<Notifikasi id={self.id} siswa_id={self.siswa_id} "
            f"tipe={self.tipe} is_read={self.is_read}>"
        )
