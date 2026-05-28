"""
NeuralKeyGen Model Architecture
================================
Model encoder berbasis autoencoder yang memetakan konten dokumen
(byte sequence) ke fixed-length unique key representation.

Arsitektur:
  Input (512 bytes) → Embedding → LSTM Encoder → FC → Key (32 dim)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ByteEmbedding(nn.Module):
    """Embed byte values (0-255) ke dense vectors."""

    def __init__(self, embedding_dim: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(256, embedding_dim, padding_idx=0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len) dtype=long
        return self.embedding(x)  # (batch, seq_len, embedding_dim)


class DocumentEncoder(nn.Module):
    """Bi-LSTM encoder untuk representasi dokumen."""

    def __init__(
        self,
        input_size: int = 64,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.attention = nn.Linear(hidden_size * 2, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        output, _ = self.lstm(x)  # (batch, seq_len, hidden*2)

        # Attention pooling
        attn_weights = F.softmax(self.attention(output), dim=1)  # (batch, seq, 1)
        context = (output * attn_weights).sum(dim=1)  # (batch, hidden*2)
        return context


class NeuralKeyGenModel(nn.Module):
    """
    Lengkap model NeuralKeyGen:
    Byte sequence → embedding → encoder → key projection.
    """

    def __init__(
        self,
        embedding_dim: int = 64,
        hidden_size: int = 128,
        num_lstm_layers: int = 2,
        key_dim: int = 32,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.embedding = ByteEmbedding(embedding_dim)
        self.encoder = DocumentEncoder(embedding_dim, hidden_size, num_lstm_layers, dropout)

        self.key_projector = nn.Sequential(
            nn.Linear(hidden_size * 2, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, key_dim),
            nn.Sigmoid(),  # output dalam [0, 1]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len) dtype=float → convert to long for embedding
        x_long = x.long().clamp(0, 255)
        embedded = self.embedding(x_long)       # (batch, seq, emb_dim)
        encoded = self.encoder(embedded)         # (batch, hidden*2)
        key = self.key_projector(encoded)        # (batch, key_dim)
        return key

    def get_hex_key(self, x: torch.Tensor) -> list[str]:
        """Generate hex string keys dari batch tensor."""
        with torch.no_grad():
            keys = self.forward(x)  # (batch, key_dim)
        result = []
        for key_vec in keys:
            uint8 = (key_vec.cpu().numpy() * 255).astype("uint8")
            result.append("".join(f"{b:02x}" for b in uint8))
        return result
