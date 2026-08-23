# 🎨 DMS Sekolah — Panduan Desain UI/UX (v1.1)

Dokumen ini mendefinisikan standar estetika, struktur tata letak, dan sistem token desain yang wajib dipatuhi oleh developer dalam mengimplementasikan antarmuka pengguna (UI/UX) pada aplikasi **DMS Sekolah**. 

Setiap bagian ditandai dengan tag `[TAG]` sebagai acuan implementasi.

---

## 💎 [DESIGN_SYSTEM] — Sistem Desain Terpadu

> [!IMPORTANT]
> Token warna, skala tipografi, dan sistem spacing di bawah ini berlaku identik untuk seluruh portal (Admin, Guru, Staf, dan Siswa). Jangan gunakan nilai *hardcoded* di luar token sistem ini.

### 🎨 [COLORS] — Token Warna Utama

| Token | Nilai Hex | Peruntukan Utama | Contoh Penerapan |
| :--- | :--- | :--- | :--- |
| **`--color-brand-900`** | `#0A2E1F` | Dark Forest Green | Latar belakang halaman login |
| **`--color-brand-800`** | `#0F3D29` | Deep Forest Green | Sidebar utama admin/siswa |
| **`--color-brand-700`** | `#14503C` | Classic Forest Green | Topbar / Navbar background |
| **`--color-brand-600`** | `#1A6B50` | Medium Forest Green | Hover state menu navigasi |
| **`--color-brand-500`** | `#208C68` | Bright Forest Green | Border fokus input, ikon aktif |
| **`--color-brand-400`** | `#3DB891` | Mint Teal | Tombol utama (CTA), badge sukses |
| **`--color-brand-300`** | `#7AD4B8` | Light Mint | Aksen ilustrasi, tautan hover |
| **`--color-brand-200`** | `#B8EAD9` | Pale Mint | Garis pembatas ringan, highlight |
| **`--color-brand-100`** | `#E0F5EE` | Soft Mint | Latar belakang kartu sukses / preview |
| **`--color-brand-5`** | `#F0FAF6` | Mint Ghost | Efek hover baris tabel |

### ⚪ [NEUTRALS] — Warna Netral & Permukaan

| Token | Nilai Hex | Peruntukan Utama | Contoh Penerapan |
| :--- | :--- | :--- | :--- |
| **`--color-neutral-950`** | `#0D0F0E` | Jet Black | Teks judul utama (heading) |
| **`--color-neutral-800`** | `#1F2421` | Charcoal | Teks body utama, label |
| **`--color-neutral-600`** | `#4A5350` | Muted Gray | Teks sekunder, deskripsi |
| **`--color-neutral-400`** | `#8FA39B` | Light Gray | Placeholder, status disabled |
| **`--color-neutral-200`** | `#D4DDD9` | Border Gray | Border komponen, divider |
| **`--color-neutral-100`** | `#EDF2F0` | Row Alt | Latar belakang tabel selang-seling |
| **`--color-neutral-50`** | `#F5F8F7` | Soft Gray | Latar belakang halaman dashboard |
| **`--color-surface`** | `#FFFFFF` | Pure White | Latar belakang kartu (card), modal, input |

### 📊 [PASTEL_CARDS] — Warna Kartu Statistik

| Kartu Statistik | BG Hex | FG Hex | Icon Hex | Penerapan |
| :--- | :--- | :--- | :--- | :--- |
| **Total Dokumen** | `#DFF2EC` | `#0F4C39` | `#1A7A5E` | Pastel Mint |
| **Total Siswa** | `#DDE9F8` | `#1A3D6B` | `#2563EB` | Pastel Blue |
| **Unduhan Hari Ini** | `#EDE0F8` | `#4A1D7A` | `#7C3AED` | Pastel Lavender |
| **Anomali Aktif** | `#FDE8D8` | `#7A2D0F` | `#C2410C` | Pastel Peach |
| **Unggahan Bulan Ini** | `#FCEEDD` | `#78350F` | `#D97706` | Pastel Amber |
| **Status Master Key** | `#E0F0E0` | `#14532D` | `#15803D` | Pastel Sage |

---

## 🔤 [TYPOGRAPHY] — Token Tipografi

> [!NOTE]
> Gunakan kombinasi Google Fonts berikut untuk menyeimbangkan nilai formalitas akademis dan estetika modern:
> - **Plus Jakarta Sans:** Font display tebal dan geometris untuk Judul Halaman dan Widget Stat.
> - **DM Sans:** Font sans-serif netral dengan keterbacaan tinggi untuk Label, Input, dan Paragraf.
> - **DM Mono:** Font monospaced bersih untuk Token Enkripsi, Hash, dan Data Teknis.

```css
/* Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --font-display: 'Plus Jakarta Sans', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'DM Mono', monospace;
}
```

### Skala Tipografi & Penerapan

