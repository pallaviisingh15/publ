from fastapi import APIRouter
from backend.core.deps import CurrentUser, DbSession
from backend.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from backend.services import customer_service

router = APIRouter()


@router.get("/", response_model=list[CustomerResponse])
async def list_customers(db: DbSession, _: CurrentUser):
    return await customer_service.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: DbSession, _: CurrentUser):
    return await customer_service.get_customer(db, customer_id)


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: DbSession, _: CurrentUser):
    return await customer_service.create_customer(db, data)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, data: CustomerUpdate, db: DbSession, _: CurrentUser):
    return await customer_service.update_customer(db, customer_id, data)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: DbSession, _: CurrentUser):
    await customer_service.delete_customer(db, customer_id)
