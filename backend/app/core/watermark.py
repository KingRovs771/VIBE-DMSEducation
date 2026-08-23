"""
Watermark & QR Verification Service
===================================
Menangani penyematan watermark dinamis di setiap halaman PDF dan
QR Code verifikasi bertandatangan HMAC-SHA256 pada halaman pertama.
Mendukung PDF Permission Protection (AES-128) agar PDF tidak bisa diedit
oleh penerima (F-014).
"""
import io
import json
import base64
import hmac
import hashlib
import qrcode
import fitz
from datetime import datetime

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
    """
    Membuat signed token berisi siswa_id, doc_id, timestamp download saat ini
    dan tanda tangan HMAC-SHA256 untuk memvalidasi keaslian data.
    """
    download_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    """
    Memverifikasi keabsahan token dengan mencocokkan HMAC-SHA256.
    Mengembalikan payload jika valid, atau {"valid": False} jika tidak valid.
    """
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


def apply_pdf_permissions(
    pdf_bytes: bytes,
    owner_password: str,
) -> bytes:
    """
    Menerapkan PDF Permission Protection (AES-128) pada PDF.

    Membuka PDF tanpa password (user password kosong), tetapi
    melarang editing, copy teks, dan print kualitas tinggi.
    Owner password diderivasi secara deterministik sehingga tidak
    perlu disimpan di database.

    Permission yang diizinkan:
        - Baca (selalu)
        - Print kualitas rendah (draft)

    Permission yang dilarang:
        - Edit konten
        - Copy teks/gambar
        - Print kualitas tinggi
        - Tambah anotasi
        - Isi form

    Args:
        pdf_bytes: PDF plaintext atau PDF yang sudah ada watermark
        owner_password: Password owner (turunan dari HMAC, tidak diketahui user)

    Returns:
        bytes: PDF terproteksi permission
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # PDF permission flags (PyMuPDF v1.21+)
    # Hanya izinkan print kualitas rendah (PDF_PERM_PRINT = 4)
    # Bit flags lain (modify=8, copy=16, annotate=32, form=256, accessibility=512,
    # assemble=1024, print_hq=2048) TIDAK diset = dilarang
    perm = (
        fitz.PDF_PERM_PRINT          # print draft (low quality)
        # fitz.PDF_PERM_MODIFY       # edit konten — DILARANG
        # fitz.PDF_PERM_COPY         # copy teks/gambar — DILARANG
        # fitz.PDF_PERM_ANNOTATE     # tambah anotasi — DILARANG
    )

    encrypt_meth = fitz.PDF_ENCRYPT_AES_128   # AES-128 (PDF 1.6+)

    # user_pass = "" → bisa dibuka langsung tanpa password
    # owner_pass = owner_password → hanya pemilik yang bisa ubah permission
    output_bytes = doc.tobytes(
        encryption=encrypt_meth,
        owner_pw=owner_password,
        user_pw="",
        permissions=perm,
    )
    doc.close()
    return output_bytes


def derive_owner_password(doc_id: int, siswa_id: int, secret_key: str) -> str:
    """
    Menurunkan owner password secara deterministik dari identitas dokumen.
    Tidak pernah disimpan di DB — selalu bisa diderivasi ulang.
    """
    message = f"PDF_OWNER:{doc_id}:{siswa_id}:DMS_SEKOLAH_v1"
    digest = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    # Gunakan 32 karakter pertama sebagai password (cukup untuk AES-128)
    return digest[:32]


def apply_watermark_and_qr(
    pdf_bytes: bytes,
    student_name: str,
    student_nis: str,
    download_time: str,
    verify_url: str | None,
    custom_watermark: str | None = None,
) -> bytes:
    """
    Menyematkan teks watermark diagonal di tengah setiap halaman
    dan QR code di pojok kanan bawah halaman pertama PDF.

    Args:
        pdf_bytes: Konten PDF mentah
        student_name: Nama siswa untuk watermark
        student_nis: NIS siswa untuk watermark
        download_time: Waktu download (string)
        verify_url: URL verifikasi QR (None = tidak tambah QR)
        custom_watermark: Override teks watermark (untuk dinas, dll)
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    if custom_watermark:
        watermark_text = custom_watermark
    else:
        watermark_text = f"DOKUMEN RESMI - {student_name.upper()} - {student_nis} - {download_time}"
    
    for page in doc:
        rect = page.rect
        width = rect.width
        height = rect.height
        
        cx = width / 2
        cy = height / 2
        
        # Miring diagonal -45 derajat (ke kanan atas) menggunakan morph matrix
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
        
    # Tambah QR Code di halaman pertama (jika verify_url tersedia)
    if verify_url and len(doc) > 0:
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

