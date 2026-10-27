import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_users(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/users/",
        json={"name": "Alice", "username": "alice", "password": "alice123"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "alice"
    assert "password" not in data

    resp = await client.get("/users/", headers=auth_headers)
    assert resp.status_code == 200
    names = [u["username"] for u in resp.json()]
    assert "alice" in names


@pytest.mark.asyncio
async def test_duplicate_username(client: AsyncClient, auth_headers: dict):
    await client.post("/users/", json={"name": "Bob", "username": "bob", "password": "x"}, headers=auth_headers)
    resp = await client.post("/users/", json={"name": "Bob2", "username": "bob", "password": "y"}, headers=auth_headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, auth_headers: dict):
    create = await client.post("/users/", json={"name": "Carol", "username": "carol", "password": "p"}, headers=auth_headers)
    uid = create.json()["id"]

    resp = await client.put(f"/users/{uid}", json={"name": "Carol Updated"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Carol Updated"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, auth_headers: dict):
    create = await client.post("/users/", json={"name": "Del", "username": "deluser", "password": "p"}, headers=auth_headers)
    uid = create.json()["id"]

    resp = await client.delete(f"/users/{uid}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/users/{uid}", headers=auth_headers)
    assert resp.status_code == 404
