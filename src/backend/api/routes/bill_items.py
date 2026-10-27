from datetime import date
from fastapi import APIRouter, Query
from backend.core.deps import CurrentUser, DbSession
from backend.schemas.bill_item import BillItemResponse
from backend.services.bill_service import list_bill_items

router = APIRouter()


@router.get("/", response_model=list[BillItemResponse])
async def get_bill_items(
    db: DbSession,
    _: CurrentUser,
    customer_id: int | None = Query(default=None),
    month: date | None = Query(default=None),
):
    return await list_bill_items(db, customer_id=customer_id, month=month)
