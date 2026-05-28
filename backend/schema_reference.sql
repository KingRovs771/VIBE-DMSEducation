-- ===========================================================================
-- DMS Sekolah — PostgreSQL Schema Reference (DDL)
-- ===========================================================================
-- File ini adalah REFERENSI. Gunakan Alembic untuk menjalankan migrasi sesungguhnya.
-- Perintah: alembic upgrade head
-- ===========================================================================

-- ── Extension ────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Untuk full-text search trigram

-- ===========================================================================
-- ENUM TYPES
-- ===========================================================================

CREATE TYPE admin_role_enum AS ENUM (
    'super_admin', 'admin', 'operator', 'viewer'
);

CREATE TYPE jenis_dokumen_enum AS ENUM (
    'ijazah', 'transkrip_nilai', 'raport', 'skhun',
    'surat_keterangan', 'sertifikat', 'piagam', 'sk_lulus',
    'kartu_pelajar', 'surat_aktif', 'rekomendasi', 'lainnya'
);

CREATE TYPE semester_enum AS ENUM (
    'ganjil', 'genap', 'full'
);

CREATE TYPE status_dokumen_enum AS ENUM (
    'draft', 'pending_review', 'approved', 'rejected', 'archived', 'expired'
);

CREATE TYPE user_type_enum AS ENUM (
    'admin', 'siswa', 'system', 'guest'
);

CREATE TYPE audit_status_enum AS ENUM (
    'success', 'failed', 'error', 'blocked'
);

CREATE TYPE tipe_notifikasi_enum AS ENUM (
    'dokumen_approved', 'dokumen_rejected', 'dokumen_uploaded',
    'dokumen_expiring', 'dokumen_expired', 'password_changed',
    'login_new_device', 'pengumuman', 'sistem'
);

-- ===========================================================================
-- TABEL 1: sekolah
-- ===========================================================================

CREATE TABLE sekolah (
    id                  SERIAL          PRIMARY KEY,
    nama                VARCHAR(255)    NOT NULL,
    kode                VARCHAR(20)     NOT NULL UNIQUE,   -- NPSN / kode internal
    alamat              TEXT,
    kota                VARCHAR(100),
    provinsi            VARCHAR(100),
    kode_pos            VARCHAR(10),
    telepon             VARCHAR(20),
    email               VARCHAR(255),
    website             VARCHAR(255),
    master_key_hash     VARCHAR(128)    NOT NULL,           -- Argon2id hash
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sekolah_kode UNIQUE (kode)
);

-- Indexes sekolah
CREATE INDEX ix_sekolah_kode ON sekolah (kode);

COMMENT ON TABLE  sekolah IS 'Master data sekolah';
COMMENT ON COLUMN sekolah.master_key_hash IS 'Hash Argon2id dari master key sekolah. Digunakan sebagai komponen enkripsi dokumen siswa';
COMMENT ON COLUMN sekolah.kode IS 'Kode NPSN atau kode internal sekolah, unik nasional';

-- ===========================================================================
-- TABEL 2: admin
-- ===========================================================================

CREATE TABLE admin (
    id                      SERIAL          PRIMARY KEY,
    username                VARCHAR(100)    NOT NULL UNIQUE,
    email                   VARCHAR(255)    NOT NULL UNIQUE,
    nama_lengkap            VARCHAR(255)    NOT NULL,
    password_hash           VARCHAR(255)    NOT NULL,           -- bcrypt/Argon2id
    role                    admin_role_enum NOT NULL DEFAULT 'operator',
    is_active               BOOLEAN         NOT NULL DEFAULT TRUE,
    is_verified             BOOLEAN         NOT NULL DEFAULT FALSE,
    failed_login_count      INTEGER         NOT NULL DEFAULT 0,
    locked_until            TIMESTAMPTZ,                        -- NULL = tidak terkunci
    password_changed_at     TIMESTAMPTZ,
    two_factor_secret       VARCHAR(64),                        -- TOTP secret (terenkripsi)
    two_factor_enabled      BOOLEAN         NOT NULL DEFAULT FALSE,
    sekolah_id              INTEGER         REFERENCES sekolah(id) ON DELETE SET NULL,
    last_login              TIMESTAMPTZ,
    last_login_ip           VARCHAR(45),
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_admin_username UNIQUE (username),
    CONSTRAINT uq_admin_email    UNIQUE (email)
);

