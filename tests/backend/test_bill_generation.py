from datetime import date
import pytest
from httpx import AsyncClient


async def _full_seed(client: AsyncClient, headers: dict) -> tuple[int, int]:
    pub = (await client.post("/publications/", json={"name": "Daily", "frequency": "daily", "base_price": 5.0, "purchase_price": 3.0}, headers=headers)).json()
    cust = (await client.post("/customers/", json={"name": "Subscriber", "address": "2 Park Rd", "pin": "400001", "contact_number": "9999999999"}, headers=headers)).json()
    await client.post("/purchase-orders/", json={"purchase_date": "2024-01-01", "customer_id": cust["id"], "publication_id": pub["id"]}, headers=headers)
    return cust["id"], pub["id"]


@pytest.mark.asyncio
async def test_generate_bills_creates_items_and_bill(client: AsyncClient, auth_headers: dict):
    cid, _ = await _full_seed(client, auth_headers)

    resp = await client.post("/bills/generate", json={"start_date": "2024-01-01", "end_date": "2024-01-31"}, headers=auth_headers)
    assert resp.status_code == 200
    result = resp.json()
    assert result["bill_items_created"] >= 1
    assert result["bills_created"] >= 1

    items = (await client.get("/bill-items/", headers=auth_headers)).json()
    assert any(i["customer_id"] == cid for i in items)
    assert any(i["quantity"] == 31 for i in items)  # 31 days in January

    bills = (await client.get("/bills/", headers=auth_headers)).json()
    assert any(b["customer_id"] == cid for b in bills)


@pytest.mark.asyncio
async def test_generate_bills_idempotent(client: AsyncClient, auth_headers: dict):
    await _full_seed(client, auth_headers)
    payload = {"start_date": "2024-02-01", "end_date": "2024-02-29"}

    r1 = (await client.post("/bills/generate", json=payload, headers=auth_headers)).json()
    r2 = (await client.post("/bills/generate", json=payload, headers=auth_headers)).json()

    # Second run must update, not create duplicates
    assert r2["bill_items_created"] == 0
    assert r2["bill_items_updated"] >= 1


@pytest.mark.asyncio
async def test_generate_bills_specific_customer(client: AsyncClient, auth_headers: dict):
    cid, _ = await _full_seed(client, auth_headers)

    resp = await client.post("/bills/generate", json={"start_date": "2024-03-01", "end_date": "2024-03-31", "customer_id": cid}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["bills_created"] >= 1
