# 📚 DMS Sekolah — Document Management System

> Platform digital untuk pengelolaan dokumen sekolah yang aman, terorganisir, dan cerdas dengan integrasi **NeuralKeyGen** berbasis PyTorch.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3-EE4C2C?style=flat&logo=pytorch)](https://pytorch.org)
[![MinIO](https://img.shields.io/badge/MinIO-latest-C72E49?style=flat&logo=minio)](https://min.io)

---

## 📐 Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Port 80/443)                  │
│               Reverse Proxy + SSL Termination           │
└──────────────────┬──────────────────┬───────────────────┘
                   │                  │
         ┌─────────▼──────┐  ┌────────▼─────────┐
         │  Next.js Front │  │  FastAPI Backend  │
         │   (Port 3000)  │  │    (Port 8000)    │
         └────────────────┘  └────────┬──────────┘
                                      │
              ┌───────────────────────┼─────────────────┐
              │                       │                 │
     ┌────────▼──────┐  ┌─────────────▼──┐  ┌──────────▼──────┐
     │  PostgreSQL   │  │     MinIO       │  │    Redis Cache  │
     │  (Port 5432)  │  │  (Port 9000)    │  │   (Port 6379)   │
     └───────────────┘  └────────────────┘  └─────────────────┘
                                      │
                            ┌─────────▼──────────┐
                            │  NeuralKeyGen ML    │
                            │  PyTorch Model      │
                            └─────────────────────┘
```

---

## 🗂️ Struktur Proyek

```
dms-sekolah/
├── backend/                          # FastAPI Python Backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── router.py             # Main API router
│   │   │   └── endpoints/
│   │   │       ├── auth.py           # Register, login, refresh
│   │   │       ├── documents.py      # Upload, download, search, approve
│   │   │       ├── users.py          # User management
│   │   │       └── categories.py     # Document categories
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic Settings
│   │   │   ├── database.py           # SQLAlchemy async engine
│   │   │   ├── security.py           # JWT + bcrypt
│   │   │   ├── neural_keygen.py      # 🧠 NeuralKeyGen wrapper
│   │   │   ├── minio_client.py       # MinIO async client
│   │   │   └── dependencies.py       # FastAPI deps (auth guards)
│   │   ├── models/
│   │   │   ├── user.py               # User model (roles: admin/guru/staf/siswa)
│   │   │   ├── document.py           # Document + Category + Version
│   │   │   └── activity_log.py       # Audit trail
│   │   ├── schemas/
│   │   │   ├── user.py               # Pydantic schemas (User, Auth)
│   │   │   └── document.py           # Pydantic schemas (Document, Category)
│   │   ├── services/
│   │   │   ├── auth_service.py       # Auth business logic
│   │   │   └── document_service.py   # Document business logic
│   │   └── ml/
│   │       └── model.py              # NeuralKeyGenModel (PyTorch)
│   ├── tests/
│   │   ├── conftest.py               # Pytest fixtures (SQLite in-memory)
│   │   ├── test_auth.py              # Auth endpoint tests
│   │   └── test_neural_keygen.py     # ML model tests
│   ├── alembic.ini                   # Database migration config
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                         # Next.js 14 + TypeScript + Tailwind
│   ├── pages/
│   │   ├── _app.tsx                  # App wrapper (QueryClient + Toast)
│   │   ├── index.tsx                 # Landing page
│   │   ├── login.tsx                 # Login page
│   │   └── dashboard.tsx             # Main dashboard
│   ├── components/
│   │   ├── UploadZone.tsx            # Drag-and-drop upload
│   │   └── DocumentCard.tsx          # Document card with status
│   ├── hooks/
│   │   └── useDocuments.ts           # React Query hooks
│   ├── lib/
│   │   └── api-client.ts             # Axios + JWT interceptors
│   ├── store/
│   │   └── authStore.ts              # Zustand auth state
│   ├── styles/
│   │   └── globals.css               # Tailwind + custom styles
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── next.config.js
│   └── Dockerfile
│
├── ml_model/                         # Standalone ML training
│   ├── train.py                      # Training pipeline
│   ├── utils.py                      # Preprocessing & evaluation
│   └── init_model.py                 # Inisialisasi model.pt awal
│
├── nginx/
│   └── nginx.conf                    # Reverse proxy config
│
├── docker-compose.yml                # Semua services
├── .env.example                      # Template environment variables
├── .gitignore
└── README.md
```

---

## 🧠 NeuralKeyGen

**NeuralKeyGen** adalah sistem unik yang menggunakan neural network untuk menghasilkan *document key* unik dari konten setiap dokumen.

### Arsitektur Model
```
Byte Sequence (512 bytes)
        ↓
   ByteEmbedding (Embedding Layer, dim=64)
        ↓
   Bi-LSTM Encoder (hidden=128, 2 layers) + Attention
        ↓
   Key Projector (FC → ReLU → Dropout → Sigmoid)
        ↓
   Document Key (32-dim hex string)
```

### Training
```bash
# 1. Install dependencies
pip install torch numpy scikit-learn

# 2. Inisialisasi model awal
cd ml_model
python init_model.py

# 3. Training dengan data dokumen sekolah
python train.py --data-dir ./data --epochs 50 --output model.pt

# 4. Evaluasi
python utils.py
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose v2
- (Opsional) Python 3.12, Node.js 20

### 1. Clone & Setup Environment
```bash
git clone <repo-url>
cd dms-sekolah

# Salin dan edit file .env
cp .env.example .env
# Edit .env sesuai konfigurasi Anda
```

### 2. Inisialisasi Model ML
```bash
cd ml_model
pip install torch numpy
python init_model.py   # Buat model.pt awal
cd ..
```

### 3. Jalankan Semua Services
```bash
docker compose up --build -d
```

### 4. Akses Aplikasi
| Service | URL | Keterangan |
|---|---|---|
| Frontend | http://localhost | Aplikasi utama |
| API Docs | http://localhost/api/docs | Swagger UI |
| MinIO Console | http://localhost:9001 | Object storage admin |
| Metrics | http://localhost/metrics | Prometheus metrics |

### 5. Migrasi Database
```bash
docker compose exec backend alembic upgrade head
```

---

## 🛠️ Development

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Jalankan server
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev                    # http://localhost:3000
```

### Tests
```bash
cd backend
pytest tests/ -v
```

---

## 🔐 Autentikasi & Otorisasi

### Peran Pengguna
| Role | Akses |
|---|---|
| `super_admin` | Akses penuh — manajemen sistem |
| `admin` | Manajemen user, approve dokumen |
| `guru` | Upload, edit dokumen sendiri |
| `staf` | Upload, lihat dokumen internal |
| `siswa` | Hanya lihat dokumen public |

### Flow Dokumen
```
Upload (draft) → Submit (pending_review) → Review Admin → Approved/Rejected
```

---

## 📄 API Endpoints

### Auth
| Method | Endpoint | Deskripsi |
|---|---|---|
| POST | `/api/v1/auth/register` | Daftar user baru |
| POST | `/api/v1/auth/login` | Login, return JWT |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Profil user aktif |

### Dokumen
| Method | Endpoint | Deskripsi |
|---|---|---|
| POST | `/api/v1/documents/upload` | Upload dokumen (multipart) |
| GET | `/api/v1/documents/search` | Cari dokumen (full-text) |
| GET | `/api/v1/documents/{id}` | Detail dokumen |
| GET | `/api/v1/documents/{id}/download` | Download via presigned URL |
| PATCH | `/api/v1/documents/{id}` | Update metadata |
| POST | `/api/v1/documents/{id}/approve` | Approve/reject (admin) |
| DELETE | `/api/v1/documents/{id}` | Hapus dokumen |

---

## 🌿 Environment Variables

Lihat [`.env.example`](.env.example) untuk daftar lengkap variabel.

Variabel wajib:
```env
SECRET_KEY=...          # Min 32 karakter
JWT_SECRET_KEY=...      # Min 32 karakter
POSTGRES_PASSWORD=...
MINIO_ROOT_PASSWORD=... # Min 8 karakter
REDIS_PASSWORD=...
```

---

## 🔧 Stack Teknologi

| Komponen | Teknologi | Versi |
|---|---|---|
| Backend | Python FastAPI | 0.111 |
| Frontend | Next.js + TypeScript | 14 |
| Styling | Tailwind CSS | 3.4 |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy (async) | 2.0 |
| ML | PyTorch | 2.3 |
| Storage | MinIO | Latest |
| Cache | Redis | 7 |
| Proxy | Nginx | Alpine |
| Auth | JWT (jose) + bcrypt | — |
| State | Zustand + React Query | v5 |
| Container | Docker Compose | v2 |

---

## 📝 Lisensi

MIT License — bebas digunakan untuk keperluan pendidikan.

---

> Dibuat dengan ❤️ untuk digitalisasi administrasi sekolah Indonesia
