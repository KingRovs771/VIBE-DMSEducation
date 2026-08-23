"""
Core TOTP & Cryptography Helpers
===============================
Menyediakan utilitas otentikasi dua faktor menggunakan protokol TOTP (RFC 6238),
pembuatan QR Code base64, dan enkripsi simetris AES-256-GCM untuk mengamankan 
secret key TOTP di database menggunakan SECRET_KEY aplikasi.
"""
import base64
import hashlib
import io
import secrets
import pyotp
import qrcode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def encrypt_totp_secret(secret: str) -> str:
    """
    Mengenkripsi secret key TOTP menggunakan AES-GCM.
    Key enkripsi diderivasi dari settings.SECRET_KEY menggunakan SHA-256.
    """
    key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, secret.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_totp_secret(encrypted_base64: str) -> str:
    """
    Mendekripsi secret key TOTP terenkripsi.
    """
    try:
        data = base64.b64decode(encrypted_base64.encode("utf-8"))
        nonce = data[:12]
        ciphertext = data[12:]
        key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception:
        return ""


def generate_totp_secret() -> str:
    """Menghasilkan kunci base32 acak untuk TOTP."""
    return pyotp.random_base32()


def get_totp_uri(username: str, secret: str) -> str:
    """Menghasilkan URI provisioning TOTP untuk aplikasi authenticator."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="DMS-Sekolah"
    )


def generate_qr_code_data_url(uri: str) -> str:
    """Menghasilkan representasi base64 data URL gambar PNG QR Code."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{qr_base64}"


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Memverifikasi kode 6 digit TOTP dari user.
    Mendukung toleransi clock-drift sebesar 30 detik (valid_window=1).
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
