from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models.purchase_order import PurchaseOrder
from backend.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderUpdate
from backend.services.publication_service import get_publication


async def list_purchase_orders(db: AsyncSession) -> list[PurchaseOrder]:
    result = await db.execute(
        select(PurchaseOrder)
        .options(
            selectinload(PurchaseOrder.customer),
            selectinload(PurchaseOrder.publication),
        )
       .order_by(PurchaseOrder.id)
    )
    return list(result.scalars().all())


async def get_purchase_order(db: AsyncSession, order_id: int) -> PurchaseOrder:
    result = await db.execute(
        select(PurchaseOrder)
        .options(
            selectinload(PurchaseOrder.customer),
            selectinload(PurchaseOrder.publication),
        )
        .where(PurchaseOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    return order


async def create_purchase_order(db: AsyncSession, data: PurchaseOrderCreate) -> PurchaseOrder:
    # Default sale_price to publication's base_price
    sale_price = data.sale_price
    if sale_price is None:
        pub = await get_publication(db, data.publication_id)
        sale_price = float(pub.base_price)

    order = PurchaseOrder(
        purchase_date=data.purchase_date,
        customer_id=data.customer_id,
        publication_id=data.publication_id,
        sale_price=sale_price,
        discount=data.discount,
    )
    db.add(order)
    await db.commit()
    return await get_purchase_order(db, order.id)


async def update_purchase_order(
    db: AsyncSession, order_id: int, data: PurchaseOrderUpdate
) -> PurchaseOrder:
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(order, field, value)
    await db.commit()
    return await get_purchase_order(db, order_id)


async def delete_purchase_order(db: AsyncSession, order_id: int) -> None:
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    await db.delete(order)
    await db.commit()
