"""Indexes lanjutan — partial indexes dan optimasi PostgreSQL

Menambahkan:
  1. Partial index untuk dokumen yang belum disetujui (WHERE status = 'pending_review')
  2. Partial index untuk notifikasi yang belum dibaca (WHERE is_read = false)
  3. GIN index pada JSONB columns untuk query JSON
  4. Index untuk full-text search sederhana
  5. Trigger otomatis updated_at

Revision ID: 003_advanced_indexes
Revises: 002_seed_data
Create Date: 2024-01-01 02:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_advanced_indexes"
down_revision: Union[str, None] = "002_seed_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ── 1. Partial index — dokumen pending review ──────────────────────────────
    # Hanya index record yang perlu ditinjau admin (jauh lebih kecil dari full index)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_dokumen_pending
        ON dokumen (created_at, siswa_id)
        WHERE status = 'pending_review'
    """)

    # ── 2. Partial index — notifikasi belum dibaca ─────────────────────────────
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_notif_unread_partial
        ON notifikasi (siswa_id, created_at)
        WHERE is_read = false
    """)

    # ── 3. Partial index — admin aktif ────────────────────────────────────────
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_admin_active
        ON admin (sekolah_id, role)
        WHERE is_active = true
    """)

    # ── 4. Partial index — dokumen aktif (tidak expired/archived) ─────────────
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_dokumen_active
        ON dokumen (siswa_id, jenis_dok, tahun_ajaran)
        WHERE status NOT IN ('archived', 'expired')
    """)

    # ── 5. GIN index pada metadata_json (JSONB) ────────────────────────────────
    # Mendukung query seperti: WHERE metadata_json @> '{"predikat": "A"}'
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_dokumen_metadata_gin
        ON dokumen USING GIN (metadata_json)
        WHERE metadata_json IS NOT NULL
    """)

    # ── 6. GIN index pada detail (JSONB) di audit_log ─────────────────────────
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_audit_detail_gin
        ON audit_log USING GIN (detail)
        WHERE detail IS NOT NULL
    """)

    # ── 7. GIN index pada payload (JSONB) di notifikasi ──────────────────────
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_notif_payload_gin
        ON notifikasi USING GIN (payload)
        WHERE payload IS NOT NULL
    """)

    # ── 8. Trigger: auto-update updated_at ────────────────────────────────────
    # Fungsi trigger yang digunakan semua tabel
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW() AT TIME ZONE 'UTC';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    # Trigger untuk setiap tabel yang punya updated_at
    for tabel in ("sekolah", "admin", "siswa", "dokumen"):
        op.execute(f"""
            CREATE TRIGGER trg_{tabel}_updated_at
            BEFORE UPDATE ON {tabel}
            FOR EACH ROW
            EXECUTE FUNCTION trg_set_updated_at()
        """)

    # ── 9. Constraint: audit_log hanya bisa INSERT ─────────────────────────────
    # Rule untuk mencegah UPDATE/DELETE pada audit_log
    op.execute("""
        CREATE RULE no_update_audit_log AS
        ON UPDATE TO audit_log
        DO INSTEAD NOTHING
    """)
    op.execute("""
        CREATE RULE no_delete_audit_log AS
        ON DELETE TO audit_log
        DO INSTEAD NOTHING
    """)

    # ── 10. Check constraint: jenis_kelamin ────────────────────────────────────
    op.execute("""
        ALTER TABLE siswa
        ADD CONSTRAINT ck_siswa_jenis_kelamin
        CHECK (jenis_kelamin IS NULL OR jenis_kelamin IN ('L', 'P'))
    """)

    # ── 11. Check constraint: angkatan dan tahun_lulus ────────────────────────
    op.execute("""
        ALTER TABLE siswa
        ADD CONSTRAINT ck_siswa_angkatan_valid
        CHECK (angkatan IS NULL OR (angkatan >= 1900 AND angkatan <= 2100))
    """)
    op.execute("""
        ALTER TABLE siswa
        ADD CONSTRAINT ck_siswa_tahun_lulus_valid
        CHECK (tahun_lulus IS NULL OR (tahun_lulus >= 1900 AND tahun_lulus <= 2100))
    """)


def downgrade() -> None:
    # ── Drop constraints ──────────────────────────────────────────────────────
    op.execute("ALTER TABLE siswa DROP CONSTRAINT IF EXISTS ck_siswa_jenis_kelamin")
    op.execute("ALTER TABLE siswa DROP CONSTRAINT IF EXISTS ck_siswa_angkatan_valid")
    op.execute("ALTER TABLE siswa DROP CONSTRAINT IF EXISTS ck_siswa_tahun_lulus_valid")

    # ── Drop rules ────────────────────────────────────────────────────────────
    op.execute("DROP RULE IF EXISTS no_update_audit_log ON audit_log")
    op.execute("DROP RULE IF EXISTS no_delete_audit_log ON audit_log")

    # ── Drop triggers ─────────────────────────────────────────────────────────
    for tabel in ("sekolah", "admin", "siswa", "dokumen"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{tabel}_updated_at ON {tabel}")
    op.execute("DROP FUNCTION IF EXISTS trg_set_updated_at()")

    # ── Drop indexes ──────────────────────────────────────────────────────────
    for idx in [
        "ix_dokumen_pending",
        "ix_notif_unread_partial",
        "ix_admin_active",
        "ix_dokumen_active",
        "ix_dokumen_metadata_gin",
        "ix_audit_detail_gin",
        "ix_notif_payload_gin",
    ]:
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {idx}")
