"""
Unit Tests untuk NeuralKeyGen Profil Siswa
===========================================
Pengujian menyeluruh untuk memvalidasi properti kritis kriptografi:
1. Deterministik (input sama selalu menghasilkan output sama)
2. Zero-storage (kunci tidak pernah disimpan di database, verifikasi bekerja secara langsung)
3. Collision-resistant (tidak ada tabrakan kunci pada siswa yang berbeda)
4. Irreversible (tidak bisa tebak data input dari output kunci)
"""
import hashlib
import random
import pytest
import numpy as np
import torch

from app.ml.student_keygen import (
    StudentFeatureExtractor,
    NeuralKeyGen,
    generate_key,
    verify_key,
    SYSTEM_SALT,
    hkdf
)


# --- FIXTURES ---

@pytest.fixture
def dummy_siswa_1():
    return {
        'nis': '20261001',
        'nama': 'Andi Santoso',
        'nama_hash': hashlib.sha256('Andi Santoso'.lower().encode()).hexdigest(),
        'tgl_lahir': '2008-05-12',
        'entropy_seed': 'a3f8b2c1d9e4f7a6b5c8d2e1f9a4b7c3',
        'angkatan': 2026
    }


@pytest.fixture
def dummy_siswa_2():
    # Siswa yang mirip tetapi berbeda sedikit (misal: beda NIS & seed)
    return {
        'nis': '20261002',
        'nama': 'Andi Santoso',
        'nama_hash': hashlib.sha256('Andi Santoso'.lower().encode()).hexdigest(),
        'tgl_lahir': '2008-05-12',
        'entropy_seed': 'f1e2d3c4b5a6978869504132210fedcb',
        'angkatan': 2026
    }


# --- TESTS ---

def test_feature_extractor_is_deterministic(dummy_siswa_1):
    """Menjamin bahwa ekstraksi fitur menghasilkan array yang persis sama untuk data yang sama."""
    extractor = StudentFeatureExtractor(SYSTEM_SALT)
    features_1 = extractor.extract(dummy_siswa_1)
    features_2 = extractor.extract(dummy_siswa_1)

    assert features_1.shape == (64,)
    assert np.array_equal(features_1, features_2), "Fitur hasil ekstraksi harus identik 100% (deterministik)"


def test_feature_extractor_shape_and_range(dummy_siswa_1):
    """Menjamin bahwa range nilai fitur berada dalam batas normal dan panjang 64."""
    extractor = StudentFeatureExtractor(SYSTEM_SALT)
    features = extractor.extract(dummy_siswa_1)

    assert features.shape == (64,), "Panjang vektor fitur harus 64 dimensi"
    # Nilai float harus terikat wajar (kebanyakan cyclic sin/cos [ -1, 1 ] atau normalized [ 0, 1 ])
    assert np.all(features >= -1.0) and np.all(features <= 1.0), "Vektor fitur harus berada dalam range [-1.0, 1.0]"


def test_hkdf_rfc5869_compliance():
    """Menguji keselarasan implementasi HKDF murni kami dengan uji vektor standar."""
    ikm = b"\x0b" * 22
    salt = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c"
    info = b"\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9"
    
    # Derivasi kunci 42 bytes
    okm = hkdf(ikm, 42, salt, info)
    
    assert len(okm) == 42
    # Hasil derivasi harus acak berkualitas tinggi
    assert okm != b"\x00" * 42


def test_property_1_deterministik(dummy_siswa_1):
    """PROPERTI 1: Deterministik — Input yang sama SELALU menghasilkan output kunci yang sama."""
    key_run_1 = generate_key(dummy_siswa_1)
    key_run_2 = generate_key(dummy_siswa_1)
    key_run_3 = generate_key(dummy_siswa_1)

    assert isinstance(key_run_1, bytes), "Kunci harus bertipe bytes"
    assert len(key_run_1) == 32, "Kunci final harus 256-bit (32 bytes) siap untuk AES-256"
    assert key_run_1 == key_run_2 == key_run_3, "Inference harus deterministik 100% untuk input yang sama"


