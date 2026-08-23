"""
Model: TahunAjaran
==================
Data tahun ajaran akademik yang aktif dan dapat dipilih di sistem.
Mendukung pengaturan tahun ajaran default.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TahunAjaran(Base):
    """
    Tabel: tahun_ajaran
    Menyimpan data tahun ajaran dan status default-nya.
    """
    __tablename__ = "tahun_ajaran"

    __table_args__ = (
        CheckConstraint(
            "length(tahun) = 9 AND substr(tahun, 5, 1) = '/'",
            name="ck_tahun_ajaran_format",
        ),
        Index("ix_tahun_ajaran_tahun", "tahun"),
        {"comment": "Daftar tahun ajaran akademik"},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key",
    )
    tahun: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
        unique=True,
        comment="Format YYYY/YYYY (contoh: 2025/2026)",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
        comment="Apakah tahun ajaran ini menjadi default di frontend",
    )
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
        comment="Waktu diperbarui (UTC)",
    )

    def __repr__(self) -> str:
        return f"<TahunAjaran id={self.id} tahun={self.tahun!r} is_default={self.is_default}>"
