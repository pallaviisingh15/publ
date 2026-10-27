"""
Create all database tables and seed an admin user if the users table is empty.
Run once before first launch: python scripts/init_db.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.core.config import settings
from backend.core.security import hash_password
from backend.db.models import Base, User


async def create_database_if_missing() -> None:
    """Create the PostgreSQL database itself if it doesn't exist."""
    # Connect to postgres maintenance DB to check/create target DB
    parts = settings.database_url.rsplit("/", 1)
    db_name = parts[-1]
    server_url = parts[0].replace("+asyncpg", "") + "/postgres"

    try:
        import asyncpg
        conn = await asyncpg.connect(server_url.replace("postgresql://", "postgresql://"))
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"  Created database: {db_name}")
        else:
            print(f"  Database '{db_name}' already exists.")
        await conn.close()
    except Exception as e:
        print(f"  Warning: could not auto-create DB ({e}). Ensure '{db_name}' exists.")


async def remove_duplicate_bill_rows(conn) -> None:
    """
    Remove duplicate bill_items / bills that existed before the UniqueConstraints
    were added.  Keeps the row with the lowest id in each duplicate group.
    Safe to run on a fresh DB (no rows → no-op).
    """
    await conn.execute(text("""
        DELETE FROM bill_items
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM bill_items
            GROUP BY customer_id, publication_id, bill_date
        )
    """))
    await conn.execute(text("""
        DELETE FROM bills
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM bills
            GROUP BY customer_id, month
        )
    """))


async def init() -> None:
    print("=== Newspaper Distribution System — DB Init ===")

    await create_database_if_missing()

    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        # Create tables first — safe to re-run, no-op if they already exist
        await conn.run_sync(Base.metadata.create_all)
        print("  All tables created / verified.")

        # Now clean up duplicates, in its own sub-transaction so a failure
        # here can't poison the rest of the connection
        try:
            async with conn.begin_nested():
                await remove_duplicate_bill_rows(conn)
            print("  Duplicate bill rows removed (if any).")
        except Exception as e:
            print("Duplicate cleanup skipped:", e)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalars().first() is None:
            admin = User(
                name="Administrator",
                username="admin",
                password_hash=hash_password("admin123"),
                is_active=True,
            )
            db.add(admin)
            await db.commit()
            print("  Seeded default admin user  (username: admin / password: admin123)")
            print("  IMPORTANT: Change the admin password after first login.")
        else:
            print("  Users table already populated — skipping seed.")

    await engine.dispose()
    print("=== Init complete ===")


if __name__ == "__main__":
    asyncio.run(init())
