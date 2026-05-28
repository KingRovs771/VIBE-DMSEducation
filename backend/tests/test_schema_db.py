"""
Tests untuk database schema — validasi model dan relasi
"""
import pytest
from datetime import datetime, date, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class TestSekolahModel:
    """Test model Sekolah."""

    async def test_create_sekolah(self, db_session: AsyncSession):
        """Buat sekolah dan verifikasi field."""
        from app.models.sekolah import Sekolah
        now = datetime.now(timezone.utc)
        sekolah = Sekolah(
            nama="SMA Negeri 1 Test",
            kode="NPSN99999999",
            alamat="Jl. Test No. 1",
            master_key_hash="$argon2id$v=19$test_hash",
            created_at=now,
            updated_at=now,
        )
        db_session.add(sekolah)
        await db_session.flush()

        assert sekolah.id is not None
        assert sekolah.is_active is True
        assert sekolah.kode == "NPSN99999999"

    async def test_sekolah_kode_unique(self, db_session: AsyncSession):
        """Kode sekolah harus unik."""
        from app.models.sekolah import Sekolah
        from sqlalchemy.exc import IntegrityError
        now = datetime.now(timezone.utc)

        s1 = Sekolah(nama="Sekolah A", kode="DUPKODE01",
                     master_key_hash="hash1", created_at=now, updated_at=now)
        s2 = Sekolah(nama="Sekolah B", kode="DUPKODE01",
                     master_key_hash="hash2", created_at=now, updated_at=now)
        db_session.add(s1)
        await db_session.flush()

        db_session.add(s2)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    def test_sekolah_repr(self):
        from app.models.sekolah import Sekolah
        s = Sekolah(id=1, kode="TEST01", nama="Test Sekolah",
                    master_key_hash="hash")
        assert "TEST01" in repr(s)


class TestSiswaModel:
    """Test model Siswa."""

    async def test_create_siswa(self, db_session: AsyncSession):
        """Buat siswa dengan sekolah yang valid."""
        from app.models.sekolah import Sekolah
        from app.models.siswa import Siswa
        now = datetime.now(timezone.utc)

        sekolah = Sekolah(
            nama="Sekolah Test Siswa", kode="SKTEST01",
            master_key_hash="hash", created_at=now, updated_at=now,
        )
        db_session.add(sekolah)
        await db_session.flush()

        siswa = Siswa(
            nis="12345",
            nama_lengkap="Budi Santoso",
            sekolah_id=sekolah.id,
            kelas="XII",
            angkatan=2022,
            created_at=now,
            updated_at=now,
        )
        db_session.add(siswa)
        await db_session.flush()

        assert siswa.id is not None
        assert siswa.is_active is True
        assert siswa.sekolah_id == sekolah.id

    async def test_nis_unique_per_sekolah(self, db_session: AsyncSession):
        """NIS harus unik per sekolah, tapi boleh sama di sekolah berbeda."""
        from app.models.sekolah import Sekolah
        from app.models.siswa import Siswa
        from sqlalchemy.exc import IntegrityError
        now = datetime.now(timezone.utc)

        s1 = Sekolah(nama="Sekolah 1", kode="SK00001",
                     master_key_hash="h1", created_at=now, updated_at=now)
        db_session.add(s1)
        await db_session.flush()

        siswa1 = Siswa(nis="999", nama_lengkap="A",
                       sekolah_id=s1.id, created_at=now, updated_at=now)
        siswa2 = Siswa(nis="999", nama_lengkap="B",
                       sekolah_id=s1.id, created_at=now, updated_at=now)
        db_session.add(siswa1)
        await db_session.flush()

        db_session.add(siswa2)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_email_siswa_unique(self, db_session: AsyncSession):
        """Email siswa harus unik secara global."""
        from app.models.sekolah import Sekolah
        from app.models.siswa import Siswa
        from sqlalchemy.exc import IntegrityError
        now = datetime.now(timezone.utc)

        s = Sekolah(nama="Tes Email", kode="SKEMAIL1",
                    master_key_hash="h", created_at=now, updated_at=now)
        db_session.add(s)
        await db_session.flush()

        s1 = Siswa(nis="001", nama_lengkap="X",
                   email="duplikat@mail.com", sekolah_id=s.id,
                   created_at=now, updated_at=now)
        s2 = Siswa(nis="002", nama_lengkap="Y",
                   email="duplikat@mail.com", sekolah_id=s.id,
                   created_at=now, updated_at=now)
        db_session.add(s1)
        await db_session.flush()

        db_session.add(s2)
        with pytest.raises(IntegrityError):
            await db_session.flush()