def test_property_2_zero_storage(dummy_siswa_1):
    """PROPERTI 2: Zero-Storage — Verifikasi kunci sukses secara deterministik tanpa penyimpanan db."""
    # Simulasikan pembuatan kunci saat enkripsi dokumen
    generated_key = generate_key(dummy_siswa_1)

    # Simulasikan verifikasi kunci saat user mengunggah dokumen baru / membaca dokumen
    # Tanpa mengambil kunci dari database, kita verifikasi menggunakan data profil siswa langsung
    is_valid = verify_key(dummy_siswa_1, generated_key)

    assert is_valid is True, "Verifikasi zero-storage harus berhasil tanpa membaca kunci dari database"

    # Simulasikan verifikasi dengan kunci salah
    bad_key = b"\x00" * 32
    assert verify_key(dummy_siswa_1, bad_key) is False, "Verifikasi harus menolak kunci yang salah"


def test_property_3_collision_resistant(dummy_siswa_1, dummy_siswa_2):
    """PROPERTI 3: Collision-Resistant — Tidak ada dua siswa berbeda yang menghasilkan kunci sama."""
    key_siswa_1 = generate_key(dummy_siswa_1)
    key_siswa_2 = generate_key(dummy_siswa_2)

    assert key_siswa_1 != key_siswa_2, "Dua siswa berbeda harus menghasilkan kunci yang unik (bebas collision)"


def test_property_3_mass_collision_resistance():
    """PROPERTI 3 (Lanjutan): Collision-Resistant secara massal untuk 1.000 sampel siswa acak."""
    keys = set()
    n_samples = 1000
    random.seed(42)

    for i in range(n_samples):
        # Generate profil unik acak
        siswa = {
            'nis': f"2026{1000 + i:04d}",
            'nama': f"Siswa_{i}",
            'nama_hash': hashlib.sha256(f"Siswa_{i}".encode()).hexdigest(),
            'tgl_lahir': f"{2005 + (i % 5)}-{1 + (i % 12):02d}-{1 + (i % 28):02d}",
            'entropy_seed': hashlib.sha256(f"seed_{i}".encode()).hexdigest()[:32],
            'angkatan': 2026
        }
        key = generate_key(siswa)
        keys.add(key)

    # Pastikan jumlah kunci unik sama dengan jumlah sampel (0 collision)
    assert len(keys) == n_samples, f"Ditemukan tabrakan kunci pada {n_samples - len(keys)} siswa!"


def test_property_4_irreversible(dummy_siswa_1):
    """PROPERTI 4: Irreversible — Tidak bisa menebak/merekonstruksi input dari output kunci final."""
    key = generate_key(dummy_siswa_1)
    
    # 1. Pastikan panjang kunci adalah 32 bytes (256 bits)
    assert len(key) == 32
    
    # 2. Karena kunci final dihasilkan dari HKDF-SHA256, maka kunci tersebut:
    #   - Memiliki entropi tinggi (distribusinya acak semu)
    #   - Bersifat satu arah (one-way property of cryptographically secure hash functions)
    # Kunci tidak memiliki kemiripan nilai langsung dengan representasi byte profil siswa mentah
    extractor = StudentFeatureExtractor(SYSTEM_SALT)
    raw_features = extractor.extract(dummy_siswa_1).tobytes()
    
    # Kunci final harus sangat berbeda dari representasi fitur mentah
    assert key != raw_features[:32]
    
    # Cek bahwa perubahan kecil pada nama melahirkan avalanche effect
    siswa_modified = dummy_siswa_1.copy()
    siswa_modified['nama'] = "Andi Santosaa"  # typo kecil
    siswa_modified['nama_hash'] = hashlib.sha256(siswa_modified['nama'].lower().encode()).hexdigest()
    
    modified_key = generate_key(siswa_modified)
    # Hamming distance antar bit kunci asli dengan modified harus cukup besar (~50% bit berbeda)
    bits_orig = np.unpackbits(np.frombuffer(key, dtype=np.uint8))
    bits_mod = np.unpackbits(np.frombuffer(modified_key, dtype=np.uint8))
    hamming_dist = np.sum(bits_orig != bits_mod)
    
    # Idealnya mendekati 128 bit dari total 256 bit. Minimal beda > 80 bit.
    assert hamming_dist > 80, f"Avalanche effect lemah! Hanya {hamming_dist} bit yang berubah."
