import pytest
from httpx import AsyncClient


_PUB = {"name": "Daily News", "frequency": "daily", "base_price": 5.00, "purchase_price": 3.50}


@pytest.mark.asyncio
async def test_create_publication(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/publications/", json=_PUB, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Daily News"
    assert data["frequency"] == "daily"
    assert data["base_price"] == 5.0


@pytest.mark.asyncio
async def test_list_publications(client: AsyncClient, auth_headers: dict):
    await client.post("/publications/", json=_PUB, headers=auth_headers)
    resp = await client.get("/publications/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_update_publication(client: AsyncClient, auth_headers: dict):
    create = await client.post("/publications/", json=_PUB, headers=auth_headers)
    pid = create.json()["id"]

    resp = await client.put(f"/publications/{pid}", json={"base_price": 6.00}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["base_price"] == 6.0


@pytest.mark.asyncio
async def test_delete_publication(client: AsyncClient, auth_headers: dict):
    create = await client.post("/publications/", json=_PUB, headers=auth_headers)
    pid = create.json()["id"]

    resp = await client.delete(f"/publications/{pid}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/publications/{pid}", headers=auth_headers)
    assert resp.status_code == 404
