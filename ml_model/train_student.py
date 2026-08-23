"""
Training Script untuk NeuralKeyGen Profil Siswa
================================================
Melatih model MLP NeuralKeyGen menggunakan 10.000 data siswa dummy,
dengan Triplet-based Loss khusus untuk menghasilkan kunci yang
deterministik, collision-resistant, dan berepisod tinggi (uniform entropy).

Cara menjalankan:
    python train_student.py --epochs 25 --batch-size 128
"""
import argparse
import hashlib
import os
import random
import sys
import time
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Menambahkan root project ke path agar bisa import backend/app
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.ml.student_keygen import NeuralKeyGen, StudentFeatureExtractor, SYSTEM_SALT


# ─── GENERATOR DUMMY SISWA DETERMINISTIK (10.000 SISWA) ───────────────────────

class SyntheticStudentGenerator:
    """Membuat profil 10.000 siswa sintetis secara deterministik untuk training."""

    NAMA_DEPAN = [
        'Andi', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Galih', 'Hani',
        'Indra', 'Joko', 'Kartika', 'Lina', 'Muhamad', 'Nadia', 'Otto',
        'Putri', 'Qori', 'Rizki', 'Sari', 'Taufik', 'Ulfa', 'Veri'
    ]
    NAMA_BELAKANG = [
        'Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Sari', 'Wibowo',
        'Setiawan', 'Nugroho', 'Hidayat', 'Susanto', 'Rahayu', 'Purnomo'
    ]

    def __init__(self, seed: int = 42):
        self.seed = seed

    def generate(self, n: int = 10000) -> List[dict]:
        random.seed(self.seed)
        np.random.seed(self.seed)
        students = []
        for i in range(n):
            # Angkatan: tahun masuk 2020 - 2026
            angkatan = 2020 + (i % 7)
            # NIS: tahun masuk + 4 digit index
            nis = f"{angkatan}{1000 + i:04d}"
            # Nama lengkap
            nama = f"{random.choice(self.NAMA_DEPAN)} {random.choice(self.NAMA_BELAKANG)}"
            nama_hash = hashlib.sha256(nama.lower().encode('utf-8')).hexdigest()
            # Tanggal lahir: SMA ~ usia 14-16 tahun
            tahun_lahir = angkatan - random.randint(14, 16)
            bulan_lahir = 1 + (i % 12)
            hari_lahir = 1 + (i % 28)
            tgl_lahir = f"{tahun_lahir}-{bulan_lahir:02d}-{hari_lahir:02d}"
            # Entropy seed unik
            seed_input = f"STUDENT_SEED_{i}_{nis}_{tgl_lahir}"
            entropy_seed = hashlib.sha256(seed_input.encode('utf-8')).hexdigest()[:32]

            students.append({
                'nis': nis,
                'nama': nama,
                'nama_hash': nama_hash,
                'tgl_lahir': tgl_lahir,
                'entropy_seed': entropy_seed,
                'angkatan': angkatan
            })
        return students


# ─── TRIPLET PYTORCH DATASET ──────────────────────────────────────────────────

class NeuralKeyGenDataset(Dataset):
    """
    Dataset bertipe Triplet yang menghasilkan:
      - anchor   : fitur siswa A
      - positive : fitur siswa A + noise sangat kecil (agar kebal noise / deterministik)
      - negative : fitur siswa B yang berbeda
    """

    def __init__(self, features: np.ndarray, augment_std: float = 0.001):
        self.X = torch.tensor(features, dtype=torch.float32)
        self.n = len(features)
        self.augment_std = augment_std

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        anchor = self.X[idx]

        # Positive: data yang sama dengan sedikit noise (simulasi interferensi input)
        noise = torch.randn_like(anchor) * self.augment_std
        positive = torch.clamp(anchor + noise, 0.0, 1.0)

        # Negative: data siswa lain secara acak
        neg_idx = random.randint(0, self.n - 1)
        while neg_idx == idx:
            neg_idx = random.randint(0, self.n - 1)
        negative = self.X[neg_idx]

        return anchor, positive, negative


# ─── CUSTOM TRIPLET LOSS FUNCTION ─────────────────────────────────────────────

