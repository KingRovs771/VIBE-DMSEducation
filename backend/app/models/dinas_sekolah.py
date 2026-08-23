from sqlalchemy import Table, Column, Integer, ForeignKey
from app.core.database import Base

dinas_sekolah_binaan = Table(
    "dinas_sekolah_binaan",
    Base.metadata,
    Column("dinas_id", Integer, ForeignKey("admin.id", ondelete="CASCADE"), primary_key=True),
    Column("sekolah_id", Integer, ForeignKey("sekolah.id", ondelete="CASCADE"), primary_key=True),
)
