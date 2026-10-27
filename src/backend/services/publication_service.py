from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.publication import Publication
from backend.schemas.publication import PublicationCreate, PublicationUpdate


async def list_publications(db: AsyncSession):
    result = await db.execute(select(Publication).order_by(Publication.id))
    return result.scalars().all()


async def get_publication(db: AsyncSession, pub_id: int) -> Publication:
    result = await db.execute(select(Publication).where(Publication.id == pub_id))
    pub = result.scalar_one_or_none()
    if pub is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    return pub


async def create_publication(db: AsyncSession, data: PublicationCreate) -> Publication:
    pub = Publication(
        name=data.name,
        frequency=data.frequency,
        base_price=data.base_price,
        purchase_price=data.purchase_price,
    )
    db.add(pub)
    await db.commit()
    await db.refresh(pub)
    return pub


async def update_publication(db: AsyncSession, pub_id: int, data: PublicationUpdate) -> Publication:
    pub = await get_publication(db, pub_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(pub, field, value)
    await db.commit()
    await db.refresh(pub)
    return pub


async def delete_publication(db: AsyncSession, pub_id: int) -> None:
    pub = await get_publication(db, pub_id)
    await db.delete(pub)
    await db.commit()
