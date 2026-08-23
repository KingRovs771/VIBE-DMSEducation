# PRD.md — Product Requirements Document
## DMS Sekolah — Sistem Manajemen Dokumen Akademik
### dengan Enkripsi NeuralKeyGen (ML-Based)

---

> **Versi:** 1.1.1  
> **Tanggal:** 22 Agustus 2026  
> **Status:** Active Development  
> **Dibaca oleh:** AI coding assistant — baca seluruh dokumen sebelum menulis kode apapun  
>
> **Dokumen terkait:**
> - `DESIGN.md` — layout, warna, komponen UI
> - `NeuralKeyGen_DMS_Sekolah.ipynb` — training model ML
> - `DESIGN_DMS_Sekolah.docx` — arsitektur teknis lengkap

---

## Cara Membaca Dokumen Ini

Dokumen ini menggunakan tag `[TAG]` sebagai referensi silang antar bagian.  
Setiap fitur punya ID (`F-XXX`) dan acceptance criteria (`AC-XXX-N`) yang langsung bisa dijadikan test case.  
Ikuti urutan bab — setiap bagian membangun di atas bagian sebelumnya.

| Tag | Isi | Panduan AI |
|-----|-----|------------|
| `[OVERVIEW]` | Tujuan, problem, solusi | Pahami konteks sebelum kode apapun |
| `[ACTORS]` | Siapa yang pakai sistem | Tentukan JWT role & middleware permission |
| `[FEATURES]` | Fitur + acceptance criteria | Jadikan unit & integration test pada level kode |
| `[USER_STORIES]` | Narasi use-case | Gunakan sebagai referensi logika bisnis — **bukan** skenario browser test |
| `[DATA_MODEL]` | Tabel, kolom, relasi, index | Generate schema SQL & ORM model langsung |
| `[API_CONTRACT]` | Endpoint, request, response | Implement route handler & schema Pydantic |
| `[SECURITY]` | Aturan keamanan wajib | **Non-negotiable** — tidak boleh dilewati |
| `[ALGO]` | Spesifikasi NeuralKeyGen | Implement persis sesuai spec |
| `[NFR]` | Non-functional requirements | Validasi performa, availability, backup |
| `[CONSTRAINTS]` | Batasan sistem | Validasi di semua layer |
| `[GLOSSARY]` | Definisi istilah | Gunakan penamaan ini konsisten di kode |

---

## [AI_WORKFLOW] — Aturan Kerja AI Developer

> ⚠️ **WAJIB DIIKUTI.** AI harus mengikuti alur kerja ini pada setiap perubahan kode.

### 1. Uji Testing — Hanya Level Kode

**AI DILARANG melakukan:**
- Membuka browser untuk menguji tampilan atau alur UI
- Menggunakan browser automation (Playwright, Puppeteer, Selenium, dsb.)
- Melakukan screenshot atau mengklik elemen UI secara langsung
- Menjalankan E2E test berbasis browser apapun

**AI WAJIB melakukan pengujian hanya melalui:**
- `npx tsc --noEmit` — TypeScript type checking
- Unit test fungsi/class Python dengan `pytest` (jika ada)
- Integration test API menggunakan `curl` atau `httpx` langsung ke endpoint di backend
- Memeriksa log container untuk memastikan tidak ada error runtime
- Membaca response dari `docker compose logs` untuk validasi perilaku kode

### 2. Deploy — Wajib ke Docker Container

**Setelah setiap perubahan kode pada backend atau frontend, AI WAJIB langsung menjalankan:**

```bash
# Untuk perubahan backend (Python/FastAPI):
docker compose restart backend

# Untuk perubahan frontend (Next.js/TypeScript):
docker compose restart frontend

# Untuk perubahan keduanya sekaligus:
docker compose restart backend frontend

# Verifikasi container berjalan dengan baik:
docker compose logs --tail=20 backend
docker compose logs --tail=20 frontend
```

**Aturan deploy:**
- Jangan tunggu instruksi dari user untuk restart — langsung deploy setelah kode selesai ditulis
- Verifikasi container kembali dalam status `Up` setelah restart
- Jika ada error pada log container, perbaiki dulu sebelum melaporkan ke user
- Jangan pernah menyuruh user menjalankan `docker compose restart` sendiri jika AI bisa melakukannya

---

## [OVERVIEW] — Gambaran Produk

---

## [IMPLEMENTATION_STATUS] — Status Implementasi Fitur

> **Terakhir diperbarui:** 22 Agustus 2026  
> **Legenda:** ✅ Selesai · 🔄 Sebagian · ❌ Belum Dimulai

---

### Backend (FastAPI + PostgreSQL)

| # | Modul / Endpoint | Status | Catatan |
|---|-----------------|--------|---------|
| 1 | **Autentikasi Siswa** — `POST /auth/siswa/login`, refresh token, logout | ✅ | JWT, Argon2id, account lock 5x salah, blacklist token |
| 2 | **Autentikasi Admin** — `POST /auth/admin/login`, refresh, logout, OTP setup | ✅ | TOTP 2FA via `pyotp`, QR Code onboarding |
| 3 | **Dokumen Siswa** — `GET /dokumen/saya`, preview, download | ✅ | Fetch asli dari MinIO + dekripsi AES-256-GCM on-the-fly |
| 4 | **Admin Dokumen** — Upload, list, update metadata, delete, preview | ✅ | Upload langsung ke MinIO terenkripsi; preview baca file asli |
| 5 | **Admin Siswa** — CRUD siswa, bulk import Excel, filter & search | ✅ | Import Excel via `openpyxl`; generate password dari tgl lahir |
| 6 | **Audit Trail** — `GET /admin/audit-log` dengan filter | ✅ | Immutable log setiap aksi download, upload, login |
| 7 | **Dashboard Statistik** — `GET /admin/statistik` | ✅ | Total siswa, dokumen, download, anomali |
| 8 | **Verifikasi QR Code** — `GET /verify/{token}` (publik) | ✅ | HMAC-SHA256 signed token, halaman HTML visual keaslian |
| 9 | **Watermark + QR PDF** — Disematkan saat download | ✅ | `fitz` (PyMuPDF); nama siswa + NIS + timestamp + QR URL |
| 10 | **Enkripsi NeuralKeyGen** — AES-256-GCM + HKDF + RSA-4096 | ✅ | `crypto.py`; encrypt, decrypt, wrap_key, rotate |
| 11 | **SINDAS Integration** — Pull data siswa dari API SINDAS eksternal | ✅ | `GET /sindas/pull`, webhook, sync-logs, sync-status |
| 12 | **Jenis Dokumen (Kategori)** — CRUD kategori dokumen | ✅ | `GET /admin/kategori` |
| 13 | **Tahun Ajaran** — CRUD + set default | ✅ | `GET/POST/PUT /admin/tahun-ajaran` |
| 14 | **Master Key Management** — Generate, rotasi, status | ✅ | Terintegrasi penuh dengan background task re-wrapping |
| 15 | **Anomali Detection** — Scoring akses mencurigakan | ✅ | Detektor ML Isolation Forest & LSTM aktif di middleware, terintegrasi ke dashboard |
| 16 | **Notifikasi Email** — Email saat dokumen tersedia | ❌ | Model `notifikasi.py` ada; SMTP belum dikonfigurasi |
| 17 | **Bulk Upload Dokumen** — Upload massal via ZIP | ✅ | Mengekstrak ZIP dan memetakan PDF otomatis menggunakan nama berkas `NISN_Kategori.pdf` |

---

### Frontend (Next.js + TypeScript)

| # | Halaman / Komponen | Status | Catatan |
|---|-------------------|--------|---------|
| 1 | **Login Siswa** — `/login` | ✅ | Desain premium, animasi framer-motion, toast notif |
| 2 | **Dashboard Siswa** — `/dashboard` | ✅ | Statistik dokumen, notifikasi, quick actions |
| 3 | **Dokumen Saya** — `/dokumen` | ✅ | Tabel dokumen, filter status, preview PDF modal, download |
| 4 | **Profil Siswa** — `/profil` | ✅ | Edit profil, ganti password |
| 5 | **Login Admin** — `/admin/login` | ✅ | Login email+password+OTP TOTP |
| 6 | **Dashboard Admin** — `/admin/dashboard` | ✅ | Statistik, grafik dokumen, audit log terbaru |
| 7 | **Manajemen Siswa** — `/admin/siswa` | ✅ | Tabel siswa, CRUD, import Excel, drawer dokumen per siswa, preview |
| 8 | **Upload Dokumen** — `/admin/upload` | ✅ | Form upload dengan progress bar |
| 9 | **Audit Log** — `/admin/audit-log` | ✅ | Tabel log dengan filter tipe user, aksi, status |
| 10 | **Jenis Dokumen** — `/admin/jenis-dokumen` | ✅ | CRUD kategori dokumen |
| 11 | **Tahun Ajaran** — `/admin/tahun-ajaran` | ✅ | CRUD + set tahun ajaran default |
| 12 | **Master Key** — `/admin/master-key` | ✅ | UI selesai dan terintegrasi penuh dengan backend |
| 13 | **SINDAS Sync** — `/admin/sindas` | ✅ | Halaman sync + status + log riwayat |
| 14 | **Halaman Verifikasi QR** | ✅ | Dibuat langsung oleh backend sebagai HTML response |

