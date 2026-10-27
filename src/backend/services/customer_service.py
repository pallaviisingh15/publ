from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.customer import Customer
from backend.schemas.customer import CustomerCreate, CustomerUpdate


async def list_customers(db: AsyncSession) -> list[Customer]:
    result = await db.execute(select(Customer).order_by(Customer.id))
    return list(result.scalars().all())


async def get_customer(db: AsyncSession, customer_id: int) -> Customer:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    cust = result.scalar_one_or_none()
    if cust is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return cust


async def create_customer(db: AsyncSession, data: CustomerCreate) -> Customer:
    cust = Customer(
        name=data.name,
        address=data.address,
        pin=data.pin,
        contact_number=data.contact_number,
    )
    db.add(cust)
    await db.commit()
    await db.refresh(cust)
    return cust


async def update_customer(db: AsyncSession, customer_id: int, data: CustomerUpdate) -> Customer:
    cust = await get_customer(db, customer_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(cust, field, value)
    await db.commit()
    await db.refresh(cust)
    return cust


async def delete_customer(db: AsyncSession, customer_id: int) -> None:
    cust = await get_customer(db, customer_id)
    await db.delete(cust)
    await db.commit()
