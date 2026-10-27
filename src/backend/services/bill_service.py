import calendar
from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models.bill import Bill
from backend.db.models.bill_item import BillItem
from backend.db.models.purchase_order import PurchaseOrder
from backend.db.models.publication import FrequencyEnum
from backend.schemas.bill import GenerateBillsRequest, GenerateBillsResult


def _months_in_range(start: date, end: date) -> list[date]:
    months = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        months.append(date(year, month, 1))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def _count_deliveries(frequency: FrequencyEnum, period_start: date, period_end: date) -> int:
    days = (period_end - period_start).days + 1
    if frequency == FrequencyEnum.DAILY:
        return days
    if frequency == FrequencyEnum.WEEKLY:
        return max(days // 7, 1)
    if frequency == FrequencyEnum.MONTHLY:
        return 1
    if frequency == FrequencyEnum.QUARTERLY:
        return 1 if period_start.month in (1, 4, 7, 10) else 0
    if frequency == FrequencyEnum.BI_ANNUAL:
        return 1 if period_start.month in (1, 7) else 0
    if frequency == FrequencyEnum.ANNUAL:
        return 1 if period_start.month == 1 else 0
    return 0


def _dedup_subscriptions(
    subscriptions: list[PurchaseOrder],
) -> dict[tuple[int, int], PurchaseOrder]:
    """
    One bill item per (customer, publication) per month.
    When a customer has multiple purchase orders for the same publication
    (e.g. a renewed subscription), use the most recent one.
    """
    best: dict[tuple[int, int], PurchaseOrder] = {}
    for sub in subscriptions:
        key = (sub.customer_id, sub.publication_id)
        if key not in best or sub.purchase_date > best[key].purchase_date:
            best[key] = sub
    return best


async def _upsert_bill_item(
    db: AsyncSession,
    sub: PurchaseOrder,
    month_start: date,
    qty: int,
    amount: Decimal,
) -> bool:
    """Returns True if created, False if updated."""
    result = await db.execute(
        select(BillItem).where(
            BillItem.customer_id == sub.customer_id,
            BillItem.publication_id == sub.publication_id,
            BillItem.bill_date == month_start,
        )
    )
    # Use .first() — safe even if stale duplicates exist in the DB
    item = result.scalars().first()
    if item:
        item.price    = sub.sale_price
        item.quantity = qty
        item.discount = sub.discount
        item.amount   = amount
        return False
    db.add(BillItem(
        customer_id=sub.customer_id,
        publication_id=sub.publication_id,
        bill_date=month_start,
        price=sub.sale_price,
        quantity=qty,
        discount=sub.discount,
        amount=amount,
    ))
    return True


async def _upsert_bill(
    db: AsyncSession,
    customer_id: int,
    month_start: date,
    total: Decimal,
) -> bool:
    """Returns True if created, False if updated."""
    result = await db.execute(
        select(Bill).where(
            Bill.customer_id == customer_id,
            Bill.month == month_start,
        )
    )
    bill = result.scalars().first()
    if bill:
        bill.total_amount = total
        return False
    db.add(Bill(customer_id=customer_id, month=month_start, total_amount=total))
    return True


async def list_bill_items(
    db: AsyncSession, customer_id: int | None = None, month: date | None = None
) -> list[BillItem]:
    query = select(BillItem).options(
        selectinload(BillItem.customer),
        selectinload(BillItem.publication),
    )
    if customer_id:
        query = query.where(BillItem.customer_id == customer_id)
    if month:
        query = query.where(BillItem.bill_date == month)
    result = await db.execute(query.order_by(BillItem.bill_date.desc()))
    return list(result.scalars().all())


async def list_bills(
    db: AsyncSession, customer_id: int | None = None
) -> list[Bill]:
    query = select(Bill).options(selectinload(Bill.customer))
    if customer_id:
        query = query.where(Bill.customer_id == customer_id)
    result = await db.execute(query.order_by(Bill.month.desc()))
    return list(result.scalars().all())


async def _process_month(
    db: AsyncSession,
    month_start: date,
    subscriptions: list[PurchaseOrder],
    req: GenerateBillsRequest,
) -> tuple[int, int, int, int]:
    """Process one billing month. Returns (items_created, items_updated, bills_created, bills_updated)."""
    month_end = date(
        month_start.year,
        month_start.month,
        calendar.monthrange(month_start.year, month_start.month)[1],
    )
    unique_subs = _dedup_subscriptions(subscriptions)
    customer_totals: dict[int, Decimal] = defaultdict(Decimal)
    items_created = items_updated = 0

    for sub in unique_subs.values():
        if max(sub.purchase_date, month_start, req.start_date) > min(month_end, req.end_date):
            continue
        qty = _count_deliveries(sub.publication.frequency, month_start, month_end)
        if qty <= 0:
            continue
        amount = Decimal(str(sub.sale_price)) * qty * (
            1 - Decimal(str(sub.discount)) / 100
        )
        created = await _upsert_bill_item(db, sub, month_start, qty, amount)
        items_created += int(created)
        items_updated += int(not created)
        customer_totals[sub.customer_id] += amount

    bills_created = bills_updated = 0
    for cust_id, total in customer_totals.items():
        created = await _upsert_bill(db, cust_id, month_start, total)
        bills_created += int(created)
        bills_updated += int(not created)

    return items_created, items_updated, bills_created, bills_updated


async def generate_bills(db: AsyncSession, req: GenerateBillsRequest) -> GenerateBillsResult:
    query = (
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.publication))
        .where(PurchaseOrder.purchase_date <= req.end_date)
    )
    if req.customer_id:
        query = query.where(PurchaseOrder.customer_id == req.customer_id)

    result = await db.execute(query)
    subscriptions = list(result.scalars().all())

    ic = iu = bc = bu = 0
    for month_start in _months_in_range(req.start_date, req.end_date):
        mic, miu, mbc, mbu = await _process_month(db, month_start, subscriptions, req)
        ic += mic; iu += miu; bc += mbc; bu += mbu

    await db.commit()
    return GenerateBillsResult(
        bill_items_created=ic,
        bill_items_updated=iu,
        bills_created=bc,
        bills_updated=bu,
    )
