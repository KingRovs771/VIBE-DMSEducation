import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.admin import Admin
from app.core.security import hash_password

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Admin).where(Admin.username == 'superadmin'))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = Admin(
                username='superadmin',
                email='superadmin@dms-sekolah.id',
                nama_lengkap='Super Administrator',
                password_hash=hash_password('Admin@DMS2024!'),
                role='super_admin',
                is_active=True,
                is_verified=True,
                failed_login_count=0,
                two_factor_enabled=False,
                two_factor_secret=None
            )
            db.add(admin)
        else:
            admin.password_hash = hash_password('Admin@DMS2024!')
            admin.is_active = True
            admin.two_factor_enabled = False
            admin.two_factor_secret = None
            admin.failed_login_count = 0
            admin.locked_until = None

        await db.commit()
        print("SEED SUCCESS: superadmin account created/updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
