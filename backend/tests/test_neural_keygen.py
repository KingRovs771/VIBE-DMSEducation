"""
Test untuk NeuralKeyGen
"""
import pytest
import torch

from app.ml.model import NeuralKeyGenModel
from app.core.neural_keygen import NeuralKeyGen


def test_model_forward_pass():
    """Model harus bisa forward pass dengan benar."""
    model = NeuralKeyGenModel(key_dim=32)
    dummy_input = torch.zeros(2, 512)  # batch=2, seq=512
    output = model(dummy_input)
    assert output.shape == (2, 32), f"Expected (2,32), got {output.shape}"
    assert (output >= 0).all() and (output <= 1).all(), "Output harus dalam range [0,1]"


def test_model_key_uniqueness():
    """Keys dari input berbeda harus berbeda."""
    model = NeuralKeyGenModel(key_dim=32)
    import random
    keys = set()
    for _ in range(100):
        content = bytes(random.randint(0, 255) for _ in range(512))
        tensor = torch.tensor(list(content), dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            output = model(tensor).squeeze()
        keys.update(model.get_hex_key(tensor))

    # Harusnya tidak ada collision pada 100 samples
    assert len(keys) == 100


def test_neural_keygen_fallback():
    """NeuralKeyGen harus berfungsi tanpa model.pt (fallback mode)."""
    keygen = NeuralKeyGen(model_path="/nonexistent/model.pt", device="cpu")
    keygen.load_model()  # Akan gagal silently
    content = b"Test document content untuk DMS Sekolah"
    key = keygen.generate_key(content)
    assert len(key) > 0
    assert all(c in "0123456789abcdef" for c in key), "Key harus hex string"


@pytest.mark.asyncio
async def test_neural_keygen_async():
    """Test async key generation."""
    keygen = NeuralKeyGen(model_path="/nonexistent/model.pt", device="cpu")
    content = b"Async test content"
    key = await keygen.generate_key_async(content)
    assert isinstance(key, str)
    assert len(key) > 0
