import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.admin import Admin
from app.core.security import hash_password, verify_password

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Admin).where(Admin.username == 'superadmin'))
        admin = res.scalar_one_or_none()
        if admin:
            admin.password_hash = hash_password('Admin@DMS2024!')
            admin.two_factor_enabled = False
            admin.two_factor_secret = None
            admin.failed_login_count = 0
            admin.locked_until = None
            admin.is_active = True
            await db.commit()
            print("SUCCESS: superadmin password set to 'Admin@DMS2024!' and 2FA disabled.")
            print("Verify check:", verify_password('Admin@DMS2024!', admin.password_hash))
        else:
            print("ERROR: superadmin not found")

if __name__ == "__main__":
    asyncio.run(main())