| Token / Kelas | Ukuran | Tebal (Weight) | Keluarga Font | Penerapan Utama |
| :--- | :--- | :--- | :--- | :--- |
| Judul Utama | `clamp(28px, 4vw, 36px)` | `800` (Extra Bold) | Display | Judul besar halaman masuk / login |
| Judul Halaman | `24px` | `700` (Bold) | Display | Judul halaman portal, halaman master |
| Judul Widget | `17px` | `600` (Semi Bold) | Display | Judul kartu panel, judul tabel |
| Nilai Statistik | `clamp(26px, 3.5vw, 34px)`| `800` (Extra Bold) | Display | Angka utama pada kartu statistik |
| Teks Utama | `15px` | `400` (Regular) | Body | Paragraf deskripsi, isi tabel |
| Teks Muted / Label | `13px` | `500` (Medium) | Body | Label form input, teks pembantu |
| Badge / Metadata | `11px` | `600` (Semi Bold) | Body | Status badge, tanggal log |

---

## 📏 [SPACING_SHADOW] — Tata Jarak, Radius & Efek Bayangan

### 1. Jarak Grid & Padding (Sistem Kelipatan 4px)
- **`--space-2` (8px):** Jarak antar elemen mikro (label ke input, icon ke teks).
- **`--space-4` (16px):** Padding dalam button, jarak antar input form.
- **`--space-6` (24px):** Padding dalam card, jarak antar kolom grid.
- **`--space-8` (32px):** Jarak vertikal antar bagian besar, padding modal utama.

### 2. Radius Lengkungan (Border Radius)
- **`--radius-sm` (6px):** Badge status kecil, input checkbox.
- **`--radius-md` (12px):** Tombol aksi, input field standar, tag pill.
- **`--radius-lg` (20px):** Kartu dashboard, widget info utama.
- **`--radius-xl` (28px):** Dialog modal konfirmasi, panel blob login kiri.

### 3. Efek Bayangan (Shadows)
- **`--shadow-sm`:** `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` (Garis batas melayang tipis).
- **`--shadow-md`:** `0 4px 16px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)` (Hover state kartu dashboard).
- **`--shadow-lg`:** `0 12px 40px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.06)` (Latar belakang modal/popover).
- **`--shadow-glow`:** `0 0 0 3px rgba(61, 184, 145, 0.30)` (Ring fokus berwarna mint teal).

---

## 🔐 [LOGIN_PAGE] — Halaman Masuk

### 1. Struktur Layout
Halaman menggunakan tata letak split 50/50 untuk desktop (`md` breakpoint ke atas). Di bawah resolusi tersebut, panel kiri otomatis disembunyikan.

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│              PANEL KIRI               │              PANEL KANAN              │
│               (Width: 50%)            │               (Width: 50%)            │
│  Latar: Dark Forest (--color-brand-900)│  Latar: Dark Forest (--color-brand-900)│
│                                       │                                       │
│   ┌──────────────────────────────┐    │           ┌──────────────────────┐    │
│   │ CARD ORGANIK (bg-white)      │    │           │ FORM LOGIN           │    │
│   │                              │    │           │                      │    │
│   │  [Logo Sekolah]              │    │           │  [Heading & Tagline] │    │
│   │  [Nama Sekolah]              │    │           │                      │    │
│   │                              │    │           │  [Form Input NIS]    │    │
│   │   ┌───────────────────────┐  │    │           │  [Form Input Sandi]  │    │
│   │   │  ILUSTRASI SVG        │  │    │           │                      │    │
│   │   │  Dokumen Aman &       │  │    │           │  [Tombol Masuk]      │    │
│   │   │  NeuralKeyGen         │  │    │           │                      │    │
│   │   └───────────────────────┘  │    │           └──────────────────────┘    │
│   │                              │    │                                       │
│   │  [Footer Copyright]          │    │          [Terms & Policy Footer]      │
│   └──────────────────────────────┘    │                                       │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

