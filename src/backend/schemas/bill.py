from datetime import date
from pydantic import BaseModel, ConfigDict
from backend.schemas.customer import CustomerResponse


class GenerateBillsRequest(BaseModel):
    start_date: date
    end_date: date
    customer_id: int | None = None  # None = all customers


class GenerateBillsResult(BaseModel):
    bill_items_created: int
    bill_items_updated: int
    bills_created: int
    bills_updated: int


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    month: date
    total_amount: float
    customer: CustomerResponse | None = None
