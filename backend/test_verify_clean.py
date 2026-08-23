import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.admin import Admin
from app.core.security import verify_password

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Admin).where(Admin.username == 'superadmin'))
        admin = res.scalar_one_or_none()
        if admin:
            print("USER:", admin.username)
            print("IS_ACTIVE:", admin.is_active)
            print("2FA_ENABLED:", admin.two_factor_enabled)
            print("VERIFY Admin@DMS2024!:", verify_password('Admin@DMS2024!', admin.password_hash))
        else:
            print("ERROR: superadmin not found")

if __name__ == "__main__":
    asyncio.run(main())
