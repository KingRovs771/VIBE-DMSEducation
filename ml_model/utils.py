"""
ML Utilities — preprocessing, evaluation, export
"""
import hashlib
import os
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import torch


# ── Preprocessing ─────────────────────────────────────────────────────────────

def read_document_bytes(path: str, max_bytes: int = 512) -> bytes:
    """Baca file dan return bytes pertama max_bytes."""
    with open(path, "rb") as f:
        return f.read(max_bytes)


def bytes_to_tensor(data: bytes, seq_len: int = 512) -> torch.Tensor:
    """Convert bytes ke float tensor dengan padding/truncate."""
    arr = list(data)
    if len(arr) < seq_len:
        arr += [0] * (seq_len - len(arr))
    return torch.tensor(arr[:seq_len], dtype=torch.float32)


def batch_bytes_to_tensor(batch: List[bytes], seq_len: int = 512) -> torch.Tensor:
    """Convert list of bytes ke batched tensor."""
    tensors = [bytes_to_tensor(b, seq_len) for b in batch]
    return torch.stack(tensors)  # (batch, seq_len)


# ── Key utilities ─────────────────────────────────────────────────────────────

def tensor_to_hex_key(tensor: torch.Tensor, key_length: int = 32) -> str:
    """Convert output tensor ke hex string key."""
    arr = (tensor.detach().cpu().numpy() * 255).astype(np.uint8)
    return "".join(f"{b:02x}" for b in arr)[:key_length]


def sha256_key(content: bytes, key_length: int = 32) -> str:
    """Fallback: SHA-256 based key."""
    return hashlib.sha256(content).hexdigest()[:key_length]


def is_key_unique(key: str, existing_keys: set) -> bool:
    """Cek apakah key sudah ada."""
    return key not in existing_keys


# ── Model utilities ───────────────────────────────────────────────────────────

def load_model(path: str, device: str = "cpu") -> Optional[torch.nn.Module]:
    """Load model dari file .pt."""
    p = Path(path)
    if not p.exists():
        print(f"⚠️  Model file tidak ditemukan: {path}")
        return None
    model = torch.load(p, map_location=torch.device(device), weights_only=False)
    model.eval()
    return model


def export_to_onnx(model: torch.nn.Module, output_path: str, seq_len: int = 512):
    """Export model ke ONNX format untuk deployment."""
    dummy_input = torch.zeros(1, seq_len, dtype=torch.float32)
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        opset_version=17,
        input_names=["bytes"],
        output_names=["key"],
        dynamic_axes={"bytes": {0: "batch_size"}, "key": {0: "batch_size"}},
    )
    print(f"✅ Model diekspor ke ONNX: {output_path}")


def count_parameters(model: torch.nn.Module) -> int:
    """Hitung jumlah parameter trainable."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_uniqueness(model: torch.nn.Module, n_samples: int = 1000) -> float:
    """
    Evaluasi seberapa unik key yang dihasilkan model.
    Return: collision rate (lower is better).
    """
    import random
    keys = set()
    collisions = 0

    model.eval()
    with torch.no_grad():
        for _ in range(n_samples):
            content = bytes(random.randint(0, 255) for _ in range(512))
            tensor = bytes_to_tensor(content).unsqueeze(0)
            output = model(tensor).squeeze()
            key = tensor_to_hex_key(output)
            if key in keys:
                collisions += 1
            keys.add(key)

    collision_rate = collisions / n_samples
    print(f"📊 Uniqueness test: {n_samples} samples, {collisions} collisions ({collision_rate:.2%})")
    return collision_rate


if __name__ == "__main__":
    # Quick sanity check
    from pathlib import Path
    model_path = Path(__file__).parent / "model.pt"
    model = load_model(str(model_path))
    if model:
        params = count_parameters(model)
        print(f"✅ Model loaded, {params:,} trainable parameters")
        evaluate_uniqueness(model, n_samples=500)
