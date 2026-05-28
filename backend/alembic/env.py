"""
Alembic env.py — Async SQLAlchemy support
==========================================
Mendukung dua mode:
  1. offline  — generate SQL script tanpa koneksi DB
  2. online   — jalankan migrasi langsung ke DB (async)
"""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Import semua model agar Alembic bisa autogenerate ─────────────────────────
# WAJIB: semua model harus diimport sebelum `target_metadata`
from app.core.database import Base  # noqa: F401
import app.models  # noqa: F401 — triggers semua import di __init__.py

# ── Alembic Config ─────────────────────────────────────────────────────────────
config = context.config

# Setup logging dari alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata untuk autogenerate
target_metadata = Base.metadata

# ── Override URL dari environment variable ─────────────────────────────────────
def get_url() -> str:
    """
    Ambil DATABASE_URL dari environment.
    Fallback ke alembic.ini jika tidak ada env var.
    Priority:
        1. DATABASE_URL env var (asyncpg driver untuk async engine)
        2. DATABASE_URL_SYNC env var (psycopg2 driver untuk offline mode)
        3. sqlalchemy.url dari alembic.ini
    """
    # Untuk async engine gunakan asyncpg
    url = os.getenv("DATABASE_URL", "")
    if url:
        return url

    # Fallback ke alembic.ini
    return config.get_main_option("sqlalchemy.url", "")


def get_sync_url() -> str:
    """URL sinkron untuk offline/run_migrations_offline."""
    url = get_url()
    # Ganti asyncpg → psycopg2 untuk offline mode
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


# ── Offline Mode ───────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """
    Mode offline: generate SQL script tanpa koneksi ke database.
    Berguna untuk review sebelum apply ke production.

    Cara pakai:
        alembic upgrade head --sql > migration.sql
    """
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Render perubahan tipe kolom
        compare_type=True,
        # Render perubahan server default
        compare_server_default=True,
        # Include schema yang ditulis di model
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online Mode (Async) ────────────────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    """Jalankan migrasi dengan koneksi yang sudah ada."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        # Render DROP INDEX juga
        render_as_batch=False,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Buat async engine dan jalankan migrasi."""
    # Konfigurasi async engine
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Gunakan NullPool untuk migrasi (no persistent connections)
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entrypoint untuk mode online — jalankan event loop asyncio."""
    asyncio.run(run_async_migrations())


# ── Dispatch ───────────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