class NeuralKeyGenLoss(nn.Module):
    """
    Triplet Loss kustom untuk memaksimalkan properti kriptografi model:
      1. Consistency: anchor vs positive harus identik (MSELoss).
      2. Separation: anchor vs negative harus sangat berbeda jauh (Cosine Similarity).
      3. Entropy: output bit bernilai uniform [0,1] dengan rata-rata mendekati 0.5.
    """

    def __init__(self, w_cons: float = 0.5, w_sep: float = 0.3, w_ent: float = 0.2, sep_margin: float = 0.2):
        super().__init__()
        self.w_cons = w_cons
        self.w_sep = w_sep
        self.w_ent = w_ent
        self.margin = sep_margin

    def forward(self, out_anchor: torch.Tensor, out_positive: torch.Tensor, out_negative: torch.Tensor) -> Tuple[torch.Tensor, dict]:
        # 1. Consistency: anchor vs positive (MSE)
        consistency = F.mse_loss(out_anchor, out_positive)

        # 2. Separation: anchor vs negative (Cosine similarity)
        cos_sim = F.cosine_similarity(out_anchor, out_negative, dim=1)
        # Ingin cosine similarity sekecil mungkin (mendekati 0 atau -1)
        separation = torch.mean(F.relu(cos_sim - self.margin + 0.1))

        # 3. Entropy: output bernilai uniform [0, 1] (BCE ke target 0.5)
        target = torch.full_like(out_anchor, 0.5)
        entropy = F.binary_cross_entropy(out_anchor, target)

        total = (self.w_cons * consistency +
                 self.w_sep * separation +
                 self.w_ent * entropy)

        return total, {
            'consistency': consistency.item(),
            'separation': separation.item(),
            'entropy': entropy.item()
        }


# ─── TRAINING PIPELINE ────────────────────────────────────────────────────────

def train(epochs: int = 25, batch_size: int = 128, lr: float = 1e-3, output_path: str = "student_model.pt"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Training menggunakan device: {device}")

    # 1. Buat data siswa sintetis (10.000 data)
    print("⏳ Menyiapkan 10.000 profil siswa sintetis...")
    generator = SyntheticStudentGenerator(seed=42)
    students = generator.generate(10000)

    # 2. Ekstrak fitur secara deterministik
    print("⏳ Mengekstrak fitur 64-dimensi...")
    extractor = StudentFeatureExtractor(SYSTEM_SALT)
    features_list = []
    for s in students:
        features_list.append(extractor.extract(s))
    features = np.stack(features_list)
    print(f"✅ Ekstraksi selesai. Fitur shape: {features.shape}")

    # 3. Split data untuk Train & Validation (90% Train, 10% Val)
    n_samples = len(features)
    n_train = int(n_samples * 0.9)
    train_features = features[:n_train]
    val_features = features[n_train:]

    train_ds = NeuralKeyGenDataset(train_features, augment_std=0.001)
    val_ds = NeuralKeyGenDataset(val_features, augment_std=0.0)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size * 2, shuffle=False)

    # 4. Inisialisasi Model, Optimizer, dan Loss
    model = NeuralKeyGen(input_dim=64, output_dim=256).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = NeuralKeyGenLoss()

    best_val_loss = float("inf")
    print(f"🚀 Mulai training selama {epochs} epochs...")

    for epoch in range(1, epochs + 1):
        # --- TRAIN ---
        model.train()
        train_loss = 0.0
        breakdown_sums = {'consistency': 0.0, 'separation': 0.0, 'entropy': 0.0}

        for anchor, positive, negative in train_loader:
            anchor = anchor.to(device)
            positive = positive.to(device)
            negative = negative.to(device)

            optimizer.zero_grad()
            out_a = model(anchor)
            out_p = model(positive)
            out_n = model(negative)

            loss, breakdown = criterion(out_a, out_p, out_n)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item()
            for k in breakdown_sums:
                breakdown_sums[k] += breakdown[k]

        train_loss /= len(train_loader)
        for k in breakdown_sums:
            breakdown_sums[k] /= len(train_loader)

        # --- VALIDATE ---
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for anchor, positive, negative in val_loader:
                anchor = anchor.to(device)
                positive = positive.to(device)
                negative = negative.to(device)

                out_a = model(anchor)
                out_p = model(positive)
                out_n = model(negative)

                loss, _ = criterion(out_a, out_p, out_n)
                val_loss += loss.item()

        val_loss /= len(val_loader)
        scheduler.step()

        print(
            f"Epoch [{epoch:2d}/{epochs}]  "
            f"Loss: {train_loss:.6f}  "
            f"Val Loss: {val_loss:.6f}  "
            f"(Cons: {breakdown_sums['consistency']:.4f}, "
            f"Sep: {breakdown_sums['separation']:.4f}, "
            f"Ent: {breakdown_sums['entropy']:.4f})"
        )

        # --- SAVE BEST MODEL ---
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Buat folder output jika belum ada
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'val_loss': best_val_loss
            }, output_path)
            print(f"  💾 Model terbaik disimpan ke {output_path}")

    print(f"\n✅ Training selesai! Best val loss: {best_val_loss:.6f}")
    print(f"   Model akhir tersimpan di: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NeuralKeyGen model on student profiles")
    parser.add_argument("--epochs", type=int, default=25, help="Jumlah epochs training")
    parser.add_argument("--batch-size", type=int, default=128, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--output", default=str(MODEL_PATH), help="Path output file model.pt")
    args = parser.parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        output_path=args.output
    )
