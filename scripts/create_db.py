"""Creates the PostgreSQL database if it does not exist. Run once before migrations."""
import asyncio
import sys

import asyncpg

from backend.core.config import settings


async def create_db() -> None:
    url = settings.database_url.replace("+asyncpg", "")
    db_name = url.rsplit("/", 1)[-1]
    server_url = url.rsplit("/", 1)[0]

    conn = await asyncpg.connect(f"{server_url}/postgres")
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", db_name
    )
    if not exists:
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Created database: {db_name}")
    else:
        print(f"Database already exists: {db_name}")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(create_db())
