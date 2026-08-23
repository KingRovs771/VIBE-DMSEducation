import structlog
import asyncio

logger = structlog.get_logger(__name__)

async def send_document_notification(email_tujuan: str, nama_siswa: str, jenis_dokumen: str):
    """
    Simulasi pengiriman notifikasi email ke siswa setelah dokumen diunggah.
    Menggunakan mode MOCK untuk development.
    """
    # Simulasi delay network
    await asyncio.sleep(1)

    html_content = f"""
    ==================================================
    [MOCK EMAIL SENT]
    To: {email_tujuan}
    Subject: Pemberitahuan Dokumen Baru: {jenis_dokumen.upper()}
    
    Halo {nama_siswa},
    
    Sekolah Anda baru saja mengunggah dokumen akademik baru ke dalam portal DokumenSekolah.
    Jenis Dokumen : {jenis_dokumen.upper()}
    
    Semua dokumen Anda telah dienkripsi secara aman dan hanya dapat dibuka oleh Anda 
    dengan login menggunakan NISN.
    
    Silakan kunjungi portal kami di http://localhost:3000/login untuk mengunduh dokumen Anda.
    
    Terima kasih,
    Admin DokumenSekolah
    ==================================================
    """
    
    logger.info(
        "📧 [EMAIL NOTIFICATION] Terkirim",
        email=email_tujuan,
        jenis=jenis_dokumen
    )
    # Print ke stdout agar terlihat jelas di log terminal docker
    print(html_content)
