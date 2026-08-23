"""Make schema dynamic: jenis_dok to string and add tahun_ajaran table

Revision ID: 004_make_schema_dynamic
Revises: 003_advanced_indexes
Create Date: 2026-06-16 14:15:00.000000
"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision: str = "004_make_schema_dynamic"
down_revision: Union[str, None] = "003_advanced_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Drop dependent constraints and indexes on dokumen ──────────────────
    op.execute("ALTER TABLE dokumen DROP CONSTRAINT IF EXISTS uq_dokumen_siswa_jenis_tahun_semester")
    op.execute("DROP INDEX IF EXISTS ix_dokumen_siswa_jenis")
    op.execute("DROP INDEX IF EXISTS ix_dokumen_jenis_dok")
    op.execute("DROP INDEX IF EXISTS ix_dokumen_active")

    # ── 2. Alter column jenis_dok from enum to varchar ────────────────────────
    op.execute("ALTER TABLE dokumen ALTER COLUMN jenis_dok TYPE VARCHAR(100) USING jenis_dok::text")

    # ── 3. Drop the old enum type ─────────────────────────────────────────────
    op.execute("DROP TYPE IF EXISTS jenis_dokumen_enum")

    # ── 4. Recreate constraints and indexes ───────────────────────────────────
    op.create_index("ix_dokumen_jenis_dok", "dokumen", ["jenis_dok"], unique=False)
    op.create_index("ix_dokumen_siswa_jenis", "dokumen", ["siswa_id", "jenis_dok"], unique=False)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_dokumen_active
        ON dokumen (siswa_id, jenis_dok, tahun_ajaran)
        WHERE status NOT IN ('archived', 'expired')
    """)
    op.create_unique_constraint(
        "uq_dokumen_siswa_jenis_tahun_semester",
        "dokumen",
        ["siswa_id", "jenis_dok", "tahun_ajaran", "semester"]
    )

    # ── 5. Create tahun_ajaran table ─────────────────────────────────────────
    op.create_table(
        "tahun_ajaran",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column("tahun", sa.String(length=9), nullable=False, unique=True),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tahun_ajaran_tahun", "tahun_ajaran", ["tahun"], unique=False)

    # ── 6. Seed categories table ──────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    categories_table = sa.table(
        "categories",
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("color", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        categories_table,
        [
            {"name": "ijazah", "description": "Ijazah Kelulusan", "color": "#6366f1", "created_at": now},
            {"name": "transkrip_nilai", "description": "Transkrip Nilai", "color": "#10b981", "created_at": now},
            {"name": "raport", "description": "Raport Akademik", "color": "#f59e0b", "created_at": now},
            {"name": "skhun", "description": "SKHUN", "color": "#ec4899", "created_at": now},
            {"name": "kartu_pelajar", "description": "Kartu Pelajar", "color": "#8b5cf6", "created_at": now},
            {"name": "surat_keterangan", "description": "Surat Keterangan", "color": "#3b82f6", "created_at": now},
            {"name": "sertifikat", "description": "Sertifikat", "color": "#06b6d4", "created_at": now},
            {"name": "piagam", "description": "Piagam", "color": "#14b8a6", "created_at": now},
            {"name": "sk_lulus", "description": "SK Lulus", "color": "#f43f5e", "created_at": now},
            {"name": "surat_aktif", "description": "Surat Aktif", "color": "#84cc16", "created_at": now},
            {"name": "rekomendasi", "description": "Rekomendasi", "color": "#eab308", "created_at": now},
            {"name": "lainnya", "description": "Dokumen Lainnya", "color": "#6b7280", "created_at": now},
        ]
    )

    # ── 7. Seed tahun_ajaran table ────────────────────────────────────────────
    tahun_ajaran_table = sa.table(
        "tahun_ajaran",
        sa.column("tahun", sa.String),
        sa.column("is_default", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        tahun_ajaran_table,
        [
            {"tahun": "2024/2025", "is_default": False, "created_at": now, "updated_at": now},
            {"tahun": "2025/2026", "is_default": True, "created_at": now, "updated_at": now},
        ]
    )


def downgrade() -> None:
    # 1. Drop tahun_ajaran table
    op.drop_table("tahun_ajaran")

    # 2. Recreate enum jenis_dokumen_enum
    jenis_dokumen_enum = sa.Enum(
        "ijazah", "transkrip_nilai", "raport", "skhun", "surat_keterangan", "sertifikat",
        "piagam", "sk_lulus", "kartu_pelajar", "surat_aktif", "rekomendasi", "lainnya",
        name="jenis_dokumen_enum"
    )
    jenis_dokumen_enum.create(op.get_bind(), checkfirst=True)

    # 3. Alter column back to enum
    op.execute("ALTER TABLE dokumen ALTER COLUMN jenis_dok TYPE jenis_dokumen_enum USING jenis_dok::jenis_dokumen_enum")

    # 4. Recreate unique constraints and indexes
    op.create_index("ix_dokumen_jenis_dok", "dokumen", ["jenis_dok"], unique=False)
    op.create_index("ix_dokumen_siswa_jenis", "dokumen", ["siswa_id", "jenis_dok"], unique=False)
    op.create_unique_constraint(
        "uq_dokumen_siswa_jenis_tahun_semester",
        "dokumen",
        ["siswa_id", "jenis_dok", "tahun_ajaran", "semester"]
    )
