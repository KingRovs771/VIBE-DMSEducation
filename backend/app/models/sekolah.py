"""
Model: Sekolah
==============
Master data sekolah. Setiap sekolah memiliki master_key_hash yang digunakan
sebagai salt/seed utama untuk enkripsi dokumen siswa.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Index, Integer,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sekolah(Base):
    """
    Tabel: sekolah
    Menyimpan data master sekolah.
    """
    __tablename__ = "sekolah"

    __table_args__ = (
        UniqueConstraint("kode", name="uq_sekolah_kode"),
        Index("ix_sekolah_kode", "kode"),
        {"comment": "Master data sekolah"},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key",
    )
    nama: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nama lengkap sekolah",
    )
    kode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment="Kode sekolah (NPSN atau kode internal)",
    )
    alamat: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Alamat lengkap sekolah",
    )
    kota: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Kota/kabupaten",
    )
    provinsi: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Provinsi",
    )
    kode_pos: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Kode pos",
    )
    telepon: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Nomor telepon sekolah",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Email resmi sekolah",
    )
    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="URL website sekolah",
    )
    # ── Keamanan ─────────────────────────────────────────────────────────────
    master_key_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment=(
            "Hash dari master key sekolah (Argon2id/bcrypt). "
            "Digunakan sebagai komponen enkripsi dokumen siswa."
        ),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default="true",
        comment="Status aktif sekolah",
    )
    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Waktu dibuat (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Waktu terakhir diperbarui (UTC)",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    siswa: Mapped[list["Siswa"]] = relationship(  # noqa: F821
        "Siswa",
        back_populates="sekolah",
        cascade="all, delete-orphan",
    )
    admin: Mapped[list["Admin"]] = relationship(  # noqa: F821
        "Admin",
        back_populates="sekolah",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Sekolah id={self.id} kode={self.kode!r} nama={self.nama[:30]!r}>"
