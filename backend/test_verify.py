import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Override host to localhost for docker exec if needed or use container URL
db_url = "postgresql+asyncpg://dms_user:your-strong-db-password@postgres:5432/dms_sekolah"
engine = create_async_engine(db_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

from app.models.admin import Admin
from app.core.security import verify_password

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Admin).where(Admin.username == 'superadmin'))
        admin = res.scalar_one_or_none()
        if admin:
            print("USER:", admin.username)
            print("HASH:", admin.password_hash)
            print("VERIFY Admin@DMS2024!:", verify_password('Admin@DMS2024!', admin.password_hash))
        else:
            print("ERROR: superadmin not found")

if __name__ == "__main__":
    asyncio.run(main())
