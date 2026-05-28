"""Seed data awal — super admin dan contoh sekolah

Menyisipkan:
  - 1 akun super_admin default
  - 1 contoh sekolah (bisa dihapus di production)

PERHATIAN: Ganti password_hash sebelum deploy ke production!
Gunakan: python -c "from passlib.context import CryptContext; print(CryptContext(['bcrypt']).hash('GantiPassword123!'))"

Revision ID: 002_seed_data
Revises: 001_initial_schema
Create Date: 2024-01-01 01:00:00.000000
"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision: str = "002_seed_data"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tabel references
sekolah_table = sa.table(
    "sekolah",
    sa.column("id", sa.Integer),
    sa.column("nama", sa.String),
    sa.column("kode", sa.String),
    sa.column("alamat", sa.Text),
    sa.column("master_key_hash", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)

admin_table = sa.table(
    "admin",
    sa.column("id", sa.Integer),
    sa.column("username", sa.String),
    sa.column("email", sa.String),
    sa.column("nama_lengkap", sa.String),
    sa.column("password_hash", sa.String),
    sa.column("role", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("is_verified", sa.Boolean),
    sa.column("failed_login_count", sa.Integer),
    sa.column("two_factor_enabled", sa.Boolean),
    sa.column("sekolah_id", sa.Integer),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)


def upgrade() -> None:
    now = datetime.now(timezone.utc)

    # ── 1. Contoh Sekolah ──────────────────────────────────────────────────────
    # master_key_hash: Argon2id hash dari "CHANGE_THIS_MASTER_KEY_IN_PRODUCTION"
    # Wajib dirotasi setelah setup awal!
    op.bulk_insert(
        sekolah_table,
        [
            {
                "nama": "SMA Negeri 1 Contoh",
                "kode": "NPSN00000001",
                "alamat": "Jl. Pendidikan No. 1, Jakarta",
                "master_key_hash": (
                    # GANTI INI DI PRODUCTION!
                    "$argon2id$v=19$m=65536,t=3,p=4$"
                    "PLACEHOLDER_HASH_GANTI_DI_PRODUCTION"
                    "$PLACEHOLDER_HASH_GANTI_DI_PRODUCTION"
                ),
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    # ── 2. Super Admin Default ─────────────────────────────────────────────────
    # password_hash: bcrypt hash dari "Admin@DMS2024!" — WAJIB DIGANTI!
    # Generate baru: python -c "import bcrypt; print(bcrypt.hashpw(b'NewPass', bcrypt.gensalt()).decode())"
    op.bulk_insert(
        admin_table,
        [
            {
                "username": "superadmin",
                "email": "superadmin@dms-sekolah.id",
                "nama_lengkap": "Super Administrator",
                "password_hash": (
                    # GANTI INI SEGERA SETELAH SETUP!
                    "$2b$12$PLACEHOLDER_BCRYPT_HASH_GANTI_SEBELUM_PRODUCTION"
                ),
                "role": "super_admin",
                "is_active": True,
                "is_verified": True,
                "failed_login_count": 0,
                "two_factor_enabled": False,
                "sekolah_id": None,  # super_admin tidak terikat ke sekolah
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    # Hapus seed data (gunakan WHERE untuk tidak menghapus data real)
    op.execute(
        "DELETE FROM admin WHERE username = 'superadmin' "
        "AND email = 'superadmin@dms-sekolah.id'"
    )
    op.execute(
        "DELETE FROM sekolah WHERE kode = 'NPSN00000001'"
    )
