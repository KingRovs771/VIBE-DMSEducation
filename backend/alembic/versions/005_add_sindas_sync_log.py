"""Add sindas_sync_log table for SINDAS integration audit trail

Revision ID: 005_add_sindas_sync_log
Revises: 004_make_schema_dynamic
Create Date: 2026-08-19 07:00:00.000000
"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_add_sindas_sync_log"
down_revision: Union[str, None] = "004_make_schema_dynamic"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Buat tabel sindas_sync_log dan enum types yang dibutuhkan."""

    # ── 1. Buat enum types ─────────────────────────────────────────────────────
    sindas_event_type = sa.Enum(
        "created", "updated", "deleted", "pull",
        name="sindas_event_type_enum",
    )
    sindas_sync_status = sa.Enum(
        "success", "failed", "skipped",
        name="sindas_sync_status_enum",
    )
    sindas_event_type.create(op.get_bind(), checkfirst=True)
    sindas_sync_status.create(op.get_bind(), checkfirst=True)

    # ── 2. Buat tabel sindas_sync_log ──────────────────────────────────────────
    op.create_table(
        "sindas_sync_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="Primary key"),
        sa.Column(
            "event_id",
            sa.String(100),
            nullable=True,
            unique=True,
            comment="ID unik event dari SINDAS (untuk idempotency)",
        ),
        sa.Column(
            "event_type",
            sindas_event_type,
            nullable=False,
            comment="Tipe event: created / updated / deleted / pull",
        ),
        sa.Column(
            "nis_sindas",
            sa.String(20),
            nullable=True,
            comment="NIS siswa dari payload SINDAS",
        ),
        sa.Column(
            "siswa_id",
            sa.Integer(),
            sa.ForeignKey("siswa.id", ondelete="SET NULL"),
            nullable=True,
            comment="FK ke tabel siswa",
        ),
        sa.Column(
            "sekolah_id",
            sa.Integer(),
            sa.ForeignKey("sekolah.id", ondelete="SET NULL"),
            nullable=True,
            comment="FK ke tabel sekolah",
        ),
        sa.Column(
            "payload_raw",
            sa.JSON(),
            nullable=True,
            comment="Payload JSON mentah dari SINDAS",
        ),
        sa.Column(
            "status",
            sindas_sync_status,
            nullable=False,
            comment="Hasil pemrosesan: success / failed / skipped",
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Pesan error jika status = failed",
        ),
        sa.Column(
            "changes_summary",
            sa.JSON(),
            nullable=True,
            comment="Ringkasan field yang berubah",
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            comment="Waktu event diproses oleh DMS (UTC)",
        ),
        sa.Column(
            "sindas_timestamp",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Waktu event terjadi di SINDAS (dari payload, UTC)",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Audit trail sinkronisasi data siswa dari SINDAS",
    )

    # ── 3. Buat indexes ────────────────────────────────────────────────────────
    op.create_index("ix_sindas_log_nis", "sindas_sync_log", ["nis_sindas"])
    op.create_index("ix_sindas_log_status", "sindas_sync_log", ["status"])
    op.create_index("ix_sindas_log_processed_at", "sindas_sync_log", ["processed_at"])
    op.create_index("ix_sindas_log_siswa_id", "sindas_sync_log", ["siswa_id"])
    op.create_index("ix_sindas_log_sekolah_id", "sindas_sync_log", ["sekolah_id"])


def downgrade() -> None:
    """Hapus tabel sindas_sync_log dan enum types."""

    # Hapus indexes
    op.drop_index("ix_sindas_log_sekolah_id", table_name="sindas_sync_log")
    op.drop_index("ix_sindas_log_siswa_id", table_name="sindas_sync_log")
    op.drop_index("ix_sindas_log_processed_at", table_name="sindas_sync_log")
    op.drop_index("ix_sindas_log_status", table_name="sindas_sync_log")
    op.drop_index("ix_sindas_log_nis", table_name="sindas_sync_log")

    # Hapus tabel
    op.drop_table("sindas_sync_log")

    # Hapus enum types
    sa.Enum(name="sindas_sync_status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sindas_event_type_enum").drop(op.get_bind(), checkfirst=True)
