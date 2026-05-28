"""
NeuralKeyGen — Core wrapper untuk model ML penghasil kunci dokumen
"""
import asyncio
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import structlog
import torch
import numpy as np

from app.core.config import settings

logger = structlog.get_logger(__name__)


class NeuralKeyGen:
    """
    Neural network-based document key generator.

    Menghasilkan unique identifier / access key berdasarkan konten
    dokumen menggunakan model PyTorch yang telah di-training.
    """

    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = Path(model_path)
        self.device = torch.device(device if torch.cuda.is_available() or device == "cpu" else "cpu")
        self.model: Optional[torch.nn.Module] = None
        self._loaded = False

    def load_model(self) -> None:
        """Load model dari file .pt ke memori."""
        if self._loaded:
            return
        try:
            if self.model_path.exists():
                self.model = torch.load(
                    self.model_path,
                    map_location=self.device,
                    weights_only=False,
                )
                self.model.eval()
                self._loaded = True
                logger.info("✅ NeuralKeyGen model loaded", path=str(self.model_path))
            else:
                logger.warning(
                    "⚠️  Model file not found, using fallback hash generator",
                    path=str(self.model_path),
                )
        except Exception as exc:
            logger.error("❌ Failed to load NeuralKeyGen model", error=str(exc))

    def _fallback_key(self, content: bytes, key_length: int) -> str:
        """Fallback: SHA-256 based key ketika model tidak tersedia."""
        import hashlib
        digest = hashlib.sha256(content).hexdigest()
        return digest[:key_length]

    def _generate_with_model(self, content: bytes) -> str:
        """Generate key menggunakan neural network."""
        tensor = torch.tensor(
            list(content[:512]),  # ambil 512 bytes pertama
            dtype=torch.float32,
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(tensor)  # type: ignore

        # Konversi output tensor menjadi hex string
        raw = output.squeeze().cpu().numpy()
        raw_uint8 = ((raw - raw.min()) / (raw.max() - raw.min() + 1e-8) * 255).astype(np.uint8)
        return "".join(f"{b:02x}" for b in raw_uint8)[: settings.ML_KEY_LENGTH]

    def generate_key(self, content: bytes) -> str:
        """Generate document key dari konten binary."""
        if self._loaded and self.model is not None:
            try:
                return self._generate_with_model(content)
            except Exception as exc:
                logger.warning("Model inference failed, using fallback", error=str(exc))
        return self._fallback_key(content, settings.ML_KEY_LENGTH)

    async def generate_key_async(self, content: bytes) -> str:
        """Async wrapper untuk generate_key."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_key, content)

    def batch_generate(self, contents: List[bytes]) -> List[str]:
        """Generate keys untuk banyak dokumen sekaligus."""
        return [self.generate_key(c) for c in contents]


@lru_cache(maxsize=1)
def get_neural_keygen() -> NeuralKeyGen:
    """Singleton instance of NeuralKeyGen (FastAPI dependency)."""
    keygen = NeuralKeyGen(
        model_path=settings.ML_MODEL_PATH,
        device=settings.ML_DEVICE,
    )
    keygen.load_model()
    return keygen
