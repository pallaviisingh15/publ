from datetime import date
import pytest
from httpx import AsyncClient


async def _seed(client: AsyncClient, headers: dict) -> tuple[int, int]:
    pub = (await client.post("/publications/", json={"name": "Weekly", "frequency": "weekly", "base_price": 10.0, "purchase_price": 7.0}, headers=headers)).json()
    cust = (await client.post("/customers/", json={"name": "Test Sub", "address": "1 Lane", "pin": "123456", "contact_number": "0000000000"}, headers=headers)).json()
    return cust["id"], pub["id"]


@pytest.mark.asyncio
async def test_create_order_defaults_sale_price(client: AsyncClient, auth_headers: dict):
    cid, pid = await _seed(client, auth_headers)
    resp = await client.post("/purchase-orders/", json={"purchase_date": str(date.today()), "customer_id": cid, "publication_id": pid}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["sale_price"] == 10.0  # defaulted to base_price
    assert data["discount"] == 0.0


@pytest.mark.asyncio
async def test_create_order_custom_price(client: AsyncClient, auth_headers: dict):
    cid, pid = await _seed(client, auth_headers)
    resp = await client.post("/purchase-orders/", json={"purchase_date": str(date.today()), "customer_id": cid, "publication_id": pid, "sale_price": 8.5, "discount": 5.0}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["sale_price"] == 8.5
    assert resp.json()["discount"] == 5.0


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient, auth_headers: dict):
    cid, pid = await _seed(client, auth_headers)
    await client.post("/purchase-orders/", json={"purchase_date": str(date.today()), "customer_id": cid, "publication_id": pid}, headers=auth_headers)
    resp = await client.get("/purchase-orders/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
