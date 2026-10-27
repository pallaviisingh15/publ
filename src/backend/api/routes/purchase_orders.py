from fastapi import APIRouter
from backend.core.deps import CurrentUser, DbSession
from backend.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse
from backend.services import purchase_order_service

router = APIRouter()


@router.get("/", response_model=list[PurchaseOrderResponse])
async def list_purchase_orders(db: DbSession, _: CurrentUser):
    return await purchase_order_service.list_purchase_orders(db)


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(order_id: int, db: DbSession, _: CurrentUser):
    return await purchase_order_service.get_purchase_order(db, order_id)


@router.post("/", response_model=PurchaseOrderResponse, status_code=201)
async def create_purchase_order(data: PurchaseOrderCreate, db: DbSession, _: CurrentUser):
    return await purchase_order_service.create_purchase_order(db, data)


@router.put("/{order_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(order_id: int, data: PurchaseOrderUpdate, db: DbSession, _: CurrentUser):
    return await purchase_order_service.update_purchase_order(db, order_id, data)


@router.delete("/{order_id}", status_code=204)
async def delete_purchase_order(order_id: int, db: DbSession, _: CurrentUser):
    await purchase_order_service.delete_purchase_order(db, order_id)