---

### Infrastruktur & DevOps

| # | Komponen | Status | Catatan |
|---|----------|--------|---------|
| 1 | **Docker Compose** — Multi-container orchestration | ✅ | Backend, Frontend, PostgreSQL, MinIO, Redis, Nginx |
| 2 | **MinIO** — Object storage terenkripsi | ✅ | Bucket `dms-documents` untuk file `.enc` |
| 3 | **PostgreSQL 16** | ✅ | ORM SQLAlchemy async, migrasi Alembic |
| 4 | **Nginx** — Reverse proxy + SSL termination | ✅ | Port 80/443, routing ke backend & frontend |
| 5 | **Redis** — Token blacklist & session cache | ✅ | Dipakai untuk invalidasi JWT logout |
| 6 | **Structlog** — Structured logging JSON | ✅ | Semua endpoint menggunakan structured logger |

---



### Problem Statement

Sekolah menyimpan dokumen akademik siswa (ijazah, rapor, transkrip) secara fisik dan tidak terstruktur. Kondisi ini menimbulkan masalah nyata:

1. **Alumni kesulitan mendapatkan dokumen** — harus datang langsung ke sekolah, antre, dan menunggu berhari-hari.
2. **Risiko kehilangan dokumen fisik** — bencana, kebakaran, atau sekadar salah simpan.
3. **Pemalsuan mudah dilakukan** — tidak ada sistem verifikasi digital yang bisa dicek pihak ketiga.
4. **Tidak ada audit trail** — tidak diketahui siapa yang akses atau menyebarkan dokumen.
5. **Enkripsi tidak ada** — file digital yang ada tersimpan tanpa proteksi apapun.

### Solusi

DMS Sekolah adalah platform web yang memungkinkan:
- **Sekolah** mengupload dan mengelola dokumen akademik siswa secara terenkripsi
- **Alumni/Siswa** mengakses dokumen kapan saja, dari mana saja, secara aman
- **Pihak ketiga** memverifikasi keaslian dokumen via QR Code tanpa perlu login

Keunikan sistem ini adalah algoritma **NeuralKeyGen** — neural network yang menghasilkan kunci enkripsi unik per siswa dari profil mereka, tanpa pernah menyimpan kunci di database.

### Tujuan Bisnis

| Tujuan | Metrik Sukses | Target 6 Bulan |
|--------|---------------|----------------|
| Alumni bisa akses dokumen mandiri | % alumni akses tanpa bantuan TU | > 80% |
| Kurangi permintaan fisik ke sekolah | Jumlah kunjungan fisik per bulan | Turun 70% |
| Zero dokumen terpalsukan | Insiden pemalsuan terdeteksi | 0 |
| Waktu dapatkan dokumen | Dari datang → dokumen di tangan | < 5 menit (dari hari kerja) |

### Scope

**Dalam jangkauan (v1.0):**
- Upload & enkripsi: Rapor Semester 1–6, Ijazah, Transkrip Nilai, Surat Keterangan Nilai Rapor (SKNR)
- Portal alumni/siswa: login, preview, download dengan watermark dinamis
- Portal admin sekolah: upload, kelola dokumen & siswa, audit log
- Hierarki kunci enkripsi: Master Key (sekolah) + Student Key (NeuralKeyGen)
- Verifikasi keaslian dokumen via QR Code (publik, tanpa login)
- Notifikasi email saat dokumen baru tersedia

**Di luar jangkauan v1.0:**
- Integrasi Dapodik / SIAP / sistem pemerintah
- Aplikasi mobile native (iOS/Android) — cukup responsive web
- Pembayaran atau transaksi keuangan apapun
- Multi-bahasa (hanya Bahasa Indonesia)
- Chat atau komunikasi antara siswa dan admin

---

## [ACTORS] — Pengguna Sistem

### Daftar Aktor

| Aktor | Nama Role di JWT | Cara Login | Hak Utama |
|-------|-----------------|------------|-----------|
| Siswa / Alumni | `siswa` | NIS + Password | Akses dokumen milik sendiri |
| Admin Sekolah | `admin` | Email + Password + OTP | Upload, kelola dokumen semua siswa |
| TU Sekolah | `tu_sekolah` | Email + Password + OTP | Upload dokumen, edit metadata & file, kelola siswa sekolahnya |
| Dinas Pendidikan | `dinas_pendidikan` | Email + Password + OTP | Read-Only monitoring & verifikasi sekolah binaan |
| Kepala Sekolah | `kepala_sekolah` | Email + Password + OTP | Semua admin + laporan eksekutif |
| Super Admin | `super_admin` | Email + Password + OTP + IP Whitelist | Kelola Master Key, rotasi kunci |

### Permission Matrix

| Aksi | siswa | admin | tu_sekolah | dinas_pendidikan | kepala_sekolah | super_admin |
|------|-------|-------|------------|------------------|----------------|-------------|
| Login | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lihat dokumen milik sendiri | ✓ | — | — | — | — | — |
| Download dokumen milik sendiri | ✓ | — | — | — | — | — |
| Lihat semua dokumen sekolahnya | ✗ | ✓ | ✓ | — | ✓ | ✓ |
| Lihat dokumen sekolah binaan | ✗ | — | — | ✓ (Read-only) | — | — |
| Upload dokumen (single/bulk) | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Edit dokumen (verifikasi dekripsi) | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Hapus dokumen (soft delete) | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Tambah / edit siswa sekolahnya | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Lihat audit log sekolahnya | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| Hapus audit log | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Lihat laporan statistik | ✗ | ✓ | ✓ | ✓ (Binaan) | ✓ | ✓ |
| Generate / Rotasi Master Key | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Lihat anomali score | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |

> ⚠️ **ATURAN AI:** Setiap endpoint WAJIB dicek role-nya via middleware **sebelum** handler dijalankan. Jangan pernah return data dokumen tanpa verifikasi `siswa_id` pada token JWT == `siswa_id` pada dokumen di database.

---

## [FEATURES] — Fitur & Acceptance Criteria

> Format acceptance criteria: **AC-{feature_id}-{nomor}**  
> Setiap AC adalah satu test case **level kode** (unit/integration test via API atau pytest) yang harus lulus sebelum fitur dianggap selesai.  
> **AI DILARANG** memvalidasi AC melalui browser. Gunakan `curl`, `httpx`, log container, atau TypeScript compiler.

---

### [x] F-001 · Autentikasi Siswa

**Deskripsi:** Siswa/alumni login menggunakan NIS dan password untuk mendapatkan JWT token.

**Input:** `{ nis: string, password: string }`  
**Output:** `{ access_token: string (exp: 1h), refresh_token: string (exp: 7d), user: {...} }`

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-001-1 | NIS valid + password benar | HTTP 200, return token pair |
| AC-001-2 | NIS tidak terdaftar | HTTP 404, pesan generik ("NIS atau password salah") — **jangan expose** "NIS tidak ditemukan" |
| AC-001-3 | Password salah | HTTP 401, pesan generik sama seperti AC-001-2 |
| AC-001-4 | Password salah 5x berturut | HTTP 423, akun terkunci 30 menit, catat di audit_log |
| AC-001-5 | Login saat akun terkunci | HTTP 423 + info "sisa waktu kunci: N menit" |
| AC-001-6 | NIS dengan karakter non-numerik | HTTP 422, validasi gagal |
| AC-001-7 | Access token expired | HTTP 401, frontend redirect ke login |
| AC-001-8 | Refresh token valid → request access token baru | HTTP 200, access_token baru |
| AC-001-9 | Refresh token setelah logout (blacklist) | HTTP 401 |
| AC-001-10 | Login berhasil → dicatat di audit_log | Record dengan action: "login", status: "success" |

---

### [x] F-002 · Autentikasi Admin

**Deskripsi:** Admin login dengan email + password + OTP 6 digit yang dikirim via email.

**Input Step 1:** `{ email, password }` → kirim OTP ke email  
**Input Step 2:** `{ email, otp_code }` → return JWT  
**Output:** `{ access_token, refresh_token, user: { role } }`

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-002-1 | Kredensial benar + OTP valid | HTTP 200, return token dengan role |
| AC-002-2 | OTP expired (> 5 menit) | HTTP 401, "OTP kadaluarsa, kirim ulang" |
| AC-002-3 | OTP salah 3x | HTTP 423, lockout 15 menit + alert email ke admin lain |
| AC-002-4 | Super Admin login dari IP bukan whitelist | HTTP 403, "Akses dari IP ini tidak diizinkan" |
| AC-002-5 | OTP format bukan 6 digit angka | HTTP 422 |
| AC-002-6 | Request OTP baru saat OTP lama masih aktif | Invalidate OTP lama, kirim OTP baru |

---

### [x] F-003 · Upload Dokumen (Admin)

**Deskripsi:** Admin mengupload file PDF ke profil siswa tertentu. File dienkripsi sebelum disimpan.

**Input:** `multipart/form-data: { file: PDF, siswa_id, jenis_dok, tahun_ajaran, semester? }`

