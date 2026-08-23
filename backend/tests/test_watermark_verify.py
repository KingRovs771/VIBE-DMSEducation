"""
Test Watermark and QR Code Generation (Standalone Integration Test)
===================================================================
Menjalankan simulasi pembuatan PDF, penyematan watermark dinamis,
pembuatan QR Code verifikasi HMAC-SHA256, dan validasi token secara mandiri.
"""
import os
import io
import sys
import json
import base64
import hmac
import hashlib
import datetime
import qrcode
import fitz

# Mock Key untuk isolasi testing
SECRET_KEY = "change-me-in-production-test-secret"

def generate_qr_code_image(url: str) -> bytes:
    """Menghasilkan kode QR dalam format PNG (bytes)."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def create_signed_token(siswa_id: int, doc_id: int, secret_key: str) -> tuple[str, str]:
    """Membuat signed token berisi siswa_id, doc_id, dan timestamp download."""
    download_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{siswa_id}:{doc_id}:{download_at}"
    sig = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    
    payload = {
        "siswa_id": str(siswa_id),
        "doc_id": str(doc_id),
        "download_at": download_at,
        "sig": sig
    }
    
    payload_json = json.dumps(payload)
    token = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")
    return token, download_at

def verify_signed_token(token: str, secret_key: str) -> dict:
    """Verifikasi keabsahan token HMAC-SHA256."""
    try:
        padded_token = token + "=" * (4 - len(token) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded_token.encode())
        payload = json.loads(payload_bytes.decode())
        
        siswa_id = payload["siswa_id"]
        doc_id = payload["doc_id"]
        download_at = payload["download_at"]
        sig = payload["sig"]
        
        expected_message = f"{siswa_id}:{doc_id}:{download_at}"
        expected_sig = hmac.new(secret_key.encode(), expected_message.encode(), hashlib.sha256).hexdigest()
        
        if hmac.compare_digest(sig, expected_sig):
            return {
                "valid": True,
                "siswa_id": int(siswa_id),
                "doc_id": int(doc_id),
                "download_at": download_at
            }
    except Exception:
        pass
    return {"valid": False}

def apply_watermark_and_qr(
    pdf_bytes: bytes,
    student_name: str,
    student_nis: str,
    download_time: str,
    verify_url: str
) -> bytes:
    """Menyematkan watermark diagonal dan QR code pojok kanan bawah PDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    watermark_text = f"DOKUMEN RESMI - {student_name.upper()} - {student_nis} - {download_time}"
    
    for page in doc:
        rect = page.rect
        width = rect.width
        height = rect.height
        
        cx = width / 2
        cy = height / 2
        
        # Miring diagonal -45 derajat (ke kanan atas) menggunakan morph matrix
        # Agar teks terpusat, gunakan cx - 180, cy + 10 sebagai anchor awal sebelum rotasi
        matrix = fitz.Matrix(-45)
        page.insert_text(
            fitz.Point(cx - 220, cy + 10),
            watermark_text,
            fontsize=28,
            fontname="hebo",
            color=(1.0, 0.0, 0.0),  # Warna Merah
            fill_opacity=0.15,
            morph=(fitz.Point(cx, cy), matrix)
        )
        
    # Tambah QR Code di halaman pertama
    if len(doc) > 0:
        first_page = doc[0]
        rect = first_page.rect
        width = rect.width
        height = rect.height
        
        qr_bytes = generate_qr_code_image(verify_url)
        
        # Ukuran: 2cm x 2cm = 56.7 x 56.7 points
        size = 56.7
        margin = 20
        
        qr_rect = fitz.Rect(
            width - size - margin,
            height - size - margin,
            width - margin,
            height - margin
        )
        
        first_page.insert_image(qr_rect, stream=qr_bytes)
        
    output_bytes = doc.write()
    doc.close()
    return output_bytes

def run_test():
    print("=== MEMULAI PENGUJIAN WATERMARK & QR CODE VERIFIKASI (STANDALONE) ===")
    
    # 1. Test Token Generation & Verification
    siswa_id = 42
    doc_id = 99
    
    print("\n[1] Menguji Pembuatan Signed Token...")
    token, download_at = create_signed_token(siswa_id, doc_id, SECRET_KEY)
    print(f"    - Timestamp: {download_at}")
    print(f"    - Generated Token: {token}")
    
    print("\n[2] Menguji Verifikasi Token...")
    verification = verify_signed_token(token, SECRET_KEY)
    print(f"    - Hasil Verifikasi: {verification}")
    
    assert verification["valid"] is True, "ERROR: Token valid harusnya True!"
    assert verification["siswa_id"] == siswa_id, f"ERROR: siswa_id tidak cocok! {verification['siswa_id']}"
    assert verification["doc_id"] == doc_id, f"ERROR: doc_id tidak cocok! {verification['doc_id']}"
    print("    - Hasil: SUKSES (Token valid & tanda tangan HMAC terverifikasi)")

    # 2. Test PDF Watermarking & QR Embedding
    print("\n[3] Menguji Penyematan Watermark & QR Code pada PDF...")
    
    # Buat PDF kosong berisi teks akademik basic
    doc = fitz.open()
    p = doc.new_page(width=595, height=842) # A4
    p.insert_text(fitz.Point(100, 100), "DMS SEKOLAH — LAPORAN DUMMY AKADEMIK", fontsize=16, fontname="hebo")
    p.insert_text(fitz.Point(100, 150), "Nama: Budi Santoso", fontsize=12, fontname="helv")
    p.insert_text(fitz.Point(100, 170), "NIS: 20261009", fontsize=12, fontname="helv")
    p.insert_text(fitz.Point(100, 220), "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", fontsize=10, fontname="helv")
    
    pdf_bytes = doc.write()
    doc.close()
    
    verify_url = f"http://localhost:8000/api/v1/verify/{token}"
    
    try:
        watermarked_bytes = apply_watermark_and_qr(
            pdf_bytes=pdf_bytes,
            student_name="Budi Santoso",
            student_nis="20261009",
            download_time=download_at,
            verify_url=verify_url
        )
        
        # Simpan sampel hasil ke file untuk inspeksi visual user
        sample_path = "tests/test_watermarked_sample.pdf"
        with open(sample_path, "wb") as f:
            f.write(watermarked_bytes)
            
        print(f"    - Hasil: SUKSES (Berkas PDF ter-watermark disimpan di {sample_path})")
        print("    - Silakan periksa berkas tersebut untuk melihat teks diagonal merah samar dan QR Code pojok kanan bawah!")
        
        # Validasi struktur PDF yang dihasilkan
        test_doc = fitz.open(sample_path)
        print(f"    - Jumlah Halaman PDF Hasil: {len(test_doc)}")
        assert len(test_doc) == 1, "ERROR: Jumlah halaman tidak cocok!"
        test_doc.close()
        
    except Exception as e:
        print(f"    - Hasil: GAGAL ({str(e)})")
        sys.exit(1)

    print("\n=== SELURUH PENGUJIAN WATERMARK & QR CODE BERHASIL DISELESAIKAN ===")

if __name__ == "__main__":
    run_test()
