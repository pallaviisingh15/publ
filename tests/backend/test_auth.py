import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import hash_password
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    db_session.add(User(name="Tester", username="tester", password_hash=hash_password("pass"), is_active=True))
    await db_session.commit()

    resp = await client.post("/auth/login", data={"username": "tester", "password": "pass"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    db_session.add(User(name="T2", username="t2", password_hash=hash_password("correct"), is_active=True))
    await db_session.commit()

    resp = await client.post("/auth/login", data={"username": "t2", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient):
    resp = await client.post("/auth/login", data={"username": "nobody", "password": "x"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_no_token(client: AsyncClient):
    resp = await client.get("/users/")
    assert resp.status_code == 401