**Proses internal (urutan wajib):**
1. Validasi format file (magic bytes, bukan hanya ekstensi) & ukuran ≤ 10MB
2. Hitung SHA-256 hash file asli
3. Cek duplikat: hash + siswa_id + jenis_dok + semester sudah ada?
4. Generate Student Key via NeuralKeyGen (dari profil siswa)
5. Enkripsi file: AES-256-GCM (nonce unik 16 bytes)
6. Upload ciphertext ke MinIO: `{nonce}{tag}{ciphertext}` dalam satu objek
7. Wrap Student Key dengan Master Key RSA (simpan `key_wrapped` di DB)
8. Simpan metadata ke tabel `dokumen`
9. Kirim notifikasi email ke siswa (via Celery task)
10. Catat di audit_log

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-003-1 | Upload PDF valid, siswa ada | HTTP 201, `{ doc_id, file_hash_sha256 }` |
| AC-003-2 | File bukan PDF (cek magic bytes) | HTTP 422, "Hanya file PDF yang diterima" |
| AC-003-3 | File > 10MB | HTTP 413, "Ukuran file melebihi batas 10MB" |
| AC-003-4 | siswa_id tidak ada di database | HTTP 404, "Siswa tidak ditemukan" |
| AC-003-5 | Duplikat dokumen (hash sama, siswa sama, jenis sama, semester sama) | HTTP 409, "Dokumen identik sudah ada" |
| AC-003-6 | Upload berhasil → notifikasi email terkirim | Email terkirim dalam 60 detik |
| AC-003-7 | Upload gagal di tengah proses (koneksi putus) | Rollback: file MinIO dihapus, record DB tidak ada |
| AC-003-8 | Upload berhasil → record di audit_log | action: "upload", admin_id, doc_id, status: "success" |
| AC-003-9 | jenis_dok tidak valid (bukan enum) | HTTP 422 |
| AC-003-10 | semester diisi untuk jenis ijazah/transkrip | HTTP 422, "Semester tidak berlaku untuk jenis ini" |

---

### [x] F-004 · Lihat Daftar Dokumen (Siswa)

**Deskripsi:** Siswa yang login melihat semua dokumen milik dirinya, terfilter dan terurut.

**Output:** List dokumen `[{ id, jenis_dok, semester, tahun_ajaran, created_at, ukuran }]`

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-004-1 | Siswa A request daftar dokumen | Hanya return dokumen milik siswa A |
| AC-004-2 | Siswa A coba akses `GET /siswa/dokumen?siswa_id=B` | Parameter siswa_id dari token, bukan query — return milik A |
| AC-004-3 | Siswa belum punya dokumen | HTTP 200, `data: []` (bukan 404) |
| AC-004-4 | Filter jenis_dok=rapor | Hanya return dokumen jenis rapor |
| AC-004-5 | Filter tahun_ajaran=2024/2025 | Hanya return tahun tersebut |
| AC-004-6 | Sort by created_at DESC | Dokumen terbaru di atas |

---

### [x] F-005 · Download Dokumen dengan Watermark (Siswa)

**Deskripsi:** Siswa mendownload dokumen miliknya. File di-dekripsi, ditambah watermark dinamis dan QR Code, lalu distream ke browser.

**Proses internal:**
1. Verifikasi JWT + cek ownership: `dokumen.siswa_id == jwt.sub`
2. Cek rate limit: maks 10 download per jam per dokumen per siswa
3. Ambil file terenkripsi dari MinIO
4. Regenerate Student Key via NeuralKeyGen (dari profil siswa — **tidak dari DB**)
5. Dekripsi: AES-256-GCM dengan nonce dari prefiks file
6. Verifikasi integritas: SHA-256 hash hasil dekripsi == `dokumen.file_hash_sha256`
7. Tambah watermark diagonal di setiap halaman
8. Embed QR Code verifikasi di halaman pertama
9. Stream PDF ke browser sebagai attachment
10. Catat di audit_log

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-005-1 | Siswa A download dokumen miliknya | HTTP 200, stream PDF |
| AC-005-2 | Siswa A coba download dokumen siswa B | HTTP 403, "Akses ditolak" |
| AC-005-3 | Download lebih dari 10x dalam 1 jam | HTTP 429, "Batas download tercapai. Coba lagi dalam N menit" |
| AC-005-4 | PDF hasil download punya watermark di setiap halaman | Watermark diagonal, opacity 15%, teks: nama + NIS + tanggal |
| AC-005-5 | QR Code ada di pojok kanan bawah halaman pertama | QR Code 2cm×2cm, scan → URL verifikasi valid |
| AC-005-6 | Hash hasil dekripsi tidak cocok (file rusak) | HTTP 500, "File tidak dapat dibuka. Hubungi admin." + alert ke admin |
| AC-005-7 | Download berhasil → catat audit_log | action: "download", siswa_id, doc_id, IP, user_agent |
| AC-005-8 | Token siswa sudah logout, coba download | HTTP 401 |

---

### [x] F-006 · Preview Dokumen Online (Siswa)

**Deskripsi:** Siswa melihat preview PDF di browser tanpa mendownload (inline viewer).

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-006-1 | Preview dokumen milik sendiri | HTTP 200, stream PDF inline (content-disposition: inline) |
| AC-006-2 | Preview dokumen siswa lain | HTTP 403 |
| AC-006-3 | Preview **tidak** menambah watermark | PDF preview sama dengan aslinya (watermark hanya saat download) |
| AC-006-4 | Preview tidak dicatat di audit_log sebagai "download" | Log action: "preview", bukan "download" |

---

### [x] F-007 · Verifikasi Dokumen via QR Code (Publik)

**Deskripsi:** Pihak ketiga (perusahaan, instansi) scan QR Code untuk verifikasi keaslian tanpa login.

**Endpoint:** `GET /verify/{token}` — publik, tidak butuh auth  

**QR Token payload (JWT signed HMAC-SHA256):**
```json
{
  "doc_id": "uuid",
  "siswa_id": "uuid",
  "jenis_dok": "ijazah",
  "downloaded_at": "ISO8601",
  "exp": "ISO8601 + 365 hari"
}
```

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-007-1 | Token valid, dokumen ada | HTTP 200, `{ valid: true, doc_info: { jenis, sekolah, siswa_name_masked, tanggal } }` |
| AC-007-2 | Token signature dimanipulasi | HTTP 200, `{ valid: false, reason: "Dokumen tidak valid atau telah dimodifikasi" }` |
| AC-007-3 | Token expired (> 365 hari) | HTTP 200, `{ valid: false, reason: "Token kadaluarsa" }` |
| AC-007-4 | Nama siswa di response | Disamarkan: "B*** S******" (hanya huruf pertama per kata) |
| AC-007-5 | Setiap verifikasi dicatat di audit_log | action: "verify_qr", aktor_type: "external", IP |
| AC-007-6 | Tidak butuh login untuk akses | HTTP 200 tanpa Authorization header |

---

### [x] F-008 · Manajemen Siswa (Admin)

**Deskripsi:** Admin mengelola data siswa: tambah, edit, import massal dari Excel.

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-008-1 | Tambah siswa baru | HTTP 201, sistem generate `entropy_seed` otomatis (CSPRNG), simpan ke DB |
| AC-008-2 | NIS sudah ada | HTTP 409, "NIS sudah terdaftar" |
| AC-008-3 | Import Excel valid (kolom: NIS, nama, tgl_lahir, kelas, tahun_masuk) | HTTP 202, return `job_id`, proses async |
| AC-008-4 | Import Excel ada baris error (NIS duplikat) | Skip baris error, import yang valid, return laporan error per baris |
| AC-008-5 | Edit email/telepon siswa | HTTP 200, data diupdate, enkripsi ulang |
| AC-008-6 | Hapus siswa (soft delete) | HTTP 200, `is_active = false`, dokumen tetap ada di storage |

---

### [x] F-009 · Manajemen Master Key (Super Admin)

**Deskripsi:** Super Admin mengelola Master Key RSA-4096 yang dipakai untuk meng-wrap Student Key.

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-009-1 | Lihat status Master Key | HTTP 200, `{ version, created_at, total_dokumen_terdampak }` |
| AC-009-2 | Generate Master Key pertama | HTTP 201, key pair dibuat, public key disimpan di DB, private key di vault |
| AC-009-3 | Rotasi Master Key (re-wrap semua dokumen) | HTTP 202, async job berjalan, semua `key_wrapped` di-re-enkripsi dengan MK baru |
| AC-009-4 | Rotasi gagal di tengah | Rollback ke MK versi sebelumnya, alert ke Super Admin |
| AC-009-5 | Akses endpoint MK dari IP bukan whitelist | HTTP 403 |
| AC-009-6 | Rotasi berhasil → catat audit_log | action: "key_rotation", old_version, new_version |

---

### [x] F-010 · Audit Trail (Admin)

**Deskripsi:** Semua aktivitas sistem tercatat secara immutable dan bisa dilihat admin.

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-010-1 | Semua aksi user (login, download, upload, verify) tercatat | Record di audit_log setiap aksi |
| AC-010-2 | Admin coba hapus record audit_log | HTTP 403, "Audit log tidak dapat dihapus" (DB trigger enforce ini) |
| AC-010-3 | Filter log by tanggal + aktor + action | Hanya return record sesuai filter |
| AC-010-4 | Export audit_log ke Excel | HTTP 200, file .xlsx download |
| AC-010-5 | Anomali score > 0.7 dicatat | Flag di kolom `anomaly_score`, masuk ke list anomali |

---

### [x] F-011 · Notifikasi Email

