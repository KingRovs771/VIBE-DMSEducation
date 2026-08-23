"""
Unit Tests untuk Core Cryptography & Encryption Module
======================================================
Menguji keandalan fungsionalitas di app.core.crypto:
1. Enkripsi & Dekripsi AES-256-GCM + HKDF
2. Pembuatan Master Key RSA-4096
3. Pembungkusan (wrapping) & Pembukaan kunci siswa menggunakan RSA-OAEP
4. Password Hashing Argon2id & Verifikasi
5. Rotasi Kunci Siswa (key rotation re-encryption)
"""
import pytest

from app.core.crypto import (
    encrypt_document,
    decrypt_document,
    generate_master_key,
    wrap_student_key,
    unwrap_student_key,
    hash_password,
    verify_password,
    compute_file_hash,
    rotate_student_document_key
)
from app.core.security import verify_password as security_verify


def test_aes_gcm_encryption_decryption():
    """Menguji siklus enkripsi dan dekripsi dokumen dengan AES-256-GCM + HKDF."""
    file_content = b"Dokumen Rahasia DMS Sekolah: Laporan Nilai Siswa Tahun 2026"
    student_key = b"12345678901234567890123456789012"  # 32 bytes master key
    
    # 1. Jalankan enkripsi
    encrypted = encrypt_document(file_content, student_key)
    
    assert len(encrypted) > 12 + 16, "Ukuran file terenkripsi harus menyertakan nonce & tag"
    assert encrypted != file_content, "Konten terenkripsi harus berbeda dari data mentah"
    
    # 2. Jalankan dekripsi
    decrypted = decrypt_document(encrypted, student_key)
    
    assert decrypted == file_content, "Data hasil dekripsi harus persis sama dengan aslinya"
    
    # 3. Dekripsi dengan kunci salah harus gagal (menghasilkan ValueError/CipherError)
    bad_key = b"bad_key_123456789012345678901234"
    with pytest.raises(Exception):
        decrypt_document(encrypted, bad_key)


def test_rsa_key_generation_and_wrapping():
    """Menguji pembuatan Master Key RSA-4096 dan proses wrapping kunci siswa."""
    # 1. Buat Master Key Sekolah
    pub_pem, priv_pem = generate_master_key()
    
    assert "BEGIN PUBLIC KEY" in pub_pem
    assert "BEGIN PRIVATE KEY" in priv_pem
    
    student_key = b"my_super_secret_student_key_32_b"
    
    # 2. Bungkus kunci siswa menggunakan RSA public key
    wrapped_b64 = wrap_student_key(student_key, pub_pem)
    
    assert len(wrapped_b64) > 0
    assert isinstance(wrapped_b64, str)
    assert wrapped_b64 != student_key.decode('utf-8', errors='ignore')
    
    # 3. Buka bungkus kunci siswa menggunakan RSA private key
    unwrapped = unwrap_student_key(wrapped_b64, priv_pem)
    
    assert unwrapped == student_key, "Kunci setelah dibuka bungkusnya harus cocok dengan kunci asli"


def test_argon2id_password_hashing():
    """Menguji password hashing berbasis Argon2id."""
    password = "MySecurePassword123!"
    
    # 1. Lakukan hashing
    hash_str = hash_password(password)
    
    assert hash_str.startswith("$argon2id$")
    assert "m=65536,t=3,p=4" in hash_str
    
    # 2. Verifikasi kecocokan password benar
    assert verify_password(password, hash_str) is True
    
    # 3. Verifikasi penolakan password salah
    assert verify_password("WrongPassword!", hash_str) is False
    
    # 4. Verifikasi terintegrasi via security.py
    assert security_verify(password, hash_str) is True
    assert security_verify("WrongPassword!", hash_str) is False


def test_legacy_bcrypt_fallback():
    """Menguji kompatibilitas ke belakang (fallback) verifikasi password bcrypt di security.py."""
    # Menggunakan hash bcrypt manual (plain: 'testpassword')
    legacy_hash = "$2b$12$lWQ/bajOJ5nZ/lio1/gb3OMkhJ4FRIedY8ratyyJlHGs33wT5bsWG"
    
    # Harus sukses diverifikasi via security_verify menggunakan fallback bcrypt
    assert security_verify("testpassword", legacy_hash) is True
    assert security_verify("wrongpassword", legacy_hash) is False


def test_file_hash_sha256():
    """Menguji kebenaran komputasi file hash SHA-256."""
    data = b"Hello DMS Sekolah 2026"
    expected_hash = "c3150d9cfef7a78a0e7d116e5e5b24090e2366b31739894d18e07425be4cac6c"
    
    assert compute_file_hash(data) == expected_hash


def test_key_rotation_re_encryption():
    """Menguji skenario rotasi kunci dokumen siswa saat seed diputar."""
    # Konten file asli
    original_data = b"Laporan Keuangan Sekolah Rahasia 2026"
    
    # Kunci siswa lama dan baru (misal dihasilkan dari NeuralKeyGen dengan seed lama & baru)
    old_student_key = b"student_old_key_1234567890123456"
    new_student_key = b"student_new_key_1234567890123456"
    
    # 1. Enkripsi file pertama kali menggunakan kunci siswa lama
    encrypted_old = encrypt_document(original_data, old_student_key)
    
    # 2. Jalankan rotasi kunci (re-enkripsi dari kunci lama ke baru)
    encrypted_new = rotate_student_document_key(encrypted_old, old_student_key, new_student_key)
    
    assert encrypted_new != encrypted_old, "File terenkripsi baru harus berbeda dari file lama karena kunci berubah"
    
    # 3. Dekripsi file baru terenkripsi menggunakan kunci siswa baru
    decrypted_new = decrypt_document(encrypted_new, new_student_key)
    
    assert decrypted_new == original_data, "Data hasil dekripsi setelah rotasi harus persis sama dengan dokumen asli"
    
    # 4. Memastikan file terenkripsi baru TIDAK bisa didekripsi dengan kunci lama
    with pytest.raises(Exception):
        decrypt_document(encrypted_new, old_student_key)