-- Indexes admin
CREATE INDEX ix_admin_username   ON admin (username);
CREATE INDEX ix_admin_email      ON admin (email);
CREATE INDEX ix_admin_sekolah_id ON admin (sekolah_id);
CREATE INDEX ix_admin_role       ON admin (role);
-- Partial: hanya admin aktif
CREATE INDEX ix_admin_active ON admin (sekolah_id, role) WHERE is_active = TRUE;

COMMENT ON TABLE  admin IS 'Akun administrator DMS';
COMMENT ON COLUMN admin.password_hash IS 'Hash password menggunakan bcrypt atau Argon2id. TIDAK BOLEH plaintext!';
COMMENT ON COLUMN admin.failed_login_count IS 'Counter login gagal. Akun terkunci jika >= 5';
COMMENT ON COLUMN admin.sekolah_id IS 'NULL untuk super_admin (akses semua sekolah)';

-- ===========================================================================
-- TABEL 3: siswa
-- ===========================================================================

CREATE TABLE siswa (
    id              SERIAL          PRIMARY KEY,
    nis             VARCHAR(20)     NOT NULL,               -- Unik per sekolah
    nisn            VARCHAR(10)     UNIQUE,                 -- Unik nasional
    nama_lengkap    VARCHAR(255)    NOT NULL,
    tgl_lahir       DATE,
    tempat_lahir    VARCHAR(100),
    jenis_kelamin   VARCHAR(1)      CHECK (jenis_kelamin IN ('L', 'P')),
    agama           VARCHAR(20),
    alamat          TEXT,
    kelas           VARCHAR(20),
    jurusan         VARCHAR(100),
    angkatan        INTEGER         CHECK (angkatan IS NULL OR angkatan BETWEEN 1900 AND 2100),
    tahun_lulus     INTEGER         CHECK (tahun_lulus IS NULL OR tahun_lulus BETWEEN 1900 AND 2100),
    email           VARCHAR(255)    UNIQUE,
    telepon         VARCHAR(20),
    telepon_ortu    VARCHAR(20),
    nama_ortu       VARCHAR(255),
    foto_path       VARCHAR(512),                           -- Path di MinIO bucket dms-avatars
    entropy_seed    VARCHAR(128),                           -- Seed untuk NeuralKeyGen
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    sekolah_id      INTEGER         NOT NULL REFERENCES sekolah(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_siswa_nis_sekolah UNIQUE (nis, sekolah_id),
    CONSTRAINT uq_siswa_nisn        UNIQUE (nisn),
    CONSTRAINT uq_siswa_email       UNIQUE (email)
);

-- Indexes siswa (WAJIB sesuai spesifikasi)
CREATE INDEX ix_siswa_nis         ON siswa (nis);           -- by NIS
CREATE INDEX ix_siswa_nisn        ON siswa (nisn);          -- by NISN
CREATE INDEX ix_siswa_email       ON siswa (email);         -- by email
CREATE INDEX ix_siswa_sekolah_id  ON siswa (sekolah_id);    -- by sekolah
CREATE INDEX ix_siswa_angkatan    ON siswa (angkatan);      -- by angkatan
CREATE INDEX ix_siswa_kelas_sekolah ON siswa (kelas, sekolah_id); -- compound

COMMENT ON TABLE  siswa IS 'Data siswa dan seed untuk NeuralKeyGen';
COMMENT ON COLUMN siswa.entropy_seed IS 'Seed entropy untuk NeuralKeyGen. Digabung dengan master_key_hash sekolah untuk enkripsi per-siswa';
COMMENT ON COLUMN siswa.nisn IS 'Nomor Induk Siswa Nasional — 10 digit, unik secara nasional';

-- ===========================================================================
-- TABEL 4: dokumen
-- ===========================================================================

CREATE TABLE dokumen (
    id                  SERIAL              PRIMARY KEY,
    siswa_id            INTEGER             NOT NULL REFERENCES siswa(id) ON DELETE RESTRICT,
    jenis_dok           jenis_dokumen_enum  NOT NULL,
    tahun_ajaran        VARCHAR(9)          NOT NULL
                            CHECK (tahun_ajaran ~ '^\d{4}/\d{4}$'),  -- Format: 2023/2024
    semester            semester_enum       NOT NULL DEFAULT 'full',
    status              status_dokumen_enum NOT NULL DEFAULT 'draft',

    -- Storage (MinIO)
    file_path_encrypted VARCHAR(1024)       NOT NULL, -- Path object MinIO, file terenkripsi
    file_hash_sha256    VARCHAR(64)         NOT NULL, -- SHA-256 SEBELUM enkripsi (integritas)
    file_size_bytes     INTEGER,
    mime_type           VARCHAR(100),
    original_filename   VARCHAR(512),

    -- Enkripsi
    key_wrapped         TEXT                NOT NULL, -- AES Key Wrap, base64 encoded

    -- Metadata
    metadata_json       JSONB,

    -- Audit
    uploaded_by         INTEGER REFERENCES admin(id) ON DELETE SET NULL,
    approved_by         INTEGER REFERENCES admin(id) ON DELETE SET NULL,
    rejected_reason     TEXT,
    versi               INTEGER             NOT NULL DEFAULT 1,
    dokumen_induk_id    INTEGER REFERENCES dokumen(id) ON DELETE SET NULL,

    -- Timestamps
    created_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    expires_at          TIMESTAMPTZ,
    approved_at         TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT uq_dokumen_siswa_jenis_tahun_semester
        UNIQUE (siswa_id, jenis_dok, tahun_ajaran, semester)
);

-- Indexes dokumen (WAJIB sesuai spesifikasi)
CREATE INDEX ix_dokumen_siswa_id       ON dokumen (siswa_id);           -- by siswa
CREATE INDEX ix_dokumen_created_at     ON dokumen (created_at);         -- timeline
CREATE INDEX ix_dokumen_jenis_dok      ON dokumen (jenis_dok);          -- by jenis
CREATE INDEX ix_dokumen_tahun_ajaran   ON dokumen (tahun_ajaran);       -- by tahun
CREATE INDEX ix_dokumen_status         ON dokumen (status);             -- by status
CREATE INDEX ix_dokumen_file_hash_sha256 ON dokumen (file_hash_sha256); -- dedup/integritas
CREATE INDEX ix_dokumen_siswa_jenis    ON dokumen (siswa_id, jenis_dok); -- compound
CREATE INDEX ix_dokumen_uploaded_by    ON dokumen (uploaded_by);

-- Partial indexes lanjutan
CREATE INDEX ix_dokumen_pending ON dokumen (created_at, siswa_id)
    WHERE status = 'pending_review';
CREATE INDEX ix_dokumen_active ON dokumen (siswa_id, jenis_dok, tahun_ajaran)
    WHERE status NOT IN ('archived', 'expired');

-- GIN index untuk JSONB query
CREATE INDEX ix_dokumen_metadata_gin ON dokumen USING GIN (metadata_json)
    WHERE metadata_json IS NOT NULL;

COMMENT ON TABLE  dokumen IS 'Dokumen akademik siswa (terenkripsi di MinIO)';
COMMENT ON COLUMN dokumen.file_path_encrypted IS 'Path object MinIO. File disimpan terenkripsi AES-256-GCM';
COMMENT ON COLUMN dokumen.file_hash_sha256 IS 'SHA-256 dari file SEBELUM enkripsi. Untuk verifikasi integritas';
COMMENT ON COLUMN dokumen.key_wrapped IS 'Document key yang sudah di-wrap dengan AES Key Wrap. base64(wrapped_key)';

-- ===========================================================================
-- TABEL 5: audit_log
-- ===========================================================================

CREATE TABLE audit_log (
    id              SERIAL              PRIMARY KEY,
    user_id         INTEGER             REFERENCES admin(id)   ON DELETE SET NULL,
    siswa_id        INTEGER             REFERENCES siswa(id)   ON DELETE SET NULL,
    user_type       user_type_enum      NOT NULL,
    action          VARCHAR(100)        NOT NULL,
    dokumen_id      INTEGER             REFERENCES dokumen(id) ON DELETE SET NULL,
    resource_type   VARCHAR(50),
    resource_id     INTEGER,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    request_id      VARCHAR(36),        -- UUID untuk korelasi
    endpoint        VARCHAR(255),
    http_method     VARCHAR(10),
    status          audit_status_enum   NOT NULL,
    error_message   TEXT,
    detail          JSONB,              -- Data tambahan
    duration_ms     INTEGER,
    created_at      TIMESTAMPTZ         NOT NULL DEFAULT NOW()
    -- TIDAK ADA updated_at — immutable!
);

-- Indexes audit_log (WAJIB sesuai spesifikasi)
CREATE INDEX ix_audit_user_id    ON audit_log (user_id);
CREATE INDEX ix_audit_created_at ON audit_log (created_at);
CREATE INDEX ix_audit_dokumen_id ON audit_log (dokumen_id);
-- Indexes tambahan
CREATE INDEX ix_audit_action     ON audit_log (action);
CREATE INDEX ix_audit_status     ON audit_log (status);
CREATE INDEX ix_audit_ip_address ON audit_log (ip_address);
CREATE INDEX ix_audit_user_action ON audit_log (user_id, action);  -- compound
CREATE INDEX ix_audit_user_type  ON audit_log (user_type);

-- GIN index untuk query detail JSONB
CREATE INDEX ix_audit_detail_gin ON audit_log USING GIN (detail)
    WHERE detail IS NOT NULL;

-- Rules: IMMUTABLE — tidak bisa di-UPDATE atau DELETE
CREATE RULE no_update_audit_log AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE RULE no_delete_audit_log AS ON DELETE TO audit_log DO INSTEAD NOTHING;

COMMENT ON TABLE  audit_log IS 'Immutable audit trail — INSERT ONLY. UPDATE dan DELETE dicegah oleh rule';

-- ===========================================================================
-- TABEL 6: notifikasi
-- ===========================================================================

CREATE TABLE notifikasi (
    id              SERIAL                  PRIMARY KEY,
    siswa_id        INTEGER                 NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
    dokumen_id      INTEGER                 REFERENCES dokumen(id) ON DELETE SET NULL,
    tipe            tipe_notifikasi_enum    NOT NULL,
    judul           VARCHAR(255)            NOT NULL,
    pesan           TEXT                    NOT NULL,
    payload         JSONB,                              -- Data action/link tambahan
    is_read         BOOLEAN                 NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMPTZ,
    is_sent_email   BOOLEAN                 NOT NULL DEFAULT FALSE,
    sent_email_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ
);

-- Indexes notifikasi (WAJIB sesuai spesifikasi)
CREATE INDEX ix_notif_siswa_id   ON notifikasi (siswa_id);
CREATE INDEX ix_notif_created_at ON notifikasi (created_at);
CREATE INDEX ix_notif_is_read    ON notifikasi (is_read);
-- Indexes tambahan
CREATE INDEX ix_notif_tipe       ON notifikasi (tipe);
-- Partial index: hanya notif yang belum dibaca
CREATE INDEX ix_notif_unread_partial ON notifikasi (siswa_id, created_at)
    WHERE is_read = FALSE;
-- Compound: unread per siswa
CREATE INDEX ix_notif_siswa_unread ON notifikasi (siswa_id, is_read);

-- GIN index untuk payload JSONB
CREATE INDEX ix_notif_payload_gin ON notifikasi USING GIN (payload)
    WHERE payload IS NOT NULL;

COMMENT ON TABLE  notifikasi IS 'Notifikasi in-app untuk siswa';

-- ===========================================================================
-- TRIGGERS: auto-update updated_at
-- ===========================================================================

CREATE OR REPLACE FUNCTION trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sekolah_updated_at
    BEFORE UPDATE ON sekolah
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER trg_admin_updated_at
    BEFORE UPDATE ON admin
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER trg_siswa_updated_at
    BEFORE UPDATE ON siswa
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER trg_dokumen_updated_at
    BEFORE UPDATE ON dokumen
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- ===========================================================================
-- RINGKASAN INDEXES
-- ===========================================================================
-- Total indexes: 28 indexes di 6 tabel
--
-- Tabel sekolah  : 1 index
-- Tabel admin    : 5 indexes (4 regular + 1 partial)
-- Tabel siswa    : 6 indexes
-- Tabel dokumen  : 11 indexes (7 regular + 2 partial + 1 GIN + 1 compound)
-- Tabel audit_log: 8 indexes (7 regular + 1 GIN)
-- Tabel notifikasi: 7 indexes (4 regular + 1 partial + 1 compound + 1 GIN)
-- ===========================================================================
