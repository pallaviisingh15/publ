import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.core.security import hash_password
from backend.db.models import Base, User
from backend.db.session import get_db
from backend.main import app

# SQLite in-memory DB for tests (no PostgreSQL required)
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# Test-only credential — not used in production
_TEST_ADMIN_SECRET = "test-admin-pass"  # noqa: S105


# Function-scoped engine so every test starts with a clean, empty database
@pytest_asyncio.fixture()
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture()
async def db_session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def admin_token(client: AsyncClient, db_session: AsyncSession):
    admin = User(
        name="Admin",
        username="admin",
        password_hash=hash_password(_TEST_ADMIN_SECRET),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    resp = await client.post(
        "/auth/login",
        data={"username": "admin", "password": _TEST_ADMIN_SECRET},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
