from fastapi import APIRouter, Query
from backend.core.deps import CurrentUser, DbSession
from backend.schemas.bill import BillResponse, GenerateBillsRequest, GenerateBillsResult
from backend.services.bill_service import generate_bills, list_bills

router = APIRouter()


@router.get("/", response_model=list[BillResponse])
async def get_bills(
    db: DbSession,
    _: CurrentUser,
    customer_id: int | None = Query(default=None),
):
    return await list_bills(db, customer_id=customer_id)


@router.post("/generate", response_model=GenerateBillsResult)
async def run_generate_bills(req: GenerateBillsRequest, db: DbSession, _: CurrentUser):
    return await generate_bills(db, req)