**Deskripsi:** Sistem mengirim email otomatis pada event tertentu.

| Event | Penerima | Isi Email |
|-------|----------|-----------|
| Dokumen baru diupload | Siswa | "Dokumen [jenis] Anda telah tersedia. Login untuk akses." |
| Login gagal 3x | Siswa | "Percobaan login gagal. Jika bukan Anda, hubungi sekolah." |
| Akun terkunci | Siswa | "Akun terkunci N menit karena 5x gagal login." |
| OTP admin | Admin | "Kode OTP Anda: XXXXXX (berlaku 5 menit)" |
| Anomali terdeteksi | Semua admin | "Akses mencurigakan terdeteksi dari IP X.X.X.X" |
| Rotasi Master Key selesai | Super Admin | "Rotasi Master Key v{N} berhasil. Total dokumen: N." |

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-011-1 | Upload berhasil → email siswa | Email terkirim dalam 60 detik |
| AC-011-2 | Email gagal terkirim | Retry 3x dengan backoff, catat error di log |
| AC-011-3 | Siswa belum punya email | Skip notifikasi, log warning |

---

### [x] F-012 · Dashboard Statistik (Admin / Kepala Sekolah)

**Deskripsi:** Halaman statistik dengan angka dan grafik aktivitas sistem.

**Data yang tersedia:**

| Metrik | Deskripsi | Periode |
|--------|-----------|---------|
| Total siswa aktif | COUNT siswa.is_active = true | Realtime |
| Total dokumen | COUNT dokumen.is_active = true | Realtime |
| Upload per bulan | GROUP BY month(created_at) | 12 bulan terakhir |
| Download per hari | GROUP BY date(created_at) | 30 hari terakhir |
| Akses per jenis dokumen | GROUP BY jenis_dok | Realtime |
| Anomali aktif | COUNT anomaly_score > 0.7 | Realtime |
| Siswa belum punya dokumen | LEFT JOIN siswa-dokumen | Realtime |

### [x] F-013 · Proteksi Edit & Anti-Tampering (Supervisi Dinas)

**Deskripsi:** Alur pembaruan berkas/metadata dokumen yang mewajibkan verifikasi dekripsi kriptografi dan perlindungan checksum hash untuk menolak dokumen yang dimanipulasi secara eksternal. Serta monitoring dinas pendidikan atas sekolah binaan.

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-013-1 | Edit dokumen → dekripsi berkas lama sukses + SHA256 cocok | HTTP 200, update berhasil, catat audit log |
| AC-013-2 | Edit dokumen → dekripsi berkas lama gagal (kunci/file rusak) | HTTP 409, error code DOC_INTEGRITY |
| AC-013-3 | Edit dokumen → hash SHA256 berkas didekripsi tidak cocok dengan DB | HTTP 409, error code DOC_INTEGRITY |
| AC-013-4 | Dinas Pendidikan melihat kepatuhan sekolah non-binaan | HTTP 403 Forbidden |
| AC-013-5 | Dinas Pendidikan mendownload dokumen sekolah binaan | HTTP 200, stream PDF + watermark pengawasan khusus + log alasan_akses |

---

### [x] F-014 · Proteksi PDF yang Didownload (PDF Permissions)

**Deskripsi:** PDF yang didownload oleh siswa atau dinas harus dilindungi dari editing, copying teks, dan print kualitas tinggi menggunakan **PDF permission flags** (AES-128). Ini berbeda dari enkripsi storage (AES-256-GCM di MinIO) yang melindungi file saat disimpan.

**Dua lapisan enkripsi yang terpisah:**

| Lapisan | Target | Teknologi | Tujuan |
|---------|--------|-----------|--------|
| Storage Encryption | File `.enc` di MinIO | AES-256-GCM (NeuralKeyGen) | Melindungi data saat istirahat di server |
| PDF Permission Protection | PDF yang didownload | PyMuPDF PDF Encrypt | Mencegah editing/copy oleh penerima dokumen |

**Spesifikasi PDF Permission Flags:**
- ✅ Boleh: Baca (read), Print kualitas rendah (draft)
- ❌ Dilarang: Edit konten, Copy teks, Print kualitas tinggi, Isi form, Tambah anotasi

**Parameter enkripsi:**
- Algorithm: AES-128 (PDF 1.6+)
- User password: kosong (langsung bisa dibuka)
- Owner password: diderivasi dari `HMAC-SHA256(doc_id + siswa_id + SECRET_KEY)` — tidak pernah diketahui user
- Permission bits: `PDF_PERM_PRINT` only (bukan `PDF_PERM_MODIFY`, bukan `PDF_PERM_COPY`)

| AC | Skenario | Expected Result |
|----|----------|-----------------|
| AC-014-1 | Download dokumen — buka di Adobe/Foxit | PDF terbuka tanpa password, tapi tombol Edit/Copy nonaktif |
| AC-014-2 | Coba edit PDF hasil download di Foxit Editor | Foxit menolak dengan pesan "File ini dilindungi" |
| AC-014-3 | Coba copy teks dari PDF di Adobe Reader | Copy teks tidak bisa |
| AC-014-4 | Print dari Adobe Reader | Hanya print kualitas draft (72dpi) yang diizinkan |
| AC-014-5 | Download oleh Dinas — PDF pakai watermark dinas + permission locked | HTTP 200, PDF tidak bisa diedit |
| AC-014-6 | Preview siswa (inline) | Tidak dilindungi permission (hanya untuk tampilan cepat) |

---

## [USER_STORIES] — Narasi Use-Case

> Format: **Sebagai [aktor], saya ingin [aksi], sehingga [tujuan bisnis].**  
> ⚠️ **Panduan AI:** User stories ini digunakan sebagai referensi logika bisnis dan penentuan endpoint API. AI **TIDAK** menggunakannya sebagai skenario E2E browser test. Validasi dilakukan melalui API integration test dan code review.

| ID | User Story | Prioritas | Feature |
|----|------------|-----------|---------|
| US-01 | Sebagai alumni, saya ingin login dengan NIS agar bisa akses dokumen saya kapan saja tanpa harus ke sekolah | P1 · MVP | F-001 |
| US-02 | Sebagai alumni, saya ingin melihat semua dokumen akademik saya dalam satu halaman agar mudah ditemukan | P1 · MVP | F-004 |
| US-03 | Sebagai alumni, saya ingin preview ijazah di browser untuk memastikan dokumen yang benar sebelum download | P2 | F-006 |
| US-04 | Sebagai alumni, saya ingin download rapor dengan watermark nama saya agar aman dibagikan ke perusahaan | P1 · MVP | F-005 |
| US-05 | Sebagai alumni, saya ingin mendapat notifikasi email saat transkrip saya tersedia agar tidak perlu cek manual | P2 | F-011 |
| US-06 | Sebagai alumni, saya ingin melihat riwayat kapan saya mengakses dokumen untuk memantau keamanan akun saya | P3 | F-010 |
| US-07 | Sebagai admin TU, saya ingin upload ijazah ke profil siswa tertentu agar mereka bisa akses sendiri | P1 · MVP | F-003 |
| US-08 | Sebagai admin TU, saya ingin upload rapor 1.200 siswa sekaligus via Excel mapping agar efisien | P2 | F-003 |
| US-09 | Sebagai admin TU, saya ingin melihat log siapa saja yang download dokumen agar ada accountability | P1 · MVP | F-010 |
| US-10 | Sebagai admin TU, saya ingin tambah data siswa baru dengan mudah agar onboarding cepat | P1 · MVP | F-008 |
| US-11 | Sebagai Super Admin, saya ingin generate Master Key baru dengan konfirmasi berlapis agar aman | P1 · MVP | F-009 |
| US-12 | Sebagai perusahaan HRD, saya ingin scan QR di ijazah pelamar untuk verifikasi keaslian tanpa perlu login ke sistem sekolah | P2 | F-007 |
| US-13 | Sebagai kepala sekolah, saya ingin melihat laporan berapa dokumen yang diakses per bulan sebagai bahan evaluasi | P3 | F-012 |
| US-14 | Sebagai alumni, saya ingin ganti password agar akun tetap aman | P1 · MVP | F-001 |
| US-15 | Sebagai admin, saya ingin melihat akses mencurigakan secara real-time agar bisa segera ditangani | P2 | F-010 |

---

## [DATA_MODEL] — Skema Database

> **Database:** PostgreSQL 16  
> **ORM:** SQLAlchemy (async)  
> **Migrations:** Alembic  
> **Aturan:** Semua timestamp pakai `TIMESTAMPTZ`. PK pakai `UUID` (gen_random_uuid()). Kolom sensitif dienkripsi di application layer sebelum masuk DB.

---

### Tabel: `sekolah`