class TestDokumenModel:
    """Test model Dokumen."""

    async def _create_prereqs(self, db_session: AsyncSession):
        """Helper: buat sekolah + siswa + admin untuk test."""
        from app.models.sekolah import Sekolah
        from app.models.siswa import Siswa
        from app.models.admin import Admin, AdminRole
        now = datetime.now(timezone.utc)

        sekolah = Sekolah(nama="SK Dok", kode="SKDOK01",
                          master_key_hash="hash", created_at=now, updated_at=now)
        db_session.add(sekolah)
        await db_session.flush()

        siswa = Siswa(nis="DOK001", nama_lengkap="Test Siswa",
                      sekolah_id=sekolah.id, created_at=now, updated_at=now)
        db_session.add(siswa)
        await db_session.flush()

        admin = Admin(
            username="admin_test", email="admin@test.id",
            nama_lengkap="Admin Test", password_hash="hash",
            role=AdminRole.ADMIN, sekolah_id=sekolah.id,
            created_at=now, updated_at=now,
        )
        db_session.add(admin)
        await db_session.flush()

        return sekolah, siswa, admin

    async def test_create_dokumen(self, db_session: AsyncSession):
        """Buat dokumen dengan semua field wajib."""
        from app.models.dokumen import Dokumen, JenisDokumen, SemesterEnum, StatusDokumen
        now = datetime.now(timezone.utc)
        _, siswa, admin = await self._create_prereqs(db_session)

        dok = Dokumen(
            siswa_id=siswa.id,
            jenis_dok=JenisDokumen.IJAZAH,
            tahun_ajaran="2023/2024",
            semester=SemesterEnum.FULL,
            file_path_encrypted="bucket/path/encrypted.bin",
            file_hash_sha256="a" * 64,
            key_wrapped="base64encodedwrappedkey==",
            uploaded_by=admin.id,
            created_at=now,
            updated_at=now,
        )
        db_session.add(dok)
        await db_session.flush()

        assert dok.id is not None
        assert dok.status == StatusDokumen.DRAFT
        assert dok.versi == 1

    async def test_dokumen_unique_per_siswa_jenis_tahun_semester(
        self, db_session: AsyncSession
    ):
        """Satu siswa tidak bisa punya 2 dokumen dengan jenis+tahun+semester sama."""
        from app.models.dokumen import Dokumen, JenisDokumen, SemesterEnum
        from sqlalchemy.exc import IntegrityError
        now = datetime.now(timezone.utc)
        _, siswa, _ = await self._create_prereqs(db_session)

        kwargs = dict(
            siswa_id=siswa.id,
            jenis_dok=JenisDokumen.RAPORT,
            tahun_ajaran="2023/2024",
            semester=SemesterEnum.GANJIL,
            file_path_encrypted="path1",
            file_hash_sha256="b" * 64,
            key_wrapped="key1",
            created_at=now,
            updated_at=now,
        )
        dok1 = Dokumen(**kwargs)
        dok2 = Dokumen(**{**kwargs, "file_path_encrypted": "path2", "file_hash_sha256": "c" * 64})

        db_session.add(dok1)
        await db_session.flush()

        db_session.add(dok2)
        with pytest.raises(IntegrityError):
            await db_session.flush()


class TestAuditLogModel:
    """Test model AuditLog."""

    async def test_create_audit_log(self, db_session: AsyncSession):
        """Buat audit log entry."""
        from app.models.audit_log import AuditLog, UserType, AuditStatus
        now = datetime.now(timezone.utc)

        log = AuditLog(
            user_type=UserType.SYSTEM,
            action="login",
            status=AuditStatus.SUCCESS,
            ip_address="127.0.0.1",
            created_at=now,
        )
        db_session.add(log)
        await db_session.flush()

        assert log.id is not None
        assert log.created_at is not None


class TestNotifikasiModel:
    """Test model Notifikasi."""

    async def test_notifikasi_cascade_delete(self, db_session: AsyncSession):
        """Hapus siswa harus menghapus notifikasinya (CASCADE)."""
        from app.models.sekolah import Sekolah
        from app.models.siswa import Siswa
        from app.models.notifikasi import Notifikasi, TipeNotifikasi
        now = datetime.now(timezone.utc)

        s = Sekolah(nama="Notif Test", kode="SKNOTIF1",
                    master_key_hash="h", created_at=now, updated_at=now)
        db_session.add(s)
        await db_session.flush()

        siswa = Siswa(nis="N001", nama_lengkap="Notif Siswa",
                      sekolah_id=s.id, created_at=now, updated_at=now)
        db_session.add(siswa)
        await db_session.flush()

        notif = Notifikasi(
            siswa_id=siswa.id,
            tipe=TipeNotifikasi.SISTEM,
            judul="Test",
            pesan="Pesan test",
            created_at=now,
        )
        db_session.add(notif)
        await db_session.flush()
        notif_id = notif.id

        # Hapus siswa → notifikasi harus ikut terhapus (CASCADE)
        await db_session.delete(siswa)
        await db_session.flush()

        result = await db_session.execute(
            select(Notifikasi).where(Notifikasi.id == notif_id)
        )
        assert result.scalar_one_or_none() is None, "Notifikasi harus terhapus cascade"


class TestIndexValidation:
    """Validasi Pydantic schemas."""

    def test_siswa_schema_valid(self):
        from app.schemas.sekolah_schemas import SiswaCreate
        s = SiswaCreate(
            nis="12345",
            nama_lengkap="Test Siswa",
            sekolah_id=1,
            jenis_kelamin="L",
            angkatan=2022,
        )
        assert s.nis == "12345"

    def test_siswa_jenis_kelamin_invalid(self):
        from app.schemas.sekolah_schemas import SiswaCreate
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            SiswaCreate(
                nis="001",
                nama_lengkap="Test",
                sekolah_id=1,
                jenis_kelamin="X",  # Tidak valid
            )

    def test_dokumen_tahun_ajaran_format(self):
        from app.schemas.sekolah_schemas import DokumenCreate
        # Format valid
        d = DokumenCreate(
            siswa_id=1,
            jenis_dok="ijazah",
            tahun_ajaran="2023/2024",
        )
        assert d.tahun_ajaran == "2023/2024"

    def test_dokumen_tahun_ajaran_invalid(self):
        from app.schemas.sekolah_schemas import DokumenCreate
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            DokumenCreate(
                siswa_id=1,
                jenis_dok="ijazah",
                tahun_ajaran="2023-2024",  # Format salah
            )

    def test_admin_password_weak(self):
        from app.schemas.sekolah_schemas import AdminCreate
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            AdminCreate(
                username="admin1",
                email="admin@test.id",
                nama_lengkap="Admin",
                password="weakpassword",  # Tidak ada huruf kapital, angka, atau spesial
            )