### 2. Spesifikasi Detail Panel Kiri
- **Card Putih Organik:**
  - Latar belakang menggunakan `--color-surface` (#FFFFFF) dengan lengkungan khusus di sisi kanan (`border-radius: 28px 60% 55% 28px / 28px 55% 60% 28px`).
  - Animasi melayang tipis (`animate-float`) diterapkan pada elemen card untuk memberikan kesan dinamis.
- **Ilustrasi SVG Keamanan:**
  - Ilustrasi vector datar modern dengan aksen warna brand-400 (Mint) dan neutral-800. Menggambarkan manajemen dokumen, kunci/gembok enkripsi, dan berkas akademik.
- **Floating Mini-Cards:**
  - **Card Kanan Atas:** Tulisan "Dokumen Terenkripsi ✓", latar belakang `--color-brand-700`, teks putih, dengan efek animasi mengambang lambat (`animate-float`).
  - **Card Kiri Bawah:** Tulisan "NeuralKeyGen 🔑", latar belakang putih, border `--color-brand-200`, teks `--color-brand-700`.

### 3. Spesifikasi Detail Panel Kanan (Form Input)
- **Glassmorphism Input:**
  - Latar belakang input menggunakan warna transparan putih tipis `rgba(255,255,255,0.08)` dan border `rgba(255,255,255,0.12)`.
  - Fokus state mengganti border menjadi `--color-brand-400` dan menambah glow ring.
- **Autofill Safe Styling:**
  - Teks ketikan wajib terlihat putih bersih (`#FFFFFF`). Untuk mencegah browser menimpa warna teks menjadi hitam saat pengisian otomatis (autofill), gunakan aturan CSS berikut:
  ```css
  .dms-input-dark:-webkit-autofill {
    -webkit-text-fill-color: #FFFFFF !important;
    -webkit-box-shadow: 0 0 0px 1000px #0A2E1F inset !important;
  }
  ```

---

## 🖥️ [DASHBOARD_PAGE] — Halaman Utama & Portal

### 1. Struktur Layout Portal
- **Navbar (Topbar):** Tinggi tetap `60px` dengan latar belakang `--color-brand-700` (`#14503C`). Berisi logo, nama "DMS Sekolah", menu navigasi inline (pada tablet/desktop), dan dropdown avatar profil siswa/admin.
- **Sidebar:** Lebar `220px` dengan latar belakang `--color-brand-800` (`#0F3D29`). Menyajikan menu vertikal dengan indikator status aktif berupa garis vertikal mint teal di sisi paling kiri item navigasi yang dipilih.

### 2. Tata Letak Dashboard 2-Kolom

```
┌────────────────────────────────────────────────────────┬──────────────────────────────┐
│  KIRI (Width: 100% / lg: 70%)                          │ KANAN (Width: 100% / lg: 30%)│
│                                                        │                              │
│  [GREETING BANNER]                                     │ [NOTIFIKASI FEED]            │
│  - Forest Green background gradient                    │ - Aktivitas real-time siswa  │
│  - Nama, Kelas, NIS dengan warna teks kontras          │ - Status anomali berdenyut   │
│                                                        │                              │
│  [CHART WIDGET]                                        │ [QUICK ACTIONS]              │
│  - Recharts bar chart 2-warna (Upload vs Download)     │ - Grid tombol aksi 2x2       │
│  - Tooltip dengan background gelap brand-800           │ - Efek hover border mint     │
│                                                        │                              │
│  [TABLE DOKUMEN]                                       │                              │
│  - Judul dokumen & status badge berwarna               │                              │
│  - Baris hover dengan efek warna Mint Ghost (#F0FAF6)  │                              │
└────────────────────────────────────────────────────────┴──────────────────────────────┘
```

- **Tabel & Badge Status:**
  - Desain baris tabel minimalis tanpa garis vertikal (*borderless grid*).
  - Badge jenis dokumen menggunakan warna pastel yang serasi:
    - **Rapor:** bg `#DFF2EC`, fg `#0F4C39`
    - **Ijazah:** bg `#FCEEDD`, fg `#78350F`
    - **Transkrip:** bg `#EDE0F8`, fg `#4A1D7A`
    - **Lainnya:** bg `#DDE9F8`, fg `#1A3D6B`
  - Badge status verifikasi menggunakan warna semantik (Hijau untuk Disetujui, Amber untuk Menunggu Review, Merah untuk Ditolak).

---

## 🎬 [MOTION] — Transisi & Animasi Keyframes

Semua interaksi mikro wajib menggunakan transisi bernilai durasi dinamis guna menjaga antarmuka terasa hidup dan responsif.

```css
@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}

@keyframes float {
  from { transform: translateY(0px) rotate(-2deg); }
  to   { transform: translateY(-6px) rotate(2deg); }
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%      { transform: scale(0.8); opacity: 0.5; }
}

/* Transisi Default */
.interactive-element {
  transition: all 150ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## ✅ [CHECKLIST_UIUX] — Panduan Verifikasi Mandiri

Sebelum menyelesaikan pekerjaan, pastikan seluruh poin di bawah ini telah tercentang:

- [ ] **Warna Konsisten:** Tidak ada kode warna Hex acak di file halaman; semua merujuk ke CSS variables.
- [ ] **Aksesibilitas Teks:** Keterbacaan warna font memenuhi standar kontras (khususnya input teks saat mengetik wajib berwarna putih kontras).
- [ ] **Ikon Sejenis:** Pustaka ikon seragam menggunakan `@heroicons/react` v2 (outline untuk sekunder, solid untuk widget aktif).
- [ ] **Responsivitas Tata Letak:** Semua halaman dicoba pada ukuran layar Mobile (lebar 360px), Tablet (768px), dan Desktop (1280px) tanpa terjadi patahan elemen atau teks bertumpuk.
- [ ] **Batas Melengkung:** Radius sudut mengikuti skala (Input/Button 12px, Card 20px, Modal 28px).

---
*DESIGN.md — DMS Sekolah v1.1 · Terintegrasi Forest Green + Mint Aesthetic*