```sql
CREATE TABLE sekolah (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    nama                VARCHAR(200) NOT NULL,
    npsn                VARCHAR(20)  UNIQUE NOT NULL,       -- Nomor Pokok Sekolah Nasional
    alamat              TEXT,
    email_kontak        VARCHAR(200),                      -- ENCRYPTED di app layer
    telp_kontak         VARCHAR(20),                       -- ENCRYPTED di app layer
    master_key_public   TEXT        NOT NULL,              -- RSA-4096 public key (PEM)
    master_key_version  INT         NOT NULL DEFAULT 1,    -- Naik saat rotasi
    is_active           BOOLEAN     NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### Tabel: `siswa`

```sql
CREATE TABLE siswa (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sekolah_id      UUID        NOT NULL REFERENCES sekolah(id),
    nis             VARCHAR(20) UNIQUE NOT NULL,            -- Login identifier
    nisn            VARCHAR(20) UNIQUE,                    -- Nomor nasional (opsional)
    nama_lengkap    TEXT        NOT NULL,                  -- ENCRYPTED di app layer
    nama_hash       VARCHAR(64) NOT NULL,                  -- SHA-256(lower(nama)) untuk NeuralKeyGen
    tgl_lahir       DATE        NOT NULL,                  -- Untuk NeuralKeyGen
    tahun_masuk     INT         NOT NULL,                  -- Untuk NeuralKeyGen
    kelas_terakhir  VARCHAR(20),                           -- Contoh: XII IPA 1
    email           VARCHAR(200),                          -- ENCRYPTED di app layer
    telepon         VARCHAR(20),                           -- ENCRYPTED di app layer
    password_hash   TEXT        NOT NULL,                  -- Argon2id
    entropy_seed    VARCHAR(64) NOT NULL UNIQUE,           -- 128-bit hex, CSPRNG saat registrasi
    reg_timestamp   BIGINT      NOT NULL,                  -- Unix epoch saat registrasi
    foto_path       TEXT,                                  -- ENCRYPTED, path di MinIO
    is_active       BOOLEAN     NOT NULL DEFAULT true,
    login_attempts  INT         NOT NULL DEFAULT 0,        -- Counter login gagal
    locked_until    TIMESTAMPTZ,                           -- Null = tidak terkunci
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index
CREATE INDEX idx_siswa_nis         ON siswa(nis);
CREATE INDEX idx_siswa_sekolah_id  ON siswa(sekolah_id);
CREATE INDEX idx_siswa_is_active   ON siswa(is_active) WHERE is_active = true;
```

---

### Tabel: `admin`

```sql
CREATE TABLE admin (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sekolah_id      UUID        NOT NULL REFERENCES sekolah(id),
    nama_lengkap    TEXT        NOT NULL,                  -- ENCRYPTED
    email           VARCHAR(200) UNIQUE NOT NULL,          -- ENCRYPTED, login identifier
    password_hash   TEXT        NOT NULL,                  -- Argon2id
    role            VARCHAR(30) NOT NULL,                  -- admin | kepala_sekolah | super_admin
    ip_whitelist    TEXT[],                                -- Hanya untuk super_admin
    otp_secret      TEXT,                                  -- TOTP secret (opsional), ENCRYPTED
    login_attempts  INT         NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    last_login      TIMESTAMPTZ,
    is_active       BOOLEAN     NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_admin_email      ON admin(email);
CREATE INDEX idx_admin_sekolah_id ON admin(sekolah_id);
```

---

### Tabel: `dokumen`

```sql
CREATE TABLE dokumen (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    siswa_id          UUID        NOT NULL REFERENCES siswa(id),
    jenis_dok         VARCHAR(20) NOT NULL                 -- ENUM: rapor | ijazah | transkrip | sknr
                      CHECK (jenis_dok IN ('rapor','ijazah','transkrip','sknr')),
    semester          INT         CHECK (semester BETWEEN 1 AND 6),  -- NULL untuk non-rapor
    tahun_ajaran      VARCHAR(10) NOT NULL,               -- Format: 2024/2025
    file_path_enc     TEXT        NOT NULL,               -- Path di MinIO, ENCRYPTED
    file_size_bytes   BIGINT      NOT NULL,               -- Ukuran file asli (sebelum enkripsi)
    file_hash_sha256  VARCHAR(64) NOT NULL,               -- Hash file ASLI untuk integritas
    key_wrapped       TEXT        NOT NULL,               -- Student Key di-wrap RSA Master Key
    mk_version        INT         NOT NULL,               -- Versi Master Key saat enkripsi
    metadata_json     JSONB       NOT NULL DEFAULT '{}',  -- { guru_wali, catatan, ttd_kepsek }
    uploaded_by       UUID        NOT NULL REFERENCES admin(id),
    is_active         BOOLEAN     NOT NULL DEFAULT true,  -- Soft delete
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraint duplikat: satu siswa tidak bisa punya 2 rapor semester sama di tahun sama
    UNIQUE (siswa_id, jenis_dok, semester, tahun_ajaran)
);

CREATE INDEX idx_dokumen_siswa_id   ON dokumen(siswa_id);
CREATE INDEX idx_dokumen_jenis      ON dokumen(jenis_dok);
CREATE INDEX idx_dokumen_created_at ON dokumen(created_at DESC);
CREATE INDEX idx_dokumen_active     ON dokumen(is_active) WHERE is_active = true;
```

---

### Tabel: `audit_log`

```sql
-- APPEND-ONLY — Tidak boleh ada UPDATE atau DELETE
CREATE TABLE audit_log (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    aktor_id        UUID        NOT NULL,                  -- siswa_id atau admin_id
    aktor_type      VARCHAR(20) NOT NULL                   -- siswa | admin | external
                    CHECK (aktor_type IN ('siswa','admin','external')),
    action          VARCHAR(30) NOT NULL,
                    -- login | logout | download | preview | upload | delete_doc
                    -- add_siswa | edit_siswa | verify_qr | key_rotation | key_generate
    dokumen_id      UUID        REFERENCES dokumen(id),    -- NULL jika bukan aksi dokumen
    ip_address      INET        NOT NULL,
    user_agent      TEXT,
    status          VARCHAR(10) NOT NULL                   -- success | failed | blocked
                    CHECK (status IN ('success','failed','blocked')),
    anomaly_score   FLOAT       NOT NULL DEFAULT 0.0,      -- 0.0–1.0 dari AnomalyDetector
    extra_json      JSONB       NOT NULL DEFAULT '{}',     -- error_msg, download_count, dsb
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index untuk query cepat
CREATE INDEX idx_audit_aktor_id   ON audit_log(aktor_id);
CREATE INDEX idx_audit_action     ON audit_log(action);
CREATE INDEX idx_audit_created_at ON audit_log(created_at DESC);
CREATE INDEX idx_audit_anomaly    ON audit_log(anomaly_score) WHERE anomaly_score > 0.5;

-- ENFORCE APPEND-ONLY di database level
CREATE RULE no_update_audit_log AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE RULE no_delete_audit_log AS ON DELETE TO audit_log DO INSTEAD NOTHING;
```

---

### Tabel: `notifikasi`

```sql
CREATE TABLE notifikasi (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    siswa_id    UUID        NOT NULL REFERENCES siswa(id),
    judul       VARCHAR(200) NOT NULL,
    pesan       TEXT        NOT NULL,
    is_read     BOOLEAN     NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_siswa_id ON notifikasi(siswa_id);
CREATE INDEX idx_notif_unread   ON notifikasi(siswa_id) WHERE is_read = false;
```

---

### Tabel: `dinas_sekolah_binaan`

```sql
CREATE TABLE dinas_sekolah_binaan (
    dinas_id    UUID        NOT NULL REFERENCES admin(id) ON DELETE CASCADE,
    sekolah_id  UUID        NOT NULL REFERENCES sekolah(id) ON DELETE CASCADE,
    PRIMARY KEY (dinas_id, sekolah_id)
);
```

---

### Tabel: `refresh_token_blacklist`

```sql
-- Token yang sudah di-logout atau di-revoke
CREATE TABLE refresh_token_blacklist (
    jti         VARCHAR(36) PRIMARY KEY,    -- JWT ID (uuid dari claim "jti")
    user_id     UUID        NOT NULL,
    revoked_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ NOT NULL        -- Sama dengan exp token
);

-- Hapus otomatis token yang sudah expired (cleanup job harian)
CREATE INDEX idx_rtb_expires ON refresh_token_blacklist(expires_at);
```

---

### Entity Relationship Diagram (Teks)

```
sekolah ─────────< admin        (sekolah.id = admin.sekolah_id)
sekolah ─────────< siswa        (sekolah.id = siswa.sekolah_id)
siswa   ─────────< dokumen      (siswa.id = dokumen.siswa_id)
siswa   ─────────< notifikasi   (siswa.id = notifikasi.siswa_id)
admin   ─────────< dokumen      (admin.id = dokumen.uploaded_by)
dokumen ─────────< audit_log    (dokumen.id = audit_log.dokumen_id, nullable)
```

---

## [API_CONTRACT] — Kontrak API

> **Base URL:** `https://api.dms-sekolah.sch.id/v1`  
> **Format request:** `application/json` (kecuali upload: `multipart/form-data`)  
> **Format response selalu:**

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "timestamp": "2026-08-19T10:30:00Z"
}
```

> **Format error selalu:**

```json
{
  "success": false,
  "error_code": "UPLOAD_FORMAT",
  "message": "Hanya file PDF yang diterima",
  "details": null,
  "timestamp": "2026-08-19T10:30:00Z"
}
```

---

### Auth Endpoints

```
POST   /auth/login/siswa
  Body:   { nis: string, password: string }
  Return: { access_token, refresh_token, user: { id, nis, nama, role } }

POST   /auth/login/admin/step1
  Body:   { email: string, password: string }
  Return: { message: "OTP dikirim ke email Anda" }

POST   /auth/login/admin/step2
  Body:   { email: string, otp_code: string }
  Return: { access_token, refresh_token, user: { id, email, nama, role } }

POST   /auth/refresh
  Body:   { refresh_token: string }
  Return: { access_token: string }

POST   /auth/logout
  Header: Authorization: Bearer {access_token}
  Body:   { refresh_token: string }
  Return: { message: "Berhasil keluar" }

POST   /auth/reset-password/request
  Body:   { nis?: string, email?: string }
  Return: { message: "Link reset dikirim ke email" }

POST   /auth/reset-password/confirm
  Body:   { token: string, new_password: string }
  Return: { message: "Password berhasil diubah" }
```

---

### Siswa Endpoints

```
GET    /siswa/dokumen
  Header: Authorization: Bearer {siswa_token}
  Query:  ?jenis_dok=rapor&tahun_ajaran=2024/2025&sort=created_at&order=desc
  Return: { data: [ DokumenSummary ], total: int }

GET    /siswa/dokumen/{id}/preview
  Header: Authorization: Bearer {siswa_token}
  Return: application/pdf (inline stream) — PDF tanpa watermark

GET    /siswa/dokumen/{id}/download
  Header: Authorization: Bearer {siswa_token}
  Return: application/pdf (attachment) — PDF + watermark + QR Code

GET    /siswa/profil
  Header: Authorization: Bearer {siswa_token}
  Return: { id, nis, kelas_terakhir, tahun_masuk, email, telepon, last_login }

PATCH  /siswa/profil
  Header: Authorization: Bearer {siswa_token}
  Body:   { email?: string, telepon?: string }
  Return: updated profil

PATCH  /siswa/profil/password
  Header: Authorization: Bearer {siswa_token}
  Body:   { current_password: string, new_password: string }
  Return: { message: "Password berhasil diubah" }

GET    /siswa/notifikasi
  Header: Authorization: Bearer {siswa_token}
  Return: [ { id, judul, pesan, is_read, created_at } ]

PATCH  /siswa/notifikasi/{id}/read
  Header: Authorization: Bearer {siswa_token}
  Return: { message: "Ditandai sudah dibaca" }
```

---

### Admin — Dokumen Endpoints

```
POST   /admin/dokumen/upload
  Header: Authorization: Bearer {admin_token}
  Body:   multipart/form-data:
            file: File (PDF, max 10MB)
            siswa_id: UUID
            jenis_dok: rapor | ijazah | transkrip | sknr
            tahun_ajaran: string (format: YYYY/YYYY)
            semester: int (1-6, hanya untuk rapor)
            metadata_json: JSON string (opsional)
  Return: { doc_id: UUID, file_hash_sha256: string, created_at: ISO8601 }

POST   /admin/dokumen/upload-bulk
  Header: Authorization: Bearer {admin_token}
  Body:   multipart/form-data:
            zip_file: ZIP berisi PDF-PDF
            mapping_csv: CSV dengan kolom [filename, nis, jenis_dok, tahun_ajaran, semester]
  Return: { job_id: UUID, message: "Proses berjalan di background" }

GET    /admin/dokumen
  Header: Authorization: Bearer {admin_token}
  Query:  ?siswa_id=&jenis_dok=&tahun_ajaran=&page=1&limit=20
  Return: { data: [ DokumenDetail ], total: int, page: int }

GET    /admin/dokumen/{id}
  Header: Authorization: Bearer {admin_token}
  Return: DokumenDetail lengkap + metadata

PUT    /admin/dokumen/{id}
  Header: Authorization: Bearer {admin_token}
  Body:   { tahun_ajaran?: string, semester?: int, metadata_json?: object }
  Return: updated DokumenDetail
  Note:   Tidak bisa ubah file atau siswa_id

DELETE /admin/dokumen/{id}
  Header: Authorization: Bearer {admin_token}
  Body:   { alasan: string }   ← wajib isi alasan
  Return: { message: "Dokumen dihapus (soft delete)" }
```

---

### Admin — Siswa Endpoints

```
GET    /admin/siswa
  Header: Authorization: Bearer {admin_token}
  Query:  ?search=&tahun_masuk=&kelas=&page=1&limit=20
  Return: { data: [ SiswaSummary ], total: int, page: int }

POST   /admin/siswa
  Header: Authorization: Bearer {admin_token}
  Body:   { nis, nisn?, nama_lengkap, tgl_lahir, tahun_masuk, kelas_terakhir?, email?, telepon? }
  Return: { id: UUID, nis, entropy_seed_generated: true }

POST   /admin/siswa/import
  Header: Authorization: Bearer {admin_token}
  Body:   multipart/form-data: { excel_file: XLSX }
  Return: { job_id: UUID }

GET    /admin/siswa/{id}
  Header: Authorization: Bearer {admin_token}
  Return: SiswaDetail + [ DokumenSummary ]

PUT    /admin/siswa/{id}
  Header: Authorization: Bearer {admin_token}
  Body:   { kelas_terakhir?, email?, telepon? }
  Return: updated SiswaDetail

DELETE /admin/siswa/{id}
  Header: Authorization: Bearer {admin_token}
  Return: { message: "Siswa dinonaktifkan (soft delete)" }
```

---

### Admin — Audit & Monitoring Endpoints

```
GET    /admin/audit-log
  Header: Authorization: Bearer {admin_token}
  Query:  ?aktor_id=&action=&status=&from=ISO8601&to=ISO8601&page=1&limit=50
  Return: { data: [ AuditLog ], total: int, page: int }

GET    /admin/audit-log/export
  Header: Authorization: Bearer {admin_token}
  Query:  sama seperti di atas
  Return: application/vnd.xlsx (file Excel)

GET    /admin/anomali
  Header: Authorization: Bearer {admin_token}
  Query:  ?min_score=0.5&resolved=false&page=1&limit=20
  Return: { data: [ AnomalyRecord ], total: int }

GET    /admin/statistik
  Header: Authorization: Bearer {admin_token | kepala_sekolah_token}
  Return: {
    total_siswa: int, total_dokumen: int,
    download_hari_ini: int, anomali_aktif: int,
    upload_per_bulan: [ { bulan: string, jumlah: int } ],   // 12 bulan
    download_per_hari: [ { tanggal: string, jumlah: int } ], // 30 hari
    dokumen_per_jenis: { rapor: int, ijazah: int, transkrip: int, sknr: int }
  }
```

---

### Master Key Endpoints

```
GET    /admin/master-key/status
  Header: Authorization: Bearer {super_admin_token}
  Return: { version: int, created_at: ISO8601, total_dokumen: int }

POST   /admin/master-key/generate
  Header: Authorization: Bearer {super_admin_token}
  Body:   { confirm: "SAYA MENGERTI RISIKO INI" }   ← literal string konfirmasi
  Return: { message: "Master Key berhasil dibuat", version: 1 }
  Note:   Hanya bisa dipanggil jika belum ada MK (first time setup)

POST   /admin/master-key/rotate
  Header: Authorization: Bearer {super_admin_token}
  Body:   { confirm: "SAYA MENGERTI RISIKO INI", alasan: string }
  Return: { job_id: UUID, message: "Rotasi berjalan di background" }

GET    /admin/master-key/jobs/{job_id}
  Header: Authorization: Bearer {super_admin_token}
  Return: { status: pending|running|done|failed, progress: int, total: int, error?: string }
```

---

### Public Endpoints

```
GET    /verify/{token}
  Auth:   Tidak perlu
  Return: {
    valid: boolean,
    doc_info?: {
      jenis_dok: string,
      sekolah_nama: string,
      siswa_nama_masked: string,   // "B*** S******"
      downloaded_at: ISO8601,
    },
    reason?: string   // jika valid = false
  }

GET    /health
  Auth:   Tidak perlu
  Return: {
    status: "ok" | "degraded" | "down",
    services: {
      database: "ok" | "down",
      storage: "ok" | "down",
      redis: "ok" | "down",
      ml_model: "ok" | "down"
    },
    version: "1.0.0"
  }
```

---

## [SECURITY] — Aturan Keamanan Wajib

> ⚠️ **Semua poin di bawah adalah NON-NEGOTIABLE.**  
> AI WAJIB mengimplementasikan semua aturan ini. Tidak ada pengecualian.

---

### S-01 · Password Hashing

```
Algorithm: Argon2id
Parameters:
  m (memory): 65536 KB (64MB)
  t (iterations): 3
  p (parallelism): 4
  hash_len: 32 bytes

DILARANG: bcrypt, scrypt, MD5, SHA-1, SHA-256 langsung untuk password
Library Python: argon2-cffi
```

### S-02 · JWT

```
Algorithm: HS256 (minimum), RS256 lebih baik untuk production
Secret: Min 256-bit random (32 bytes), disimpan di env var JWT_SECRET_KEY
Access token TTL: 60 menit
Refresh token TTL: 7 hari
Claim wajib: sub (user_id), role, jti (UUID untuk blacklist), iat, exp
```

### S-03 · Transport Security

```
Protocol: TLS 1.3 (TLS 1.2 minimum, TLS 1.0/1.1 DISABLED)
Force HTTPS: Redirect semua HTTP → HTTPS
HSTS: Strict-Transport-Security: max-age=31536000; includeSubDomains
Certificate: Let's Encrypt (auto-renew via Certbot)
```

### S-04 · Rate Limiting

```
Konfigurasi di Nginx + Redis:

Endpoint                          Limit                      Window
/auth/login/siswa                 5 request per IP           1 menit
/auth/login/admin/step1           5 request per IP           1 menit
/auth/login/admin/step2           3 request per IP           5 menit
/siswa/dokumen/{id}/download      10 request per user        1 jam
/admin/dokumen/upload             100 request per admin      1 hari
/* (semua endpoint auth)          200 request per IP         1 menit

Response saat limit tercapai:
  HTTP 429 Too Many Requests
  Header: Retry-After: {seconds}
  Body: { error_code: "RATE_LIMITED", message: "...", retry_after_seconds: N }
```

### S-05 · Input Validation

```
Semua input WAJIB di-validate di Pydantic schema SEBELUM masuk ke business logic.
Jangan pernah trust input dari client.
Sanitasi: strip whitespace, cek panjang min/max, format regex.
File upload: cek magic bytes (bukan hanya ekstensi file)
  PDF magic bytes: %PDF- (hex: 25 50 44 46 2D)
```

### S-06 · SQL Injection Prevention

```
WAJIB gunakan SQLAlchemy ORM atau parameterized query.
DILARANG: string concatenation untuk query SQL.
Contoh DILARANG: f"SELECT * FROM siswa WHERE nis = '{nis}'"
Contoh BENAR:    db.query(Siswa).filter(Siswa.nis == nis).first()
```

### S-07 · File Upload Security

```
1. Cek ukuran SEBELUM membaca konten (tolak jika > 10MB)
2. Cek magic bytes SETELAH membaca 8 byte pertama
3. JANGAN simpan file asli — langsung enkripsi
4. Generate nama file di server (bukan dari input user)
5. Simpan di MinIO dengan bucket private (tidak public)
6. Path file dienkripsi sebelum disimpan di database
```

### S-08 · Enkripsi File

```
Algorithm: AES-256-GCM (authenticated encryption)
Nonce: os.urandom(16) — unik per file, BUKAN reuse
Format storage di MinIO: {nonce_16bytes}{tag_16bytes}{ciphertext}
Jangan simpan nonce terpisah — embed di awal file

Python:
  from Crypto.Cipher import AES
  cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
  ciphertext, tag = cipher.encrypt_and_digest(plaintext)
  storage_bytes = nonce + tag + ciphertext
```

### S-09 · Zero-Storage Key (NeuralKeyGen)

```
Student Key TIDAK BOLEH:
  ❌ Disimpan di database dalam bentuk apapun
  ❌ Di-log ke file log
  ❌ Dikirim melalui API ke frontend
  ❌ Disimpan di session atau cache

Student Key HANYA BOLEH:
  ✓ Dibuat ulang via NeuralKeyGen setiap kali dibutuhkan
  ✓ Hidup di memory proses selama proses enkripsi/dekripsi
  ✓ Di-wrap dengan Master Key (hasilnya = key_wrapped, ini yang disimpan)
  ✓ Di-zero-kan dari memory setelah digunakan: key = b'\x00' * len(key)
```

### S-10 · Master Key Storage

```
Private key RSA WAJIB disimpan di:
  Option A: Hardware Security Module (HSM) — production ideal
  Option B: HashiCorp Vault atau AWS Secrets Manager
  Option C: Docker secret (read-only mount di /run/secrets/) — minimum

DILARANG:
  ❌ Simpan di database
  ❌ Simpan di filesystem container (akan hilang saat restart)
  ❌ Hardcode di kode
  ❌ Commit ke git

Public key aman disimpan di database tabel sekolah.
```

### S-11 · Audit Log Immutability

```
Enforce di database level:
  CREATE RULE no_update_audit_log AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
  CREATE RULE no_delete_audit_log AS ON DELETE TO audit_log DO INSTEAD NOTHING;

Enforce di application level:
  Tidak ada endpoint DELETE /admin/audit-log/...
  Tidak ada fungsi delete di AuditService
  Semua operasi ke audit_log HANYA INSERT

Retensi: 7 tahun (sesuai regulasi pendidikan Indonesia)
```

### S-12 · Error Handling

```
Response ke client: pesan generik, tidak expose detail teknis
Log server: detail lengkap (stack trace, query, context) ke file log

DILARANG di response client:
  ❌ Stack trace Python
  ❌ Query SQL
  ❌ Nama tabel atau kolom database
  ❌ Path file sistem
  ❌ Versi library

WAJIB:
  ✓ error_code yang konsisten (lihat kode di bawah)
  ✓ Pesan yang helpful tapi aman untuk user
```

**Error Codes:**

| Kode | HTTP | Situasi |
|------|------|---------|
| `AUTH_INVALID` | 401 | Kredensial salah |
| `AUTH_EXPIRED` | 401 | Token expired |
| `AUTH_LOCKED` | 423 | Akun terkunci |
| `AUTH_FORBIDDEN` | 403 | Role tidak cukup |
| `AUTH_IP_BLOCKED` | 403 | IP tidak di whitelist |
| `DOC_NOT_FOUND` | 404 | Dokumen tidak ada |
| `DOC_FORBIDDEN` | 403 | Bukan dokumen milik user |
| `DOC_DUPLICATE` | 409 | Dokumen identik sudah ada |
| `DOC_INTEGRITY` | 500 | Hash tidak cocok, file mungkin rusak |
| `UPLOAD_FORMAT` | 422 | Bukan PDF |
| `UPLOAD_SIZE` | 413 | Melebihi batas ukuran |
| `UPLOAD_FAILED` | 500 | Gagal upload ke storage |
| `RATE_LIMITED` | 429 | Terlalu banyak request |
| `VALIDATION_ERROR` | 422 | Input tidak valid |
| `NOT_FOUND` | 404 | Resource tidak ditemukan |
| `SERVER_ERROR` | 500 | Error tidak terduga |

### S-13 · Security Headers

```nginx
# nginx.conf — tambahkan di server block
add_header X-Content-Type-Options    "nosniff" always;
add_header X-Frame-Options           "DENY" always;
add_header X-XSS-Protection         "1; mode=block" always;
add_header Referrer-Policy           "strict-origin-when-cross-origin" always;
add_header Permissions-Policy        "geolocation=(), microphone=(), camera=()" always;
add_header Content-Security-Policy   "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data:; connect-src 'self' api.dms-sekolah.sch.id;" always;
```

### S-14 · CORS

```python
# DILARANG: allow_origins=["*"]
# WAJIB: whitelist domain spesifik

app.add_middleware(CORSMiddleware,
    allow_origins=[
        "https://dms-sekolah.sch.id",
        "https://admin.dms-sekolah.sch.id",
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    allow_credentials=True,
)
```

---

## [ALGO] — Spesifikasi Algoritma NeuralKeyGen

### Kontrak Fungsi

```python
# Signature fungsi di produksi
def generate_student_key(siswa_profile: dict) -> bytes:
    """
    Input:
        siswa_profile: {
            nis: str,              # "20240001"
            tahun_masuk: int,      # 2024
            npsn: str,             # "NPSN00001"
            nama_hash: str,        # SHA-256(lower(nama_lengkap)).hexdigest()
            tgl_lahir: str,        # "2008-03-15"
            entropy_seed: str,     # 32-char hex, tersimpan di DB
            reg_timestamp: int,    # Unix epoch saat registrasi
        }

    Output:
        bytes[32] — kunci AES-256-GCM siap pakai

    Properti WAJIB:
        1. DETERMINISTIK: input identik → output identik (selamanya)
        2. ZERO-STORAGE: output tidak pernah disimpan
        3. COLLISION-FREE: P(collision) < 2^-128 untuk semua pasang siswa berbeda
        4. IRREVERSIBLE: tidak bisa recover input dari output
        5. LATENCY: < 5ms per call di CPU
    """
```

### Pipeline Enkripsi Lengkap

```
UPLOAD DOKUMEN:
Step 1  extract_features(siswa_profile)      → vektor 64 dimensi
Step 2  NeuralKeyGen.forward(features)       → raw output 256-dim sigmoid
Step 3  HKDF(raw_output, SYSTEM_SALT, 32)   → student_key (bytes[32])
Step 4  os.urandom(16)                       → nonce (bytes[16])
Step 5  AES.new(student_key, GCM, nonce)    → cipher
Step 6  cipher.encrypt_and_digest(file)     → ciphertext, tag
Step 7  storage = nonce + tag + ciphertext  → simpan ke MinIO
Step 8  RSA_OAEP.encrypt(student_key, MK)   → key_wrapped → simpan ke DB
Step 9  student_key = b'\x00' * 32          → zero-kan dari memory

DOWNLOAD DOKUMEN:
Step 1  extract_features(siswa_profile)      → vektor 64 dimensi (IDENTIK dengan upload)
Step 2  NeuralKeyGen.forward(features)       → raw output (IDENTIK)
Step 3  HKDF(raw_output, SYSTEM_SALT, 32)   → student_key (IDENTIK)
Step 4  baca file MinIO                      → storage bytes
Step 5  nonce = storage[:16]
        tag   = storage[16:32]
        ct    = storage[32:]
Step 6  AES.new(student_key, GCM, nonce)    → cipher
Step 7  cipher.decrypt_and_verify(ct, tag)  → plaintext
Step 8  SHA-256(plaintext) == file_hash_sha256?  → validasi integritas
Step 9  add_watermark(plaintext, siswa)     → pdf dengan watermark
Step 10 embed_qr_code(pdf, token)          → pdf final
Step 11 student_key = b'\x00' * 32         → zero-kan dari memory
```

### Model Info

```
File:         neuralkeygen.pt (PyTorch checkpoint)
Architecture: 3 Dense blocks (512→256→256) + BatchNorm + Dropout(0.3) + Sigmoid output
Input dim:    64
Output dim:   256
Trained on:   500.000 profil sintetis (BUKAN data siswa nyata)
Inference:    model.eval() + torch.no_grad() + lru_cache singleton
Target:       < 5ms per inference di CPU
```

---

## [NFR] — Non-Functional Requirements

### Performa

| Metrik | Target | Cara Ukur |
|--------|--------|-----------|
| API response (p95) | < 500ms | Prometheus histogram |
| API response (p99) | < 1000ms | Prometheus histogram |
| Download PDF (p95) | < 8 detik (termasuk dekripsi + watermark) | Prometheus |
| Upload + enkripsi (p95) | < 10 detik untuk file 10MB | Prometheus |
| NeuralKeyGen inference | < 5ms per call | Unit test timing |
| DB query (p95) | < 100ms | pg_stat_statements |
| Concurrent users | Min 100 siswa simultan | Load test dengan k6 |

### Availability

```
Target uptime: 99.5% per bulan (≈ 3.6 jam downtime/bulan)
Maintenance window: Minggu 02:00–04:00 WIB (umumkan 24 jam sebelum)
Health check: GET /health — Nginx kirim setiap 10 detik, restart jika gagal 3x
```

### Backup & Recovery

```
Backup database:
  Frekuensi: pg_dump harian (02:00 WIB), WAL archiving real-time
  Enkripsi:  AES-256 dengan kunci berbeda dari Master Key
  Destinasi: Local + MinIO bucket backup + cloud cold storage
  Retensi:   30 hari lokal, 7 tahun cloud (sesuai retensi audit_log)

Backup file dokumen:
  MinIO replication ke bucket secondary
  Verifikasi integritas mingguan (spot check hash)

Recovery:
  RTO (Recovery Time Objective):  < 4 jam
  RPO (Recovery Point Objective): < 1 jam
  Test restore: wajib dilakukan setiap bulan
```

### Monitoring

```
Stack: Prometheus + Grafana

Alert yang WAJIB dikonfigurasi:
  - Error rate > 1% dalam 5 menit → alert Telegram/email admin
  - p95 response time > 1 detik dalam 5 menit
  - Disk usage > 80%
  - RAM usage > 85%
  - Anomali score > 0.7 → alert ke admin sekolah
  - Rotasi Master Key gagal → alert critical ke Super Admin
  - Backup harian gagal → alert ke Super Admin
  - SSL certificate expire < 14 hari
```

---

## [CONSTRAINTS] — Batasan Sistem

| Kategori | Batasan | Konsekuensi Pelanggaran |
|----------|---------|------------------------|
| File | Maks 10MB per file | HTTP 413 |
| File | Format PDF saja | HTTP 422 |
| File | Maks 100 upload per admin per hari | HTTP 429 |
| Download | Maks 10x per jam per dokumen per siswa | HTTP 429 |
| Auth | Token expire 1 jam | HTTP 401, redirect login |
| Auth | Maks 5x login gagal → lockout 30 menit | HTTP 423 |
| Auth | OTP expire 5 menit | HTTP 401 |
| Storage | Audit log retensi 7 tahun | Tidak bisa dihapus |
| Storage | Dokumen: soft delete saja (tidak dihapus dari storage) | Tetap ada di MinIO |
| Browser | Chrome 90+, Firefox 88+, Safari 14+ | Tidak support IE, Edge Legacy |
| Mobile | Responsive min 360px, tanpa native app | Hanya progressive web |
| Enkripsi | SYSTEM_SALT tidak boleh berubah setelah production | Semua dokumen tidak bisa dibuka |
| NeuralKeyGen | entropy_seed tidak boleh berubah setelah registrasi | Kunci berubah, dokumen tidak bisa dibuka |

---

## [GLOSSARY] — Daftar Istilah

> Gunakan penamaan ini secara **konsisten** di seluruh kode: variabel, fungsi, tabel, endpoint, komentar.

| Istilah | Nama di Kode | Definisi |
|---------|-------------|----------|
| Master Key | `master_key` / `MK` | Pasangan kunci RSA-4096 milik sekolah. Public key tersimpan di DB, private key di vault. Bisa membuka semua dokumen. |
| Student Key | `student_key` / `SK` | Kunci AES-256 unik per siswa. Dihasilkan NeuralKeyGen dari profil siswa. **Tidak pernah disimpan.** |
| Wrapped Key | `key_wrapped` | Student Key yang dienkripsi dengan Master Key RSA (tersimpan di kolom `dokumen.key_wrapped`). |
| Entropy Seed | `entropy_seed` | String hex 32 karakter (128-bit), dibuat sekali saat registrasi dengan CSPRNG, tersimpan di `siswa.entropy_seed`. Memastikan keunikan antar siswa. |
| System Salt | `SYSTEM_SALT` | Konstanta bytes untuk HKDF, disimpan di environment variable. Tidak pernah berubah setelah produksi. |
| NeuralKeyGen | `NeuralKeyGenService` | Class singleton yang membungkus model PyTorch dan fungsi `generate_key()`. Dimuat sekali saat startup. |
| Jenis Dokumen | `jenis_dok` | Enum string: `rapor` \| `ijazah` \| `transkrip` \| `sknr` |
| SKNR | `sknr` | Surat Keterangan Nilai Rapor |
| Audit Log | `audit_log` | Tabel append-only yang mencatat semua aktivitas sistem. |
| Anomaly Score | `anomaly_score` | Float 0.0–1.0, output AnomalyDetector ML. > 0.5 = monitor, > 0.7 = blokir dan alert. |
| Watermark | `watermark` | Teks diagonal semi-transparan pada setiap halaman PDF yang didownload. Berisi nama + NIS + tanggal. |
| QR Token | `qr_token` | JWT payload verifikasi yang di-embed dalam QR Code di halaman pertama PDF. |
| Key Rotation | `key_rotation` | Proses generate Master Key baru dan re-wrap semua `key_wrapped` dokumen yang ada. |
| Soft Delete | `is_active = false` | Dokumen/siswa tidak dihapus dari DB/storage, hanya ditandai tidak aktif. |
| Feature Vector | `features` | Vektor numpy 64 dimensi hasil encoding profil siswa, input ke NeuralKeyGen. |
| CSPRNG | — | Cryptographically Secure Pseudo-Random Number Generator. Pakai `secrets.token_hex()` di Python. |
| DEK | `student_key` | Data Encryption Key — kunci yang dipakai langsung untuk enkripsi file (dalam sistem ini = Student Key). |
| KEK | `master_key` | Key Encryption Key — kunci yang mengenkripsi DEK (dalam sistem ini = Master Key RSA). |

---

## Lampiran — Environment Variables Wajib

```bash
# .env.example — copy ke .env dan isi semua nilai

# ─── DATABASE ─────────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://dms_user:GANTI_PASS@postgres:5432/dms_sekolah
POSTGRES_PASSWORD=GANTI_DENGAN_RANDOM_32_CHAR

# ─── JWT ──────────────────────────────────────────────────────────────
JWT_SECRET_KEY=GANTI_DENGAN_RANDOM_64_CHAR_HEX
JWT_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=7

# ─── NEURALKEYGEN ─────────────────────────────────────────────────────
SYSTEM_SALT=DMS_SEKOLAH_SALT_v1_GANTI_INI_JANGAN_UBAH_SETELAH_PROD
NEURAL_MODEL_PATH=/app/ml_model/neuralkeygen.pt

# ─── STORAGE ──────────────────────────────────────────────────────────
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=GANTI
MINIO_SECRET_KEY=GANTI_DENGAN_RANDOM_32_CHAR
MINIO_BUCKET_DOCS=dms-documents
MINIO_BUCKET_BACKUP=dms-backup
MINIO_USE_SSL=false

# ─── REDIS ────────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ─── EMAIL ────────────────────────────────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dms@sekolah.sch.id
SMTP_PASSWORD=GANTI_DENGAN_APP_PASSWORD
EMAIL_FROM_NAME=DMS Sekolah

# ─── SECURITY ─────────────────────────────────────────────────────────
ALLOWED_ORIGINS=https://dms-sekolah.sch.id,https://admin.dms-sekolah.sch.id
SUPERADMIN_IP_WHITELIST=203.x.x.x,10.x.x.x
MASTER_KEY_VAULT_PATH=/run/secrets/master_key_private

# ─── APP ──────────────────────────────────────────────────────────────
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_UPLOAD_MB=10
APP_URL=https://dms-sekolah.sch.id
API_URL=https://api.dms-sekolah.sch.id
```

---

*PRD.md — DMS Sekolah v1.1 · Dibuat untuk AI Developer · Baca bersama DESIGN.md*  
*Revisi v1.1: Tambah [AI_WORKFLOW] — larangan browser test, kewajiban deploy ke Docker setelah setiap perubahan kode.*
