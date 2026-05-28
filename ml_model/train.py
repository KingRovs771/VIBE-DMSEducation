"""
NeuralKeyGen Training Script
==============================
Training pipeline untuk model NeuralKeyGen.

Cara menjalankan:
  python train.py --epochs 50 --batch-size 32 --output model.pt

Dataset:
  Gunakan kumpulan file PDF/DOCX dari sekolah.
  Script akan membaca byte content setiap file sebagai input.
"""
import argparse
import os
import sys
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split

# Tambahkan backend ke path supaya bisa import model
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.ml.model import NeuralKeyGenModel


# ── Dataset ──────────────────────────────────────────────────────────────────

class DocumentDataset(Dataset):
    """
    Dataset berbasis file: membaca file biner dari folder data_dir.
    Label: hash SHA-256 dari konten (digunakan sebagai target key).
    """

    SEQ_LEN = 512

    def __init__(self, data_dir: str):
        self.files: List[Path] = []
        for ext in ("*.pdf", "*.docx", "*.txt", "*.xlsx", "*.pptx"):
            self.files.extend(Path(data_dir).rglob(ext))
        if not self.files:
            # Fallback: generate random data for testing
            print("⚠️  Tidak ada file ditemukan, menggunakan data sintetis untuk demo")
            self._synthetic = True
            self._n = 1000
        else:
            self._synthetic = False
            print(f"✅ Ditemukan {len(self.files)} file")

    def __len__(self) -> int:
        return self._n if self._synthetic else len(self.files)

    def _read_file(self, path: Path) -> bytes:
        with open(path, "rb") as f:
            return f.read(self.SEQ_LEN)

    def _bytes_to_tensor(self, data: bytes) -> torch.Tensor:
        arr = list(data)
        # Pad or truncate to SEQ_LEN
        if len(arr) < self.SEQ_LEN:
            arr += [0] * (self.SEQ_LEN - len(arr))
        arr = arr[: self.SEQ_LEN]
        return torch.tensor(arr, dtype=torch.float32)

    def _content_to_target(self, content: bytes) -> torch.Tensor:
        import hashlib
        digest = hashlib.sha256(content).digest()[:32]
        return torch.tensor(list(digest), dtype=torch.float32) / 255.0

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        if self._synthetic:
            content = bytes(random.randint(0, 255) for _ in range(self.SEQ_LEN))
        else:
            content = self._read_file(self.files[idx])

        x = self._bytes_to_tensor(content)
        y = self._content_to_target(content)
        return x, y


# ── Training ─────────────────────────────────────────────────────────────────

def train(
    data_dir: str,
    output_path: str,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    val_split: float = 0.1,
    device_name: str = "cpu",
):
    device = torch.device(device_name if torch.cuda.is_available() or device_name == "cpu" else "cpu")
    print(f"🖥️  Menggunakan device: {device}")

    # Dataset
    dataset = DocumentDataset(data_dir)
    val_size = max(1, int(len(dataset) * val_split))
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, num_workers=0)

    # Model
    model = NeuralKeyGenModel(key_dim=32).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    print(f"\n🚀 Mulai training selama {epochs} epochs...\n")

    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()

        # Validate
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                pred = model(x)
                val_loss += criterion(pred, y).item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        scheduler.step()

        print(
            f"Epoch [{epoch:3d}/{epochs}]  "
            f"Train Loss: {train_loss:.6f}  "
            f"Val Loss: {val_loss:.6f}"
        )

        # Save best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model, output_path)
            print(f"  💾 Model tersimpan ke {output_path}")

    print(f"\n✅ Training selesai! Best val loss: {best_val_loss:.6f}")
    print(f"   Model disimpan: {output_path}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training NeuralKeyGen model")
    parser.add_argument("--data-dir", default="./data", help="Folder berisi file dokumen")
    parser.add_argument("--output", default="model.pt", help="Path output model")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    args = parser.parse_args()

    train(
        data_dir=args.data_dir,
        output_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device_name=args.device,
    )
