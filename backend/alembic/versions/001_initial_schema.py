"""Initial schema — DMS Sekolah

Membuat semua tabel utama:
  - sekolah
  - admin
  - siswa
  - dokumen
  - audit_log
  - notifikasi

Termasuk semua indexes, constraints, dan enum types.

Revision ID: 001_initial_schema
Revises: (none — initial migration)
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# ── Revision info ──────────────────────────────────────────────────────────────
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE
# ─────────────────────────────────────────────────────────────────────────────
def upgrade() -> None:

    # ══ 1. ENUM TYPES ══════════════════════════════════════════════════════════
    # Buat PostgreSQL ENUM types (harus sebelum tabel yang menggunakannya)

    admin_role_enum = postgresql.ENUM(
        "super_admin", "admin", "operator", "viewer",
        name="admin_role_enum",
        create_type=True,
    )
    admin_role_enum.create(op.get_bind(), checkfirst=True)

    jenis_dokumen_enum = postgresql.ENUM(
        "ijazah", "transkrip_nilai", "raport", "skhun",
        "surat_keterangan", "sertifikat", "piagam", "sk_lulus",
        "kartu_pelajar", "surat_aktif", "rekomendasi", "lainnya",
        name="jenis_dokumen_enum",
        create_type=True,
    )
    jenis_dokumen_enum.create(op.get_bind(), checkfirst=True)

    semester_enum = postgresql.ENUM(
        "ganjil", "genap", "full",
        name="semester_enum",
        create_type=True,
    )
    semester_enum.create(op.get_bind(), checkfirst=True)

    status_dokumen_enum = postgresql.ENUM(
        "draft", "pending_review", "approved", "rejected", "archived", "expired",
        name="status_dokumen_enum",
        create_type=True,
    )
    status_dokumen_enum.create(op.get_bind(), checkfirst=True)

    user_type_enum = postgresql.ENUM(
        "admin", "siswa", "system", "guest",
        name="user_type_enum",
        create_type=True,
    )
    user_type_enum.create(op.get_bind(), checkfirst=True)

    audit_status_enum = postgresql.ENUM(
        "success", "failed", "error", "blocked",
        name="audit_status_enum",
        create_type=True,
    )
    audit_status_enum.create(op.get_bind(), checkfirst=True)

    tipe_notifikasi_enum = postgresql.ENUM(
        "dokumen_approved", "dokumen_rejected", "dokumen_uploaded",
        "dokumen_expiring", "dokumen_expired", "password_changed",
        "login_new_device", "pengumuman", "sistem",
        name="tipe_notifikasi_enum",
        create_type=True,
    )
    tipe_notifikasi_enum.create(op.get_bind(), checkfirst=True)

    # ══ 2. TABEL: sekolah ══════════════════════════════════════════════════════
    op.create_table(
        "sekolah",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False,
                  comment="Primary key"),
        sa.Column("nama", sa.String(length=255), nullable=False,
                  comment="Nama lengkap sekolah"),
        sa.Column("kode", sa.String(length=20), nullable=False,
                  comment="Kode sekolah (NPSN atau kode internal)"),
        sa.Column("alamat", sa.Text(), nullable=True,
                  comment="Alamat lengkap sekolah"),
        sa.Column("kota", sa.String(length=100), nullable=True,
                  comment="Kota/kabupaten"),
        sa.Column("provinsi", sa.String(length=100), nullable=True,
                  comment="Provinsi"),
        sa.Column("kode_pos", sa.String(length=10), nullable=True,
                  comment="Kode pos"),
        sa.Column("telepon", sa.String(length=20), nullable=True,
                  comment="Nomor telepon sekolah"),
        sa.Column("email", sa.String(length=255), nullable=True,
                  comment="Email resmi sekolah"),
        sa.Column("website", sa.String(length=255), nullable=True,
                  comment="URL website sekolah"),
        sa.Column("master_key_hash", sa.String(length=128), nullable=False,
                  comment="Hash dari master key sekolah (Argon2id/bcrypt)"),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False,
                  comment="Status aktif sekolah"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu dibuat (UTC)"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu terakhir diperbarui (UTC)"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kode", name="uq_sekolah_kode"),
        comment="Master data sekolah",
    )
    op.create_index("ix_sekolah_kode", "sekolah", ["kode"], unique=False)

    # ══ 3. TABEL: admin ════════════════════════════════════════════════════════
    op.create_table(
        "admin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False,
                  comment="Primary key"),
        sa.Column("username", sa.String(length=100), nullable=False,
                  comment="Username untuk login"),
        sa.Column("email", sa.String(length=255), nullable=False,
                  comment="Email admin"),
        sa.Column("nama_lengkap", sa.String(length=255), nullable=False,
                  comment="Nama lengkap admin"),
        sa.Column("password_hash", sa.String(length=255), nullable=False,
                  comment="Hash password (Argon2id/bcrypt)"),
        sa.Column("role", sa.Enum("super_admin", "admin", "operator", "viewer",
                                   name="admin_role_enum"), nullable=False,
                  comment="Level akses admin"),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False,
                  comment="Status aktif akun admin"),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False,
                  comment="Apakah email sudah diverifikasi"),
        sa.Column("failed_login_count", sa.Integer(), server_default="0", nullable=False,
                  comment="Jumlah percobaan login gagal"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True,
                  comment="Akun terkunci sampai waktu ini"),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Waktu terakhir password diubah"),
        sa.Column("two_factor_secret", sa.String(length=64), nullable=True,
                  comment="Secret key TOTP untuk 2FA"),
        sa.Column("two_factor_enabled", sa.Boolean(), server_default="false", nullable=False,
                  comment="Apakah 2FA aktif"),
        sa.Column("sekolah_id", sa.Integer(), nullable=True,
                  comment="FK ke sekolah yang dikelola"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True,
                  comment="Waktu login terakhir (UTC)"),
        sa.Column("last_login_ip", sa.String(length=45), nullable=True,
                  comment="IP address saat login terakhir"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu akun dibuat (UTC)"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu terakhir data diperbarui (UTC)"),
        sa.ForeignKeyConstraint(["sekolah_id"], ["sekolah.id"],
                                 ondelete="SET NULL", name="fk_admin_sekolah"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_admin_username"),
        sa.UniqueConstraint("email", name="uq_admin_email"),
        comment="Akun administrator DMS",
    )
    # Admin indexes
    op.create_index("ix_admin_username", "admin", ["username"], unique=False)
    op.create_index("ix_admin_email", "admin", ["email"], unique=False)
    op.create_index("ix_admin_sekolah_id", "admin", ["sekolah_id"], unique=False)
    op.create_index("ix_admin_role", "admin", ["role"], unique=False)

    # ══ 4. TABEL: siswa ════════════════════════════════════════════════════════
    op.create_table(
        "siswa",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False,
                  comment="Primary key"),
        sa.Column("nis", sa.String(length=20), nullable=False,
                  comment="Nomor Induk Siswa (unik per sekolah)"),
        sa.Column("nisn", sa.String(length=10), nullable=True,
                  comment="Nomor Induk Siswa Nasional (10 digit)"),
        sa.Column("nama_lengkap", sa.String(length=255), nullable=False,
                  comment="Nama lengkap siswa"),
        sa.Column("tgl_lahir", sa.Date(), nullable=True,
                  comment="Tanggal lahir siswa"),
        sa.Column("tempat_lahir", sa.String(length=100), nullable=True,
                  comment="Tempat lahir siswa"),
        sa.Column("jenis_kelamin", sa.String(length=1), nullable=True,
                  comment="L = Laki-laki, P = Perempuan"),
        sa.Column("agama", sa.String(length=20), nullable=True,
                  comment="Agama siswa"),
        sa.Column("alamat", sa.Text(), nullable=True,
                  comment="Alamat lengkap siswa"),
        sa.Column("kelas", sa.String(length=20), nullable=True,
                  comment="Kelas/tingkat"),
        sa.Column("jurusan", sa.String(length=100), nullable=True,
                  comment="Jurusan / program studi"),
        sa.Column("angkatan", sa.Integer(), nullable=True,
                  comment="Tahun angkatan masuk"),
        sa.Column("tahun_lulus", sa.Integer(), nullable=True,
                  comment="Tahun kelulusan"),
        sa.Column("email", sa.String(length=255), nullable=True,
                  comment="Email siswa"),
        sa.Column("telepon", sa.String(length=20), nullable=True,
                  comment="Nomor telepon siswa"),
        sa.Column("telepon_ortu", sa.String(length=20), nullable=True,
                  comment="Nomor telepon orang tua/wali"),
        sa.Column("nama_ortu", sa.String(length=255), nullable=True,
                  comment="Nama orang tua/wali"),
        sa.Column("foto_path", sa.String(length=512), nullable=True,
                  comment="Path/URL foto siswa di MinIO"),
        sa.Column("entropy_seed", sa.String(length=128), nullable=True,
                  comment="Seed entropy untuk NeuralKeyGen"),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False,
                  comment="Status aktif siswa"),
        sa.Column("sekolah_id", sa.Integer(), nullable=False,
                  comment="FK ke tabel sekolah"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu record dibuat (UTC)"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu terakhir diperbarui (UTC)"),
        sa.ForeignKeyConstraint(["sekolah_id"], ["sekolah.id"],
                                 ondelete="RESTRICT", name="fk_siswa_sekolah"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nis", "sekolah_id", name="uq_siswa_nis_sekolah"),
        sa.UniqueConstraint("nisn", name="uq_siswa_nisn"),
        sa.UniqueConstraint("email", name="uq_siswa_email"),
        comment="Data siswa dan seed untuk NeuralKeyGen",
    )
    # Siswa indexes
    op.create_index("ix_siswa_nis", "siswa", ["nis"], unique=False)
    op.create_index("ix_siswa_nisn", "siswa", ["nisn"], unique=False)
    op.create_index("ix_siswa_email", "siswa", ["email"], unique=False)
    op.create_index("ix_siswa_sekolah_id", "siswa", ["sekolah_id"], unique=False)
    op.create_index("ix_siswa_angkatan", "siswa", ["angkatan"], unique=False)
    op.create_index("ix_siswa_kelas_sekolah", "siswa", ["kelas", "sekolah_id"], unique=False)

    # ══ 5. TABEL: dokumen ══════════════════════════════════════════════════════
    op.create_table(
        "dokumen",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False,
                  comment="Primary key"),
        sa.Column("siswa_id", sa.Integer(), nullable=False,
                  comment="FK ke tabel siswa"),
        sa.Column("jenis_dok", sa.Enum("ijazah", "transkrip_nilai", "raport", "skhun",
                                        "surat_keterangan", "sertifikat", "piagam",
                                        "sk_lulus", "kartu_pelajar", "surat_aktif",
                                        "rekomendasi", "lainnya",
                                        name="jenis_dokumen_enum"), nullable=False,
                  comment="Jenis/kategori dokumen akademik"),
        sa.Column("tahun_ajaran", sa.String(length=9), nullable=False,
                  comment="Tahun ajaran format YYYY/YYYY"),
        sa.Column("semester", sa.Enum("ganjil", "genap", "full",
                                       name="semester_enum"),
                  server_default="full", nullable=False,
                  comment="Semester: ganjil | genap | full"),
        sa.Column("status", sa.Enum("draft", "pending_review", "approved",
                                     "rejected", "archived", "expired",
                                     name="status_dokumen_enum"),
                  server_default="draft", nullable=False,
                  comment="Status alur persetujuan"),
        sa.Column("file_path_encrypted", sa.String(length=1024), nullable=False,
                  comment="Path object di MinIO (file terenkripsi AES-256-GCM)"),
        sa.Column("file_hash_sha256", sa.String(length=64), nullable=False,
                  comment="SHA-256 hash dari file sebelum enkripsi"),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True,
                  comment="Ukuran file asli dalam bytes"),
        sa.Column("mime_type", sa.String(length=100), nullable=True,
                  comment="MIME type file asli"),
        sa.Column("original_filename", sa.String(length=512), nullable=True,
                  comment="Nama file asli saat diupload"),
        sa.Column("key_wrapped", sa.Text(), nullable=False,
                  comment="Document key yang sudah di-wrap (AES Key Wrap)"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment="Metadata tambahan dalam JSONB"),
        sa.Column("uploaded_by", sa.Integer(), nullable=True,
                  comment="FK ke admin yang mengupload"),
        sa.Column("approved_by", sa.Integer(), nullable=True,
                  comment="FK ke admin yang menyetujui"),
        sa.Column("rejected_reason", sa.Text(), nullable=True,
                  comment="Alasan penolakan"),
        sa.Column("versi", sa.Integer(), server_default="1", nullable=False,
                  comment="Nomor versi dokumen"),
        sa.Column("dokumen_induk_id", sa.Integer(), nullable=True,
                  comment="FK ke versi dokumen sebelumnya"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu dokumen diupload (UTC)"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu terakhir metadata diperbarui (UTC)"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Batas waktu berlaku dokumen"),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Waktu dokumen disetujui (UTC)"),
        sa.ForeignKeyConstraint(["siswa_id"], ["siswa.id"],
                                 ondelete="RESTRICT", name="fk_dokumen_siswa"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["admin.id"],
                                 ondelete="SET NULL", name="fk_dokumen_uploaded_by"),
        sa.ForeignKeyConstraint(["approved_by"], ["admin.id"],
                                 ondelete="SET NULL", name="fk_dokumen_approved_by"),
        sa.ForeignKeyConstraint(["dokumen_induk_id"], ["dokumen.id"],
                                 ondelete="SET NULL", name="fk_dokumen_induk"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "siswa_id", "jenis_dok", "tahun_ajaran", "semester",
            name="uq_dokumen_siswa_jenis_tahun_semester",
        ),
        sa.CheckConstraint(
            "tahun_ajaran ~ '^[0-9]{4}/[0-9]{4}$'",
            name="ck_dokumen_format_tahun_ajaran",
        ),
        comment="Dokumen akademik siswa (terenkripsi di MinIO)",
    )
    # Dokumen indexes
    op.create_index("ix_dokumen_siswa_id", "dokumen", ["siswa_id"], unique=False)
    op.create_index("ix_dokumen_created_at", "dokumen", ["created_at"], unique=False)
    op.create_index("ix_dokumen_jenis_dok", "dokumen", ["jenis_dok"], unique=False)
    op.create_index("ix_dokumen_tahun_ajaran", "dokumen", ["tahun_ajaran"], unique=False)
    op.create_index("ix_dokumen_status", "dokumen", ["status"], unique=False)
    op.create_index("ix_dokumen_file_hash_sha256", "dokumen", ["file_hash_sha256"], unique=False)
    op.create_index("ix_dokumen_siswa_jenis", "dokumen", ["siswa_id", "jenis_dok"], unique=False)
    op.create_index("ix_dokumen_uploaded_by", "dokumen", ["uploaded_by"], unique=False)

    # ══ 6. TABEL: audit_log ════════════════════════════════════════════════════
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False,
                  comment="Primary key"),
        sa.Column("user_id", sa.Integer(), nullable=True,
                  comment="FK ke tabel admin"),
        sa.Column("siswa_id", sa.Integer(), nullable=True,
                  comment="FK ke tabel siswa"),
        sa.Column("user_type", sa.Enum("admin", "siswa", "system", "guest",
                                        name="user_type_enum"), nullable=False,
                  comment="Tipe aktor"),
        sa.Column("action", sa.String(length=100), nullable=False,
                  comment="Jenis aksi yang dilakukan"),
        sa.Column("dokumen_id", sa.Integer(), nullable=True,
                  comment="FK ke dokumen yang terlibat"),
        sa.Column("resource_type", sa.String(length=50), nullable=True,
                  comment="Tipe resource yang diakses"),
        sa.Column("resource_id", sa.Integer(), nullable=True,
                  comment="ID resource yang diakses"),
        sa.Column("ip_address", sa.String(length=45), nullable=True,
                  comment="IP address aktor (IPv4/IPv6)"),
        sa.Column("user_agent", sa.Text(), nullable=True,
                  comment="User-Agent string dari HTTP request"),
        sa.Column("request_id", sa.String(length=36), nullable=True,
                  comment="UUID request untuk korelasi log"),
        sa.Column("endpoint", sa.String(length=255), nullable=True,
                  comment="Endpoint HTTP yang diakses"),
        sa.Column("http_method", sa.String(length=10), nullable=True,
                  comment="HTTP method"),
        sa.Column("status", sa.Enum("success", "failed", "error", "blocked",
                                     name="audit_status_enum"), nullable=False,
                  comment="Hasil aksi"),
        sa.Column("error_message", sa.Text(), nullable=True,
                  comment="Pesan error jika status = failed/error"),
        sa.Column("detail", postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment="Detail tambahan dalam JSONB"),
        sa.Column("duration_ms", sa.Integer(), nullable=True,
                  comment="Durasi request dalam milidetik"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu aksi terjadi (UTC, immutable)"),
        sa.ForeignKeyConstraint(["user_id"], ["admin.id"],
                                 ondelete="SET NULL", name="fk_audit_admin"),
        sa.ForeignKeyConstraint(["siswa_id"], ["siswa.id"],
                                 ondelete="SET NULL", name="fk_audit_siswa"),
        sa.ForeignKeyConstraint(["dokumen_id"], ["dokumen.id"],
                                 ondelete="SET NULL", name="fk_audit_dokumen"),
        sa.PrimaryKeyConstraint("id"),
        comment="Immutable audit trail — INSERT ONLY",
    )
    # AuditLog indexes
    op.create_index("ix_audit_user_id", "audit_log", ["user_id"], unique=False)
    op.create_index("ix_audit_created_at", "audit_log", ["created_at"], unique=False)
    op.create_index("ix_audit_dokumen_id", "audit_log", ["dokumen_id"], unique=False)
    op.create_index("ix_audit_action", "audit_log", ["action"], unique=False)
    op.create_index("ix_audit_status", "audit_log", ["status"], unique=False)
    op.create_index("ix_audit_ip_address", "audit_log", ["ip_address"], unique=False)
    op.create_index("ix_audit_user_action", "audit_log", ["user_id", "action"], unique=False)
    op.create_index("ix_audit_user_type", "audit_log", ["user_type"], unique=False)

    # ══ 7. TABEL: notifikasi ═══════════════════════════════════════════════════
    op.create_table(
        "notifikasi",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False,
                  comment="Primary key"),
        sa.Column("siswa_id", sa.Integer(), nullable=False,
                  comment="FK ke tabel siswa — penerima notifikasi"),
        sa.Column("dokumen_id", sa.Integer(), nullable=True,
                  comment="FK ke dokumen yang terkait"),
        sa.Column("tipe", sa.Enum(
            "dokumen_approved", "dokumen_rejected", "dokumen_uploaded",
            "dokumen_expiring", "dokumen_expired", "password_changed",
            "login_new_device", "pengumuman", "sistem",
            name="tipe_notifikasi_enum"
        ), nullable=False,
                  comment="Kategori notifikasi"),
        sa.Column("judul", sa.String(length=255), nullable=False,
                  comment="Judul notifikasi"),
        sa.Column("pesan", sa.Text(), nullable=False,
                  comment="Isi pesan notifikasi"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment="Data tambahan dalam JSONB"),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False,
                  comment="Apakah notifikasi sudah dibaca"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Waktu notifikasi dibaca (UTC)"),
        sa.Column("is_sent_email", sa.Boolean(), server_default="false", nullable=False,
                  comment="Apakah sudah dikirim via email"),
        sa.Column("sent_email_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Waktu email dikirim (UTC)"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  comment="Waktu notifikasi dibuat (UTC)"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Waktu notifikasi kedaluwarsa"),
        sa.ForeignKeyConstraint(["siswa_id"], ["siswa.id"],
                                 ondelete="CASCADE", name="fk_notifikasi_siswa"),
        sa.ForeignKeyConstraint(["dokumen_id"], ["dokumen.id"],
                                 ondelete="SET NULL", name="fk_notifikasi_dokumen"),
        sa.PrimaryKeyConstraint("id"),
        comment="Notifikasi in-app untuk siswa",
    )
    # Notifikasi indexes
    op.create_index("ix_notif_siswa_id", "notifikasi", ["siswa_id"], unique=False)
    op.create_index("ix_notif_created_at", "notifikasi", ["created_at"], unique=False)
    op.create_index("ix_notif_is_read", "notifikasi", ["is_read"], unique=False)
    op.create_index("ix_notif_siswa_unread", "notifikasi", ["siswa_id", "is_read"], unique=False)
    op.create_index("ix_notif_tipe", "notifikasi", ["tipe"], unique=False)


# ─────────────────────────────────────────────────────────────────────────────
# DOWNGRADE — DROP dalam urutan terbalik (dependents first)
# ─────────────────────────────────────────────────────────────────────────────
def downgrade() -> None:

    # ── Drop tabel (urutan: dependents first) ──────────────────────────────────
    op.drop_table("notifikasi")
    op.drop_table("audit_log")
    op.drop_table("dokumen")
    op.drop_table("siswa")
    op.drop_table("admin")
    op.drop_table("sekolah")

    # ── Drop ENUM types ────────────────────────────────────────────────────────
    for enum_name in [
        "tipe_notifikasi_enum",
        "audit_status_enum",
        "user_type_enum",
        "status_dokumen_enum",
        "semester_enum",
        "jenis_dokumen_enum",
        "admin_role_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")
