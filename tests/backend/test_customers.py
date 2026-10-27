import pytest
from httpx import AsyncClient

_CUST = {"name": "Ravi Kumar", "address": "12 MG Road, Bengaluru", "pin": "560001", "contact_number": "9876543210"}


@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/customers/", json=_CUST, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Ravi Kumar"


@pytest.mark.asyncio
async def test_list_customers(client: AsyncClient, auth_headers: dict):
    await client.post("/customers/", json=_CUST, headers=auth_headers)
    resp = await client.get("/customers/", headers=auth_headers)
    assert resp.status_code == 200
    assert any(c["name"] == "Ravi Kumar" for c in resp.json())


@pytest.mark.asyncio
async def test_update_customer(client: AsyncClient, auth_headers: dict):
    create = await client.post("/customers/", json=_CUST, headers=auth_headers)
    cid = create.json()["id"]

    resp = await client.put(f"/customers/{cid}", json={"contact_number": "1111111111"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["contact_number"] == "1111111111"


@pytest.mark.asyncio
async def test_delete_customer(client: AsyncClient, auth_headers: dict):
    create = await client.post("/customers/", json=_CUST | {"name": "Delete Me"}, headers=auth_headers)
    cid = create.json()["id"]
    assert (await client.delete(f"/customers/{cid}", headers=auth_headers)).status_code == 204
    assert (await client.get(f"/customers/{cid}", headers=auth_headers)).status_code == 404
