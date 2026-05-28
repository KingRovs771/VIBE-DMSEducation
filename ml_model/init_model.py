"""
Script untuk membuat model.pt awal (untrained/random weights).
Jalankan ini sebelum training untuk menyiapkan file model.pt.

Usage:
    python init_model.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import torch
from app.ml.model import NeuralKeyGenModel


def create_initial_model(output_path: str = "model.pt"):
    model = NeuralKeyGenModel(
        embedding_dim=64,
        hidden_size=128,
        num_lstm_layers=2,
        key_dim=32,
        dropout=0.3,
    )
    model.eval()
    torch.save(model, output_path)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"✅ Model awal dibuat: {output_path}")
    print(f"   Total parameter: {total_params:,}")
    print(f"   Jalankan train.py untuk melatih model dengan data sekolah")


if __name__ == "__main__":
    create_initial_model()
